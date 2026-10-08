import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.FogExp2(0x07111f, 0.010);
const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 700);
camera.position.set(56, 55, 64);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI / 2.03;
controls.target.set(0, 0, 0);
scene.add(new THREE.HemisphereLight(0xa7dbff, 0x43522f, 2.5));
const sun = new THREE.DirectionalLight(0xffedc0, 3.2);
sun.position.set(35, 75, 27);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = sun.shadow.camera.bottom = -75;
sun.shadow.camera.right = sun.shadow.camera.top = 75;
scene.add(sun);

const terrainGroup = new THREE.Group();
scene.add(terrainGroup);
const tileGeometry = new THREE.BoxGeometry(1, 1, 1);
const biomeMaterials = {
 water:new THREE.MeshStandardMaterial({color:0x195e88,roughness:0.28,metalness:0.12}),
 beach:new THREE.MeshStandardMaterial({color:0xdac18b,roughness:0.92}),
 grassland:new THREE.MeshStandardMaterial({color:0x539b60,roughness:0.98}),
 forest:new THREE.MeshStandardMaterial({color:0x226947,roughness:0.98}),
 highland:new THREE.MeshStandardMaterial({color:0x728477,roughness:1})
};
const ground = new THREE.Mesh(new THREE.PlaneGeometry(85,85),new THREE.MeshStandardMaterial({color:0x0c3c62}));
ground.rotation.x=-Math.PI/2; ground.position.y=-2.5; scene.add(ground);
let terrainReady=false;
function buildTerrain(terrain){
 if(terrainReady || !terrain?.tiles)return;
 terrainReady=true;
 const grid=terrain.tiles, half=Math.floor(terrain.size/2);
 const grouped={};
 for(let z=0;z<grid.length;z++)for(let x=0;x<grid[z].length;x++){
   const t=grid[z][x];
   (grouped[t.biome]??=[]).push({x:x-half,z:z-half,height:t.height});
 }
 for(const [biome,locations] of Object.entries(grouped)){
   const mesh=new THREE.InstancedMesh(tileGeometry,biomeMaterials[biome],locations.length);
   const matrix=new THREE.Matrix4();
   locations.forEach((v,i)=>{
     matrix.compose(new THREE.Vector3(v.x,v.height/2-0.4,v.z),new THREE.Quaternion(),new THREE.Vector3(1,v.height+1,1));
     mesh.setMatrixAt(i,matrix);
   });
   mesh.instanceMatrix.needsUpdate=true;
   mesh.receiveShadow=true;
   terrainGroup.add(mesh);
 }
}
const people=new Map(), houses=new Map(), farms=new Map(), cities=new Map();
const personGeo=new THREE.CapsuleGeometry(0.42,1.05,4,8);
const personMat=new THREE.MeshStandardMaterial({color:0xffc77e});
const roofMat=new THREE.MeshStandardMaterial({color:0x8d443b});
const wallMat=new THREE.MeshStandardMaterial({color:0xd4ba8e});

const routeMeshes=new Map(), caravanMeshes=new Map();
function refreshTransport(data){
 const routes=new Map();
 for(const route of data.roads||[]){
  const key=route.from+"-"+route.to;
  routes.set(key,route);
  if(routeMeshes.has(key))continue;
  const points=(route.waypoints||[]).map(p=>new THREE.Vector3(p.x,1.15,p.z));
  if(points.length<2)continue;
  const material=new THREE.LineBasicMaterial({color:route.mode==="sea"?0x61c9f4:route.mode==="bridge"?0xf4ce81:route.mode==="pass"?0xdb9f76:0xb9ad8b});
  const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),material);
  scene.add(line);routeMeshes.set(key,line);
 }
 for(const [key,mesh] of routeMeshes)if(!routes.has(key)){scene.remove(mesh);mesh.geometry.dispose();mesh.material.dispose();routeMeshes.delete(key);}
 const visible=new Set();
 (data.shipments||[]).forEach((cargo,index)=>{
  const key=[Math.min(cargo.from,cargo.to),Math.max(cargo.from,cargo.to)].join("-");
  const route=routes.get(key);
  if(!route||route.waypoints.length<2)return;
  const id=key+"-"+cargo.kind+"-"+index;
  visible.add(id);
  let group=caravanMeshes.get(id);
  if(!group){
   group=new THREE.Group();
   const ship=route.mode==="sea";
   const base=new THREE.Mesh(ship?new THREE.BoxGeometry(1.6,.5,.8):new THREE.BoxGeometry(1,.7,.65),new THREE.MeshStandardMaterial({color:ship?0x65cbe3:0xc28d4f}));
   base.position.y=.55;group.add(base);
   const load=new THREE.Mesh(new THREE.BoxGeometry(.65,.6,.5),new THREE.MeshStandardMaterial({color:0xe1b96f}));
   load.position.y=1.05;group.add(load);
   scene.add(group);caravanMeshes.set(id,group);
  }
  const start=route.waypoints[0],end=route.waypoints[route.waypoints.length-1];
  const reverse=cargo.from!==route.from;
  const distance=Math.max(1,Number(cargo.remaining_ticks)||10);
  const total=Math.max(10,Number(route.travel_ticks)||10);
  const t=Math.max(0,Math.min(1,1-distance/total));
  const fraction=reverse?1-t:t;
  const location=fraction*(route.waypoints.length-1);
  const left=Math.min(route.waypoints.length-2,Math.floor(location)),alpha=location-left;
  const one=route.waypoints[left],two=route.waypoints[left+1];
  group.position.set(one.x+(two.x-one.x)*alpha,.9,one.z+(two.z-one.z)*alpha);
  group.rotation.y=Math.atan2(two.x-one.x,two.z-one.z)+(reverse?Math.PI:0);
 });
 for(const [id,mesh] of caravanMeshes)if(!visible.has(id)){scene.remove(mesh);caravanMeshes.delete(id);}
}

let latest={residents:[]};
let frozen=false;
document.getElementById('pause').addEventListener('click',()=>{frozen=!frozen;document.getElementById('pause').textContent=frozen?'Продолжить':'Стоп-кадр';});
document.getElementById('observe').addEventListener('click',()=>{controls.target.set(0,0,0);camera.position.set(56,55,64);});
document.getElementById('focus').addEventListener('click',()=>{const city=latest.settlements?.[0];if(city){controls.target.set(city.x,0,city.z);camera.position.set(city.x+18,25,city.z+20);}});
function synchronize(data){
 if(frozen)return;
 latest=data;
 const states=document.getElementById('states');
 states.replaceChildren();
 for(const state of data.states||[]){const entry=document.createElement('div');entry.textContent=state.name+' · '+(state.government||'council')+' · казна '+Math.round(state.treasury||0);states.appendChild(entry);}
 buildTerrain(data.terrain);
 refreshTransport(data);
 for(const [id,el] of Object.entries({population:data.population,tick:data.tick,food:data.resources.food,wood:data.resources.wood})){document.getElementById(id).textContent=el;}
 document.getElementById("history").innerHTML=(data.chronicle||data.history).slice(-10).reverse().map(t=>`<div>• ${t.replaceAll("<","&lt;")}</div>`).join("") || "Первые жители исследуют остров...";
 const active=new Set(data.residents.map(p=>p.id));
 for(const [id,mesh] of people)if(!active.has(id)){scene.remove(mesh);people.delete(id);}
 for(const p of data.residents){
  if(!people.has(p.id)){const mesh=new THREE.Mesh(personGeo,personMat);mesh.castShadow=true;scene.add(mesh);people.set(p.id,mesh);}
  const mesh=people.get(p.id);mesh.userData.target=new THREE.Vector3(p.x,1.65,p.z);
 }
 for(const city of data.settlements||[])if(!cities.has(city.id)){
  const tower=new THREE.Group();
  const base=new THREE.Mesh(new THREE.CylinderGeometry(1.2,1.6,4,8),new THREE.MeshStandardMaterial({color:0x7993b8}));
  base.position.y=2.4;base.castShadow=true;tower.add(base);
  const top=new THREE.Mesh(new THREE.ConeGeometry(1.7,2.5,8),new THREE.MeshStandardMaterial({color:0x594f94}));
  top.position.y=5.7;tower.add(top);
  tower.position.set(city.x,0,city.z);scene.add(tower);cities.set(city.id,tower);
 }
 for(const farm of data.farms||[])if(!farms.has(farm.id)){
  const crop=new THREE.Mesh(new THREE.BoxGeometry(2.2,.28,2.2),new THREE.MeshStandardMaterial({color:0xd2a04f}));
  crop.position.set(farm.x,.95,farm.z);scene.add(crop);farms.set(farm.id,crop);
 }
 for(const h of data.buildings)if(!houses.has(h.id)){
  const group=new THREE.Group(),wall=new THREE.Mesh(new THREE.BoxGeometry(3,2.8,3),wallMat);
  wall.position.y=1.4;wall.castShadow=true;group.add(wall);
  const roof=new THREE.Mesh(new THREE.ConeGeometry(2.65,2,4),roofMat);
  roof.rotation.y=Math.PI/4;roof.position.y=3.55;roof.castShadow=true;group.add(roof);
  group.position.set(h.x,0.5,h.z);scene.add(group);houses.set(h.id,group);
 }
}
async function connect(){
 try{
  const response=await fetch("/api/world");if(response.ok)synchronize(await response.json());
 }catch(error){console.warn("Initial snapshot unavailable",error);}
 const protocol=location.protocol==="https:"?"wss":"ws";
 const ws=new WebSocket(`${protocol}://${location.host}/ws/world`);
 ws.onopen=()=>{document.getElementById("status").textContent="Мир развивается";};
 ws.onmessage=e=>synchronize(JSON.parse(e.data));
 ws.onclose=()=>{document.getElementById("status").textContent="Переподключение...";setTimeout(connect,3000);};
}
connect();
function animate(){
 requestAnimationFrame(animate);
 for(const mesh of people.values())if(mesh.userData.target)mesh.position.lerp(mesh.userData.target,0.045);
 controls.update();renderer.render(scene,camera);
}
animate();
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
