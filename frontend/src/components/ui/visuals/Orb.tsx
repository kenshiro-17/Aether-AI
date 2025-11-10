import { motion } from "framer-motion";

export const Orb = () => {
  return (
    <div className="relative w-48 h-48 flex items-center justify-center">
      {/* Background glow */}
      <div className="absolute inset-0 bg-[#00fff2]/10 rounded-full blur-3xl animate-pulse" />
      
      {/* Outer hexagonal ring - rotating slowly */}
      <motion.svg
        animate={{ rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        className="absolute w-44 h-44"
        viewBox="0 0 100 100"
      >
        <polygon
          points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"
          fill="none"
          stroke="#00fff2"
          strokeWidth="0.5"
          opacity="0.15"
        />
      </motion.svg>

      {/* Second hex ring - counter rotating slowly */}
      <motion.svg
        animate={{ rotate: -360 }}
        transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
        className="absolute w-36 h-36"
        viewBox="0 0 100 100"
      >
        <polygon
          points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"
          fill="none"
          stroke="#ff00ff"
          strokeWidth="0.5"
          opacity="0.15"
        />
      </motion.svg>

      {/* Pulsing rings - subtle */}
      <motion.div
        animate={{ scale: [1, 1.1, 1], opacity: [0.15, 0.05, 0.15] }}
        transition={{ duration: 4, repeat: Infinity }}
        className="absolute w-32 h-32 border border-[#00fff2]/20 rounded-full"
      />
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.05, 0.1] }}
        transition={{ duration: 5, repeat: Infinity, delay: 0.5 }}
        className="absolute w-28 h-28 border border-[#ff00ff]/15 rounded-full"
      />

      {/* DedSec Mask SVG */}
      <motion.div
        animate={{ 
          filter: [
            'drop-shadow(0 0 10px #00fff2)',
            'drop-shadow(0 0 20px #00fff2)',
            'drop-shadow(0 0 10px #00fff2)'
          ]
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className="relative z-10"
      >
        <svg width="80" height="80" viewBox="0 0 100 100" className="drop-shadow-[0_0_15px_#00fff2]">
          {/* Mask outline */}
          <path
            d="M50 10 L85 30 L85 70 L50 90 L15 70 L15 30 Z"
            fill="none"
            stroke="#00fff2"
            strokeWidth="2"
            className="animate-pulse"
          />
          
          {/* Left eye */}
          <motion.circle
            cx="35"
            cy="45"
            r="8"
            fill="#00fff2"
            animate={{ 
              opacity: [1, 0.5, 1],
              r: [8, 9, 8]
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
            style={{ filter: 'drop-shadow(0 0 10px #00fff2)' }}
          />
          
          {/* Right eye */}
          <motion.circle
            cx="65"
            cy="45"
            r="8"
            fill="#00fff2"
            animate={{ 
              opacity: [1, 0.5, 1],
              r: [8, 9, 8]
            }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
            style={{ filter: 'drop-shadow(0 0 10px #00fff2)' }}
          />
          
          {/* Mouth/teeth - horizontal lines */}
          <motion.g
            animate={{ opacity: [0.8, 1, 0.8] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <line x1="30" y1="65" x2="70" y2="65" stroke="#00fff2" strokeWidth="2" />
            <line x1="35" y1="60" x2="35" y2="70" stroke="#00fff2" strokeWidth="1.5" />
            <line x1="45" y1="60" x2="45" y2="70" stroke="#00fff2" strokeWidth="1.5" />
            <line x1="55" y1="60" x2="55" y2="70" stroke="#00fff2" strokeWidth="1.5" />
            <line x1="65" y1="60" x2="65" y2="70" stroke="#00fff2" strokeWidth="1.5" />
          </motion.g>

          {/* Forehead symbol */}
          <motion.path
            d="M45 25 L50 20 L55 25 L50 30 Z"
            fill="#ff00ff"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1, repeat: Infinity }}
            style={{ filter: 'drop-shadow(0 0 5px #ff00ff)' }}
          />
        </svg>
      </motion.div>

      {/* Glitch effect overlay */}
      <motion.div
        animate={{
          opacity: [0, 0.5, 0],
          x: [-2, 2, -2],
        }}
        transition={{
          duration: 0.1,
          repeat: Infinity,
          repeatDelay: 3,
        }}
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
      >
        <svg width="80" height="80" viewBox="0 0 100 100" className="opacity-50">
          <path
            d="M50 10 L85 30 L85 70 L50 90 L15 70 L15 30 Z"
            fill="none"
            stroke="#ff00ff"
            strokeWidth="2"
          />
        </svg>
      </motion.div>

      {/* Data particles */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          animate={{
            y: [0, -30, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 2 + Math.random(),
            repeat: Infinity,
            delay: i * 0.2,
          }}
          className="absolute text-[8px] font-mono text-[#00fff2]/60"
          style={{
            top: `${20 + Math.random() * 60}%`,
            left: `${10 + Math.random() * 80}%`,
          }}
        >
          {Math.random() > 0.5 ? '1' : '0'}
        </motion.div>
      ))}

      {/* Corner brackets */}
      <div className="absolute top-2 left-2 w-4 h-4 border-l-2 border-t-2 border-[#00fff2]/50" />
      <div className="absolute top-2 right-2 w-4 h-4 border-r-2 border-t-2 border-[#00fff2]/50" />
      <div className="absolute bottom-2 left-2 w-4 h-4 border-l-2 border-b-2 border-[#00fff2]/50" />
      <div className="absolute bottom-2 right-2 w-4 h-4 border-r-2 border-b-2 border-[#00fff2]/50" />
    </div>
  );
};
