import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js";

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

const island = new THREE.Mesh(new THREE.CylinderGeometry(36, 42, 5, 56), new THREE.MeshStandardMaterial({color:0x4b7d4f,roughness:0.9}));
island.position.y = -2.6;
island.receiveShadow = true;
scene.add(island);
const water = new THREE.Mesh(new THREE.CylinderGeometry(100,100,0.15,96),new THREE.MeshStandardMaterial({color:0x164d78,metalness:0.15,roughness:0.25}));
water.position.y=-5.25;
scene.add(water);

const rng = (i) => { const v = Math.sin(i * 127.1 + 78.233) * 43758.5453; return v - Math.floor(v); };
const trunk = new THREE.CylinderGeometry(0.24,0.35,2.7,7);
const crown = new THREE.ConeGeometry(1.6,4.8,8);
for (let i=0;i<125;i++){
 const x=(rng(i+20)-0.5)*65,z=(rng(i+440)-0.5)*65;
 if(x*x+z*z>1030 || x*x+z*z<90)continue;
 const wood=new THREE.Mesh(trunk,new THREE.MeshStandardMaterial({color:0x6c5139}));wood.position.set(x,1.3,z);wood.castShadow=true;scene.add(wood);
 const top=new THREE.Mesh(crown,new THREE.MeshStandardMaterial({color:i%2?0x236742:0x2d8152}));top.position.set(x,4.7,z);top.castShadow=true;scene.add(top);
}
const people=new Map(), houses=new Map();
const personGeo=new THREE.CapsuleGeometry(0.42,1.05,4,8);
const personMat=new THREE.MeshStandardMaterial({color:0xffc77e});
const roofMat=new THREE.MeshStandardMaterial({color:0x8d443b});
const wallMat=new THREE.MeshStandardMaterial({color:0xd4ba8e});
let latest={residents:[]};
function synchronize(data){
 latest=data;
 for(const [id,el] of Object.entries({population:data.population,tick:data.tick,food:data.resources.food,wood:data.resources.wood})){document.getElementById(id).textContent=el;}
 document.getElementById("history").innerHTML=data.history.slice(-6).reverse().map(t=>`<div>• ${t.replaceAll("<","&lt;")}</div>`).join("") || "Первые жители исследуют остров...";
 const active=new Set(data.residents.map(p=>p.id));
 for(const [id,mesh] of people)if(!active.has(id)){scene.remove(mesh);people.delete(id);}
 for(const p of data.residents){
  if(!people.has(p.id)){const mesh=new THREE.Mesh(personGeo,personMat);mesh.castShadow=true;scene.add(mesh);people.set(p.id,mesh);}
  const mesh=people.get(p.id);mesh.userData.target=new THREE.Vector3(p.x,1.1,p.z);
 }
 for(const h of data.buildings)if(!houses.has(h.id)){
  const group=new THREE.Group(),wall=new THREE.Mesh(new THREE.BoxGeometry(3,2.8,3),wallMat);
  wall.position.y=1.4;wall.castShadow=true;group.add(wall);
  const roof=new THREE.Mesh(new THREE.ConeGeometry(2.65,2,4),roofMat);
  roof.rotation.y=Math.PI/4;roof.position.y=3.55;roof.castShadow=true;group.add(roof);
  group.position.set(h.x,0,h.z);scene.add(group);houses.set(h.id,group);
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
