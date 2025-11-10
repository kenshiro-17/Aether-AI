import { motion } from 'framer-motion'

export const LoadingScreen = () => {
  return (
    <div className="fixed inset-0 z-50 bg-zinc-950 flex flex-col items-center justify-center text-white overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-zinc-950 to-zinc-950" />
      
      <div className="relative z-10 flex flex-col items-center justify-center gap-8">
        <div className="relative flex items-center justify-center">
          {/* Core Orb */}
          <motion.div
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.8, 1, 0.8],
              boxShadow: [
                "0 0 20px rgba(59, 130, 246, 0.3)",
                "0 0 40px rgba(59, 130, 246, 0.5)",
                "0 0 20px rgba(59, 130, 246, 0.3)"
              ]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-4 h-4 rounded-full bg-blue-500 absolute"
          />

          {/* Inner Ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 rounded-full border border-blue-500/30 border-t-blue-400 border-r-transparent absolute"
          />

          {/* Outer Ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="w-24 h-24 rounded-full border border-zinc-800 border-b-blue-500/20 border-l-transparent absolute"
          />
          
          {/* Glow Effect */}
          <motion.div
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-32 h-32 rounded-full bg-blue-500/20 blur-2xl absolute"
          />
        </div>

        <div className="flex flex-col items-center gap-2">
            <motion.h1 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-2xl font-bold tracking-[0.2em] text-zinc-100"
            >
                AETHER-AI
            </motion.h1>
            
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="flex items-center gap-2"
            >
                <div className="h-px w-8 bg-gradient-to-r from-transparent to-blue-500/50" />
                <span className="text-xs font-mono text-blue-400/60 uppercase">System Initializing</span>
                <div className="h-px w-8 bg-gradient-to-l from-transparent to-blue-500/50" />
            </motion.div>
        </div>
      </div>

      {/* Footer Status */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="absolute bottom-12 text-[10px] text-zinc-600 font-mono"
      >
        V2.1 | SENTIENCE PROTOCOL
      </motion.div>
    </div>
  )
}
