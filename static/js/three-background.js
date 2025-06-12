// 海浪波动背景效果
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否有Three.js容器
    const container = document.getElementById('scene-container');
    if (!container) return;
    
    // 创建场景
    const scene = new THREE.Scene();
    
    // 创建相机
    const camera = new THREE.PerspectiveCamera(
        75, // 视野角度
        window.innerWidth / window.innerHeight, // 宽高比
        0.1, // 近裁剪面
        1000 // 远裁剪面
    );
    camera.position.z = 100;
    
    // 创建渲染器
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    // 创建海面几何体
    const geometry = new THREE.PlaneGeometry(300, 300, 50, 50);
    
    // 创建海面材质
    const material = new THREE.MeshStandardMaterial({
        color: 0x0088ff,
        wireframe: true,
        transparent: true,
        opacity: 0.3,
        emissive: 0x0066cc,
        metalness: 0.3,
        roughness: 0.8
    });
    
    // 创建海面网格
    const ocean = new THREE.Mesh(geometry, material);
    ocean.rotation.x = -Math.PI / 2;
    ocean.position.y = -50;
    scene.add(ocean);
    
    // 添加光源
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 50, 50);
    scene.add(directionalLight);
    
    // 浪花粒子
    const particleCount = 500;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const scales = new Float32Array(particleCount);
    
    for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        positions[i3] = (Math.random() * 2 - 1) * 150;
        positions[i3 + 1] = (Math.random() - 0.5) * 40;
        positions[i3 + 2] = (Math.random() * 2 - 1) * 150;
        scales[i] = Math.random() * 2 + 0.5;
    }
    
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));
    
    const particleMaterial = new THREE.PointsMaterial({
        color: 0x88ccff,
        size: 0.8,
        transparent: true,
        opacity: 0.6,
        sizeAttenuation: true
    });
    
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);
    
    // 窗口大小调整
    window.addEventListener('resize', function() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    
    // 动画循环
    let time = 0;
    function animate() {
        requestAnimationFrame(animate);
        
        time += 0.01;
        
        // 更新海面波浪
        const vertices = ocean.geometry.attributes.position.array;
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i];
            const z = vertices[i + 2];
            const distance = Math.sqrt(x * x + z * z);
            vertices[i + 1] = Math.sin(distance * 0.05 + time) * 5;
        }
        ocean.geometry.attributes.position.needsUpdate = true;
        
        // 更新粒子位置
        const particlePositions = particles.geometry.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            particlePositions[i3 + 1] = Math.sin(particlePositions[i3] * 0.01 + time) * 5 + 
                                        Math.cos(particlePositions[i3 + 2] * 0.01 + time) * 5 - 30;
        }
        particles.geometry.attributes.position.needsUpdate = true;
        
        // 旋转场景
        ocean.rotation.z = time * 0.1;
        
        renderer.render(scene, camera);
    }
    
    animate();
}); 