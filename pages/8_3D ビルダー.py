import streamlit as st
import streamlit.components.v1 as components

st.title("3D モデルビューアー")
st.write("マウスでドラッグ（回転）、ホイール（ズーム）、右クリックドラッグ（移動）ができます。")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #2c3e50; }
        canvas { display: block; }
        #loading { position: absolute; top: 10px; left: 10px; color: white; font-family: sans-serif; }
    </style>
</head>
<body>
    <div id="loading">モデル読み込み中...</div>

    <!-- importmapでThree.js本体と、追加機能(アドオン)の読み込み先を設定 -->
    <script type="importmap">
      {
        "imports": {
          "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
          "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }
      }
    </script>
    
    <script type="module">
        import * as THREE from 'three';
        // カメラ操作用のOrbitControlsを読み込み
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        // .glb / .gltf 読み込み用のGLTFLoaderを読み込み
        import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
        camera.position.set(5, 5, 5); // 初期カメラ位置を少し離す

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        // よりリアルな光の表現にする設定
        renderer.outputColorSpace = THREE.SRGBColorSpace; 
        document.body.appendChild(renderer.domElement);

        // ★ カメラ操作 (OrbitControls) の追加
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // 滑らかに動くようにする
        controls.dampingFactor = 0.05;

        // 照明の設定（3Dモデルがきれいに見えるように複数配置）
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 2.0);
        directionalLight.position.set(10, 10, 10);
        scene.add(directionalLight);

        // ★ フリーの3Dモデル (.glb) を読み込む
        const loader = new GLTFLoader();
        // 今回はテストとしてネット上のサンプルURLを直接指定
        const modelUrl = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb';
        
        loader.load(
            modelUrl,
            function (gltf) {
                // 読み込み成功時の処理
                const model = gltf.scene;
                // モデルが大きすぎたり小さすぎたりする場合に備えてサイズ調整（今回はそのまま）
                model.scale.set(1, 1, 1);
                // モデルを画面の中心付近に配置
                model.position.set(0, -1, 0); 
                scene.add(model);
                
                // ロード完了の文字を消す
                document.getElementById('loading').style.display = 'none';
            },
            undefined,
            function (error) {
                console.error('エラーが発生しました:', error);
                document.getElementById('loading').innerText = '読み込みエラー';
            }
        );

        // グリッドヘルパー（床の網目）を追加して空間を分かりやすくする
        const gridHelper = new THREE.GridHelper(10, 10);
        scene.add(gridHelper);

        // アニメーションループ
        function animate() {
            requestAnimationFrame(animate);
            controls.update(); // Damping(滑らかさ)を有効にするために必要
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=600)