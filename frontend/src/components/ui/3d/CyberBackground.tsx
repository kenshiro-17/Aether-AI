import { useRef, useMemo, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import * as THREE from 'three'

// Cyber Grid Floor
function CyberGrid() {
  const gridRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (gridRef.current) {
      gridRef.current.position.z = (state.clock.elapsedTime * 0.5) % 4
    }
  })

  const lines = useMemo(() => {
    const linesArray = []
    const gridSize = 40
    const spacing = 2
    
    // Horizontal lines
    for (let i = -gridSize; i <= gridSize; i += spacing) {
      linesArray.push({
        points: [
          new THREE.Vector3(-gridSize, 0, i),
          new THREE.Vector3(gridSize, 0, i)
        ],
        color: i % 10 === 0 ? '#00fff2' : '#00fff2'
      })
    }
    
    // Vertical lines
    for (let i = -gridSize; i <= gridSize; i += spacing) {
      linesArray.push({
        points: [
          new THREE.Vector3(i, 0, -gridSize),
          new THREE.Vector3(i, 0, gridSize)
        ],
        color: i % 10 === 0 ? '#00fff2' : '#00fff2'
      })
    }
    
    return linesArray
  }, [])

  return (
    <group ref={gridRef} position={[0, -5, 0]} rotation={[-Math.PI / 6, 0, 0]}>
      {lines.map((line, i) => (
        <Line
          key={i}
          points={line.points}
          color={line.color}
          lineWidth={0.5}
          transparent
          opacity={0.08}
        />
      ))}
    </group>
  )
}

// Floating Data Particles - Disabled for performance/stability
// function DataParticles({ count = 800 }) {
//   const ref = useRef<THREE.Points>(null)
//   const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
// 
//   useEffect(() => {
//     const handleMouseMove = (e: MouseEvent) => {
//       setMousePos({
//         x: (e.clientX / window.innerWidth) * 2 - 1,
//         y: -(e.clientY / window.innerHeight) * 2 + 1
//       })
//     }
//     window.addEventListener('mousemove', handleMouseMove)
//     return () => window.removeEventListener('mousemove', handleMouseMove)
//   }, [])
// 
//   const [positions, velocities] = useMemo(() => {
//     const pos = new Float32Array(count * 3)
//     const vel = new Float32Array(count * 3)
//     
//     for (let i = 0; i < count; i++) {
//       const i3 = i * 3
//       pos[i3] = (Math.random() - 0.5) * 30
//       pos[i3 + 1] = (Math.random() - 0.5) * 30
//       pos[i3 + 2] = (Math.random() - 0.5) * 30
//       
//       vel[i3] = (Math.random() - 0.5) * 0.01
//       vel[i3 + 1] = (Math.random() - 0.5) * 0.01 + 0.005
//       vel[i3 + 2] = (Math.random() - 0.5) * 0.01
//     }
//     
//     return [pos, vel]
//   }, [count])
// 
//   useFrame((state) => {
//     if (!ref.current) return
//     
//     const positions = ref.current.geometry.attributes.position.array as Float32Array
//     
//     for (let i = 0; i < count; i++) {
//       const i3 = i * 3
//       
//       // Update positions
//       positions[i3] += velocities[i3] + mousePos.x * 0.0005
//       positions[i3 + 1] += velocities[i3 + 1]
//       positions[i3 + 2] += velocities[i3 + 2] + mousePos.y * 0.0005
//       
//       // Reset particles that go too far
//       if (positions[i3 + 1] > 15) {
//         positions[i3 + 1] = -15
//         positions[i3] = (Math.random() - 0.5) * 30
//         positions[i3 + 2] = (Math.random() - 0.5) * 30
//       }
//     }
//     
//     ref.current.geometry.attributes.position.needsUpdate = true
//     ref.current.rotation.y = state.clock.elapsedTime * 0.01
//   })
// 
//   return (
//     <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
//       <PointMaterial
//         transparent
//         color="#00fff2"
//         size={0.03}
//         sizeAttenuation={true}
//         depthWrite={false}
//         opacity={0.6}
//         blending={THREE.AdditiveBlending}
//       />
//     </Points>
//   )
// }

// Floating Hexagons
function FloatingHexagons({ count = 8 }) {
  const hexagons = useMemo(() => {
    return Array.from({ length: count }, () => ({
      position: [
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 15,
        (Math.random() - 0.5) * 10 - 5
      ] as [number, number, number],
      rotation: Math.random() * Math.PI,
      speed: 0.1 + Math.random() * 0.2,
      scale: 0.3 + Math.random() * 0.7,
      color: Math.random() > 0.5 ? '#00fff2' : '#ff00ff'
    }))
  }, [count])

  return (
    <group>
      {hexagons.map((hex, i) => (
        <FloatingHexagon key={i} {...hex} />
      ))}
    </group>
  )
}

function FloatingHexagon({ position, rotation, speed, scale, color }: {
  position: [number, number, number]
  rotation: number
  speed: number
  scale: number
  color: string
}) {
  const ref = useRef<THREE.Mesh>(null)
  const initialY = position[1]

  useFrame((state) => {
    if (!ref.current) return
    ref.current.rotation.z = state.clock.elapsedTime * speed
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * speed * 0.5) * 0.2
    ref.current.position.y = initialY + Math.sin(state.clock.elapsedTime * speed) * 0.3
  })

  const hexagonShape = useMemo(() => {
    const shape = new THREE.Shape()
    const sides = 6
    const radius = 1
    
    for (let i = 0; i <= sides; i++) {
      const angle = (i / sides) * Math.PI * 2 - Math.PI / 2
      const x = Math.cos(angle) * radius
      const y = Math.sin(angle) * radius
      
      if (i === 0) shape.moveTo(x, y)
      else shape.lineTo(x, y)
    }
    
    return shape
  }, [])

  return (
    <mesh ref={ref} position={position} rotation={[0, 0, rotation]} scale={scale}>
      <shapeGeometry args={[hexagonShape]} />
      <meshBasicMaterial color={color} transparent opacity={0.05} side={THREE.DoubleSide} />
      <lineSegments>
        <edgesGeometry args={[new THREE.ShapeGeometry(hexagonShape)]} />
        <lineBasicMaterial color={color} transparent opacity={0.2} />
      </lineSegments>
    </mesh>
  )
}

// Data Streams - Vertical lines of "code"
function DataStreams({ count = 15 }) {
  const streams = useMemo(() => {
    return Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 40,
      z: (Math.random() - 0.5) * 20 - 10,
      speed: 1 + Math.random() * 2,
      length: 3 + Math.random() * 8,
      delay: Math.random() * 5
    }))
  }, [count])

  return (
    <group>
      {streams.map((stream, i) => (
        <DataStream key={i} {...stream} />
      ))}
    </group>
  )
}

function DataStream({ x, z, speed, length, delay }: {
  x: number
  z: number
  speed: number
  length: number
  delay: number
}) {
  const ref = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (!ref.current) return
    const t = ((state.clock.elapsedTime + delay) * speed) % 30
    ref.current.position.y = 15 - t
    const material = ref.current.material as THREE.MeshBasicMaterial
    if (material) {
      material.opacity = Math.sin((t / 30) * Math.PI) * 0.2
    }
  })

  return (
    <mesh ref={ref} position={[x, 15, z]}>
      <boxGeometry args={[0.02, length, 0.02]} />
      <meshBasicMaterial color="#00fff2" transparent opacity={0.1} />
    </mesh>
  )
}

// Glowing Orbs
function GlowingOrbs({ count = 4 }) {
  const orbs = useMemo(() => {
    return Array.from({ length: count }, () => ({
      position: [
        (Math.random() - 0.5) * 25,
        (Math.random() - 0.5) * 15,
        -5 - Math.random() * 10
      ] as [number, number, number],
      color: ['#00fff2', '#ff00ff', '#9d00ff'][Math.floor(Math.random() * 3)],
      scale: 0.1 + Math.random() * 0.3,
      speed: 0.2 + Math.random() * 0.5
    }))
  }, [count])

  return (
    <group>
      {orbs.map((orb, i) => (
        <GlowingOrb key={i} {...orb} />
      ))}
    </group>
  )
}

function GlowingOrb({ position, color, scale, speed }: {
  position: [number, number, number]
  color: string
  scale: number
  speed: number
}) {
  const ref = useRef<THREE.Mesh>(null)
  const [initialPos] = useState(position)

  useFrame((state) => {
    if (!ref.current) return
    ref.current.position.x = initialPos[0] + Math.sin(state.clock.elapsedTime * speed) * 1.5
    ref.current.position.y = initialPos[1] + Math.cos(state.clock.elapsedTime * speed * 0.5) * 1
    ref.current.scale.setScalar(scale * (1 + Math.sin(state.clock.elapsedTime * 1) * 0.1))
  })

  return (
    <mesh ref={ref} position={position}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshBasicMaterial color={color} transparent opacity={0.3} />
    </mesh>
  )
}

// Camera Controller - responds to mouse
function CameraController() {
  const { camera } = useThree()
  const [mouse, setMouse] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMouse({
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: -(e.clientY / window.innerHeight) * 2 + 1
      })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useFrame(() => {
    camera.position.x += (mouse.x * 1 - camera.position.x) * 0.01
    camera.position.y += (mouse.y * 0.5 - camera.position.y) * 0.01
    camera.lookAt(0, 0, -5)
  })

  return null
}

// Main Background Component
export function CyberBackground() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 75 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <fog attach="fog" args={['#0a0a0a', 10, 50]} />
        <ambientLight intensity={0.5} />
        
        <CameraController />
        <CyberGrid />
        {/* <DataParticles count={800} /> */}
        <FloatingHexagons count={8} />
        <DataStreams count={15} />
        <GlowingOrbs count={4} />
      </Canvas>
    </div>
  )
}

export default CyberBackground
