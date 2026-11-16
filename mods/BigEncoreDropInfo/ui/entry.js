/* Loaded by the shared BL4 UI Link; no BigEncore-specific PAK or native page replacement. */
(function(ns){
 'use strict';
 if(!ns||!ns.ext)return;
 const key='bigencore';
 if(ns.ext.teardowns[key])ns.ext.teardowns[key]();
 // A legacy integrated PAK has already installed its own hooks. Do not stack another copy.
 if(globalThis.__BigEncoreTravel_v1||window.BigEncoreDropInfoUI){
  if(ns.log)ns.log('盛大安可：检测到旧版 UI PAK。请退出游戏，移除 BigEncoreMapTeleport_UI_1000_P.pak 后重启。');
  return;
 }
 let alive=true;
 ns.ext.teardowns[key]=()=>{
  if(!alive)return;alive=false;
  if(globalThis.__BigEncoreTravel_v1)globalThis.__BigEncoreTravel_v1.teardown();
  if(window.BigEncoreDropInfoUI)window.BigEncoreDropInfoUI.teardown();
 };
 const base='coui://uiresources/bl4bigencore/';
 // Load each editable loose file through UILink, after the game's menu scripts are ready.
 ns.get(base+'encore.js',code=>{
  if(!alive||!code)return;
  new Function(code)();
  ns.get(base+'drops.js',drops=>{if(alive&&drops)new Function(drops)();});
 });
})((typeof bl4linkNs!=='undefined'&&bl4linkNs)||window.bl4ModMenu);
