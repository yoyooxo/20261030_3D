"""Interactive 3D viewer: export the render scene to GLB with kicad-cli and embed it in a single HTML file
(three.js, orbit controls). Double-click 立體檢視.html to open in Chrome/Edge (needs internet for three.js).
usage: python gen_viewer.py   (after gen_scene.py, which writes _scene_render_only.kicad_pcb)"""
import base64, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KCLI = os.environ.get("KICAD_CLI", "kicad-cli")   # set KICAD_CLI to your kicad-cli path (KiCad 9+)
glb = os.path.join(HERE, "3d", "scene.glb")
subprocess.run([KCLI, "pcb", "export", "glb", "-f", "--include-tracks", "--include-pads", "--include-silkscreen",
                "--include-soldermask", "-o", glb, os.path.join(HERE, "_scene_render_only.kicad_pcb")], check=True)
b64 = base64.b64encode(open(glb, "rb").read()).decode()

html = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>讀卡座轉接板 3D</title>
<style>
 html,body{margin:0;height:100%;background:#2b2f3a;color:#eee;font-family:"Microsoft JhengHei",sans-serif;overflow:hidden}
 #ui{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.55);padding:10px 12px;border-radius:8px;font-size:14px;line-height:1.6}
 #ui button{margin:2px 4px 2px 0;padding:4px 10px;font-size:14px;border-radius:5px;border:1px solid #888;background:#444;color:#fff;cursor:pointer}
 #ui button:hover{background:#666}
 #msg{position:absolute;bottom:10px;left:10px;font-size:13px;opacity:.8}
</style>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
 "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
</head><body>
<div id="ui"><b>讀卡座轉接板 3D</b><br>
左鍵拖曳：旋轉　右鍵拖曳：平移　滾輪：縮放<br>
<button data-v="iso">斜視</button><button data-v="top">正上方</button><button data-v="bottom">正下方</button><button data-v="front">側面（插卡口）</button><button data-v="low">低角度</button><br>
<button id="spin">自動旋轉：關</button>
</div>
<div id="msg">載入中…</div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x2b2f3a);
scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(1, 2, 1.5); scene.add(sun);
const sun2 = new THREE.DirectionalLight(0xffffff, 0.6); sun2.position.set(-1, -1.5, -1); scene.add(sun2);
const camera = new THREE.PerspectiveCamera(40, innerWidth/innerHeight, 0.0001, 100);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const b64 = "__GLB__";
const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;
let center = new THREE.Vector3(), radius = 1, up = new THREE.Vector3(0,1,0);
new GLTFLoader().parse(bin, "", gltf => {
  const root = gltf.scene;
  scene.add(root);
  const box = new THREE.Box3().setFromObject(root);
  box.getCenter(center);
  radius = box.getSize(new THREE.Vector3()).length() / 2;
  controls.target.copy(center);
  view("iso");
  document.getElementById("msg").textContent = "麵包板、卡座、IC 卡為示意方塊；卡座外框與腳位、排針位置照規格書";
}, err => { document.getElementById("msg").textContent = "載入失敗：" + err; });

// KiCad GLB: board lies in the X-Z plane with +Y up (glTF convention)
function view(v){
  const d = radius * 2.2, c = center;
  const p = {iso:[0.55,0.75,0.9], top:[0,1,0.0001], bottom:[0,-1,0.0001], front:[0,0.12,1], low:[-0.6,0.18,0.8]}[v];
  const dir = new THREE.Vector3(...p).normalize().multiplyScalar(d);
  camera.position.copy(c).add(dir);
  camera.near = radius/100; camera.far = radius*50; camera.updateProjectionMatrix();
  controls.target.copy(c); controls.update();
}
document.querySelectorAll("button[data-v]").forEach(b => b.onclick = () => view(b.dataset.v));
const spin = document.getElementById("spin");
spin.onclick = () => { controls.autoRotate = !controls.autoRotate; spin.textContent = "自動旋轉：" + (controls.autoRotate ? "開" : "關"); };
addEventListener("resize", () => { camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
</script></body></html>
""".replace("__GLB__", b64)
open(os.path.join(HERE, "立體檢視.html"), "w", encoding="utf-8").write(html)
print("ok", len(html) // 1024, "KB")
