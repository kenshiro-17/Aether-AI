import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface GlitchTextProps {
  text: string
  className?: string
}

export function GlitchText({ text, className = '' }: GlitchTextProps) {
  const [isGlitching, setIsGlitching] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setIsGlitching(true)
      setTimeout(() => setIsGlitching(false), 200)
    }, 3000 + Math.random() * 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`relative ${className}`}>
      <span className="relative z-10">{text}</span>
      
      {isGlitching && (
        <>
          <motion.span
            initial={{ x: -2, opacity: 0 }}
            animate={{ x: [-2, 2, -1, 1, 0], opacity: [0.8, 0.6, 0.8, 0.4, 0] }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 text-[#00fff2] z-0"
            style={{ clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)' }}
          >
            {text}
          </motion.span>
          <motion.span
            initial={{ x: 2, opacity: 0 }}
            animate={{ x: [2, -2, 1, -1, 0], opacity: [0.8, 0.6, 0.8, 0.4, 0] }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 text-[#ff00ff] z-0"
            style={{ clipPath: 'polygon(0 55%, 100% 55%, 100% 100%, 0 100%)' }}
          >
            {text}
          </motion.span>
        </>
      )}
    </div>
  )
}

// Interactive Terminal Cursor
export function TerminalCursor() {
  return (
    <motion.span
      animate={{ opacity: [1, 0] }}
      transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse' }}
      className="inline-block w-3 h-5 bg-[#00fff2] ml-1 shadow-[0_0_10px_#00fff2]"
    />
  )
}

// Typing Effect
export function TypeWriter({ text, speed = 50, onComplete }: { 
  text: string
  speed?: number
  onComplete?: () => void 
}) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)

      return () => clearTimeout(timeout)
    } else if (onComplete) {
      onComplete()
    }
  }, [currentIndex, text, speed, onComplete])

  return (
    <span>
      {displayedText}
      <TerminalCursor />
    </span>
  )
}

// Scan Line Effect
export function ScanLine() {
  return (
    <motion.div
      initial={{ top: '-10%' }}
      animate={{ top: '110%' }}
      transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
      className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#00fff2]/30 to-transparent pointer-events-none z-50"
    />
  )
}

// Data Stream Background Element
export function DataStreamBg() {
  const streams = Array.from({ length: 15 }, (_, i) => ({
    left: `${(i / 15) * 100}%`,
    delay: Math.random() * 5,
    duration: 3 + Math.random() * 4
  }))

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
      {streams.map((stream, i) => (
        <motion.div
          key={i}
          initial={{ y: '-100%' }}
          animate={{ y: '100vh' }}
          transition={{
            duration: stream.duration,
            repeat: Infinity,
            delay: stream.delay,
            ease: 'linear'
          }}
          className="absolute top-0 w-px h-32 bg-gradient-to-b from-[#00fff2] via-[#00fff2]/50 to-transparent"
          style={{ left: stream.left }}
        />
      ))}
    </div>
  )
}

// Hexagon Border Frame
export function HexFrame({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`relative ${className}`}>
      {/* Corner accents */}
      <svg className="absolute top-0 left-0 w-6 h-6" viewBox="0 0 24 24">
        <path d="M0 12 L0 0 L12 0" fill="none" stroke="#00fff2" strokeWidth="2" />
      </svg>
      <svg className="absolute top-0 right-0 w-6 h-6" viewBox="0 0 24 24">
        <path d="M24 12 L24 0 L12 0" fill="none" stroke="#00fff2" strokeWidth="2" />
      </svg>
      <svg className="absolute bottom-0 left-0 w-6 h-6" viewBox="0 0 24 24">
        <path d="M0 12 L0 24 L12 24" fill="none" stroke="#ff00ff" strokeWidth="2" />
      </svg>
      <svg className="absolute bottom-0 right-0 w-6 h-6" viewBox="0 0 24 24">
        <path d="M24 12 L24 24 L12 24" fill="none" stroke="#ff00ff" strokeWidth="2" />
      </svg>
      
      {children}
    </div>
  )
}

// Glowing Border Container
export function GlowContainer({ children, color = 'cyan', className = '' }: { 
  children: React.ReactNode
  color?: 'cyan' | 'magenta' | 'purple'
  className?: string 
}) {
  const colors = {
    cyan: '#00fff2',
    magenta: '#ff00ff',
    purple: '#9d00ff'
  }

  return (
    <motion.div
      whileHover={{ boxShadow: `0 0 30px ${colors[color]}40` }}
      className={`relative border border-[${colors[color]}]/30 ${className}`}
      style={{ 
        boxShadow: `0 0 15px ${colors[color]}20`,
        background: `linear-gradient(135deg, ${colors[color]}05 0%, transparent 50%)`
      }}
    >
      {children}
    </motion.div>
  )
}

// Animated Status Indicator
export function StatusIndicator({ status = 'online', label }: { status?: 'online' | 'offline' | 'processing', label?: string }) {
  const statusColors = {
    online: '#00fff2',
    offline: '#ff0040',
    processing: '#ffff00'
  }

  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={status === 'processing' ? { scale: [1, 1.2, 1] } : { opacity: [1, 0.5, 1] }}
        transition={{ duration: status === 'processing' ? 0.5 : 2, repeat: Infinity }}
        className="w-2 h-2 rounded-full"
        style={{ 
          backgroundColor: statusColors[status],
          boxShadow: `0 0 10px ${statusColors[status]}`
        }}
      />
      {label && (
        <span className="text-[10px] font-['Orbitron'] tracking-wider uppercase" style={{ color: statusColors[status] }}>
          {label}
        </span>
      )}
    </div>
  )
}

// Binary Rain Column
export function BinaryRain({ className = '' }: { className?: string }) {
  const chars = ['0', '1']
  const columns = 20
  
  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {Array.from({ length: columns }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ y: -100 }}
          animate={{ y: '100vh' }}
          transition={{
            duration: 5 + Math.random() * 5,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: 'linear'
          }}
          className="absolute text-[8px] font-mono text-[#00fff2]/20 leading-none"
          style={{ left: `${(i / columns) * 100}%` }}
        >
          {Array.from({ length: 30 }).map((_, j) => (
            <div key={j}>{chars[Math.floor(Math.random() * 2)]}</div>
          ))}
        </motion.div>
      ))}
    </div>
  )
}
