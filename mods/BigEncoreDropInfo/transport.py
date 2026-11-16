# -*- coding: utf-8 -*-
"""Loopback presentation transport. Worker handles plain JSON only, never Unreal."""
import json
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread, Lock
from .catalog import load, processor_details
from .probe import destination
from . import encore_runtime
from .i18n import localize

PORT = 19386
PREFIX = '/big-encore-20261019-v1'
_server = None
_enabled = False
_catalog = {}
_lock = Lock()
_count = 0
_root = None


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(3.0)
        super().setup()

    def log_message(self, *args):
        pass

    def reply(self, code, data):
        body = json.dumps(localize(data), ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        encoding = self.headers.get('Accept-Encoding', '').lower()
        use_gzip = len(body) >= 1024 and any(
            part.strip().split(';', 1)[0] == 'gzip' and not any(
                option.strip() in ('q=0', 'q=0.0', 'q=0.00', 'q=0.000')
                for option in part.split(';')[1:])
            for part in encoding.split(','))
        if use_gzip:
            body = gzip.compress(body, compresslevel=5, mtime=0)
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Vary', 'Accept-Encoding')
        if use_gzip:
            self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == PREFIX + '/encore':
            return self.reply(200, encore_runtime.snapshot() if _enabled else {'status':'disabled','bosses':[]})
        if self.path != PREFIX + '/catalog':
            return self.reply(404, {})
        with _lock:
            data = {'enabled': _enabled, 'bosses': _catalog, 'version': '0.6.0-preview.18'}
        self.reply(200, data)

    def do_POST(self):
        global _count
        if self.path not in (PREFIX + '/trace', PREFIX + '/encore'):
            return self.reply(404, {})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 24000:
                return self.reply(413, {})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                return self.reply(400, {})
            if self.path == PREFIX + '/encore':
                queued = bool(_enabled and encore_runtime.enqueue(data))
                return self.reply(200, {'queued':queued})
            with _lock:
                if data.get('kind') == 'map_poi' and isinstance(data.get('data'), dict) and _root is not None:
                    # One bounded snapshot overwritten on selection changes; no UObject access.
                    (_root / 'latest-map-poi.json').write_text(
                        json.dumps({'version': '0.5.7', 'selection': data['data']}, ensure_ascii=False, indent=2),
                        encoding='utf-8')
                if _count < 100 and _root is not None:
                    _count += 1
                    with (_root / 'ui-events.jsonl').open('a', encoding='utf-8') as out:
                        out.write(json.dumps(data, ensure_ascii=False) + '\n')
            return self.reply(200, {})
        except (ValueError, OSError):
            return self.reply(400, {})


def start():
    global _server, _catalog, _enabled, _root
    # Called on SDK mod lifecycle; only Python files/network state are touched.
    _root = destination(); _root.mkdir(parents=True, exist_ok=True)
    catalog = {key: {'name': row['name'], 'map_names': row['map_names'],
                     'world_keys': row['world_keys'], 'note': row.get('note', ''), 'note_before': row.get('note_before', False),
                     'station_ids': row['station_ids'],
                     'drops': [{field: d[field] for field in
                                ('name', 'kind', 'kind_label', 'rarity')} for d in row['drops']]}
               for key, row in load().items()}
    catalog['activity_processor']=processor_details(load())
    if _server is None:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
        server.daemon_threads = True
        server.timeout = 1
        _server = server
        Thread(target=server.serve_forever, name='BigEncoreDropInfo-JSON', daemon=True).start()
    with _lock:
        _catalog = catalog
        _enabled = True


def stop():
    global _enabled
    # Keep the daemon serving disabled state so later UI events clear their label.
    with _lock:
        _enabled = False
