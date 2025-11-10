import { useState, useRef, useEffect } from 'react'
import { Command, Terminal, Sparkles, GraduationCap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function LearningPage() {
    const [topic, setTopic] = useState('')
    const [isLearning, setIsLearning] = useState(false)
    const [logs, setLogs] = useState<string[]>([])
    const logsEndRef = useRef<HTMLDivElement>(null)

    // State for Network
    const [networkStatus, setNetworkStatus] = useState<'checking' | 'online' | 'offline'>('checking')
    const [isMasteryMode, setIsMasteryMode] = useState(false)
    const [isAutoMode, setIsAutoMode] = useState(false)
    const [level, setLevel] = useState("PHD")

    useEffect(() => {
        checkNetwork()
    }, [])

    const checkNetwork = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/check-internet`)
            const data = await res.json()
            setNetworkStatus(data.connected ? 'online' : 'offline')
        } catch {
            setNetworkStatus('offline')
        }
    }

    // API URL
    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    const startLearning = async (isRecursive = false) => {
        if (networkStatus === 'offline') {
            setLogs(prev => [...prev, ">> WARNING: Connectivity check failed, but forcing uplink...", ">> Attempting to bypass..."])
        } else {
            if (!topic.trim() && !isRecursive && !isAutoMode) return
        }

        if (!isRecursive && !topic.trim() && !isAutoMode) {
            setLogs(prev => [...prev, ">> ERROR: SUBJECT REQUIRED FOR MANUAL/MASTERY MODES."])
            return
        }

        setIsLearning(true)
        setLogs(["INITIATING NEURAL LINK...", "Connecting to Cortex..."])

        let endpoint = `${API_BASE}/v1/learn/stream?topic=${encodeURIComponent(topic)}`

        if (isAutoMode) {
            // Deep Automation Mode
            endpoint = `${API_BASE}/v1/learn/automate/stream?topic=${encodeURIComponent(topic)}&level=${level}`
            setLogs(prev => [...prev, `>> INITIATING DEEP AUTOMATION PROTOCOL (${level})...`, ">> CONSULTING EXPERT PROFESSORS...", `>> Endpoint: ${endpoint}`])
        } else if (isRecursive) {
            // Autonomous Mode (Curriculum)
            endpoint = `${API_BASE}/v1/learn/auto/stream`
            setLogs(prev => [...prev, ">> AUTO-PILOT ENGAGED (Curriculum Mode).", `>> Endpoint: ${endpoint}`])
        } else if (isMasteryMode) {
            setLogs(prev => [...prev, ">> ACTIVATING MASTERY PROTOCOL...", ">> GENERATING CURRICULUM...", `>> Endpoint: ${endpoint}`])
            endpoint = `${API_BASE}/v1/learn/mastery/stream?topic=${encodeURIComponent(topic)}`
        } else {
            setLogs(prev => [...prev, `>> Endpoint: ${endpoint}`])
        }

        const eventSource = new EventSource(endpoint)

        eventSource.onmessage = (event) => {
            const data = event.data
            if (data === "[DONE]") {
                setIsLearning(false)
                eventSource.close()
                setLogs(prev => [...prev, ">> PROCESS COMPLETE. STANDBY."])
            } else {
                setLogs(prev => [...prev, data])
            }
        }

        eventSource.onerror = () => {
            setLogs(prev => [...prev, ">> ERROR: SIGNAL LOST."])
            setIsLearning(false)
            eventSource.close()
        }
    }

    return (
        <div className="flex flex-col h-full max-w-5xl mx-auto p-6 gap-6">

            {/* Header */}
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-display font-bold text-foreground">Active Learning</h1>
                <p className="text-muted-foreground">
                    Deploy the AI to autonomously research a topic, read articles, and commit facts to long-term memory.
                </p>
            </div>
            {/* Network Status Badge */}
            <div className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono border
                ${networkStatus === 'online'
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
                    : 'bg-red-500/10 border-red-500/20 text-red-500'
                }
`}>
                <div className={`w-2 h-2 rounded-full ${networkStatus === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'} `} />
                {networkStatus === 'online' ? 'UPLINK ESTABLISHED' : 'NETWORK OFFLINE'}
            </div>


            {/* Input Section */}
            <div className="flex gap-4 items-center">
                <div className="relative flex-1">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                        <Sparkles size={18} />
                    </div>
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Enter a topic (e.g. 'SpaceX Starship', 'React 19 features', 'History of Rome')..."
                        className="w-full bg-background border border-border rounded-xl py-3 pl-10 pr-4 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                        disabled={isLearning}
                        onKeyDown={(e) => e.key === 'Enter' && startLearning()}
                    />
                </div>
                {/* Start Button */}
                <button
                    onClick={() => startLearning()}
                    disabled={isLearning}
                    className={`px-8 py-4 rounded-xl font-bold tracking-widest transition-all duration-300 ${isLearning
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                        : isMasteryMode
                            ? 'bg-purple-500 hover:bg-purple-400 text-black shadow-[0_0_30px_rgba(168,85,247,0.5)] border border-purple-400'
                            : 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_30px_rgba(6,182,212,0.5)] border border-cyan-400'
                        } `}
                >
                    {isLearning ? 'NEURAL SYNC ACTIVE...' : isMasteryMode ? 'INITIATE MASTERY' : 'INITIATE RESEARCH'}
                </button>
            </div>

            {/* Mode Toggles */}
            <div className="flex flex-col gap-4">
                <div className="flex gap-4 flex-wrap">
                    <button
                        onClick={() => { setIsMasteryMode(false); setIsAutoMode(false) }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${!isMasteryMode && !isAutoMode ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'text-zinc-600 hover:text-zinc-400'}`}
                    >
                        <Sparkles size={14} /> MANUAL MODE
                    </button>
                    <button
                        onClick={() => { setIsMasteryMode(true); setIsAutoMode(false) }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${isMasteryMode && !isAutoMode ? 'bg-purple-500/20 text-purple-400 border border-purple-500/50' : 'text-zinc-600 hover:text-zinc-400'}`}
                    >
                        <GraduationCap size={14} /> MASTERY MODE
                    </button>
                    <button
                        onClick={() => { setIsAutoMode(true); setIsMasteryMode(false) }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${isAutoMode ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'text-zinc-600 hover:text-zinc-400'}`}
                    >
                        <Sparkles size={14} /> AUTOMATION TASK (DEEP)
                    </button>
                </div>

                {/* Level Selector for Automation Mode */}
                {isAutoMode && (
                    <div className="flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                        <span className="text-zinc-500 text-sm font-mono">TARGET LEVEL:</span>
                        {["Undergrad", "Graduate", "PHD"].map((l) => (
                            <button
                                key={l}
                                onClick={() => setLevel(l)}
                                className={`px-3 py-1 rounded text-xs font-mono border transition-all ${level === l ? 'bg-amber-500 text-black border-amber-500 font-bold' : 'border-zinc-700 text-zinc-500 hover:border-zinc-500'}`}
                            >
                                {l.toUpperCase()}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Matrix Logs Terminal */}
            <div className="flex-1 bg-black rounded-xl border border-zinc-800 shadow-2xl overflow-hidden flex flex-col font-mono text-sm relative">

                {/* Terminal Header */}
                <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-800 flex items-center gap-2">
                    <Terminal size={14} className="text-emerald-500" />
                    <span className="text-zinc-400 text-xs">AETHER_CORE // LEARNING_MODULE // TTY_01</span>
                </div>

                {/* Content */}
                <div className="flex-1 p-6 overflow-y-auto space-y-2 font-mono scrollbar-hide">

                    {logs.length === 0 && !isLearning && (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-600 gap-4 opacity-50">
                            <Command size={48} />
                            <p>Awaiting Instructions...</p>
                        </div>
                    )}

                    <AnimatePresence>
                        {logs.map((log, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="text-emerald-500/90 whitespace-pre-wrap break-words"
                            >
                                <span className="text-emerald-800/50 mr-2">[{new Date().toLocaleTimeString()}]</span>
                                {log}
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {isLearning && (
                        <motion.div
                            animate={{ opacity: [0, 1, 0] }}
                            transition={{ repeat: Infinity, duration: 0.8 }}
                            className="w-3 h-5 bg-emerald-500/50 inline-block align-middle"
                        />
                    )}
                    <div ref={logsEndRef} />
                </div>

                {/* CRT Scanline Effect */}
                <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 bg-[length:100%_2px,3px_100%] opacity-20" />
            </div>

        </div >
    )
}
