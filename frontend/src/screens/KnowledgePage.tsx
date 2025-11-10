import { useState, useEffect } from 'react'
import { Save, BookOpen, Search, FileText, Database, Globe, Code } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'


// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Memory {
  id: string
  content: string
  metadata: Record<string, any>
}

export default function KnowledgePage() {
  const [activeTab, setActiveTab] = useState<'browse' | 'add'>('browse')


  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-500 shadow-sm border border-indigo-500/20">
            <Database size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Neural Memory</h1>
            <p className="text-zinc-400 text-sm font-medium">Manage long-term knowledge and sources.</p>
          </div>
        </div>

        <div className="flex bg-zinc-900/50 p-1 rounded-xl border border-white/5 backdrop-blur-sm">
          <TabButton
            active={activeTab === 'browse'}
            onClick={() => setActiveTab('browse')}
            icon={Search}
            label="Browse"
          />
          <TabButton
            active={activeTab === 'add'}
            onClick={() => setActiveTab('add')}
            icon={Save}
            label="Ingest"
          />
        </div>
      </div>

      <div className="flex-1 min-h-0 relative">
        <AnimatePresence mode="wait">
          {activeTab === 'browse' ? (
            <BrowseView key="browse" />
          ) : (
            <IngestView key="add" />
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

function TabButton({ active, onClick, icon: Icon, label }: any) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${active
        ? 'bg-white/10 text-white shadow-sm'
        : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5'
        }`}
    >
      <Icon size={16} />
      {label}
    </button>
  )
}

function BrowseView() {
  const [memories, setMemories] = useState<Memory[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all' | 'file' | 'web' | 'manual'>('all')

  useEffect(() => {
    fetchMemories()
  }, [])

  const fetchMemories = async () => {
    try {
      const res = await fetch(`${API_BASE}/memory/list?limit=500`)
      const data = await res.json()
      if (data.memories) setMemories(data.memories)
    } catch (e) {
      console.error("Failed to load memory", e)
    } finally {
      setLoading(false)
    }
  }

  // Processing & Grouping
  const filtered = memories.filter(m => {
    const matchesSearch = m.content.toLowerCase().includes(search.toLowerCase()) ||
      JSON.stringify(m.metadata).toLowerCase().includes(search.toLowerCase())

    const type = m.metadata.source || m.metadata.type || 'manual'
    const matchesFilter = filter === 'all' ||
      (filter === 'file' && (type === 'file' || m.metadata.filename)) ||
      (filter === 'web' && (type.includes('http') || m.metadata.url)) ||
      (filter === 'manual' && (!m.metadata.filename && !type.includes('http')))

    return matchesSearch && matchesFilter
  })

  // Organize by "Source" Name
  const grouped: Record<string, Memory[]> = {}
  filtered.forEach(m => {
    let groupName = "General Knowledge"
    if (m.metadata.filename) groupName = `📄 ${m.metadata.filename}`
    else if (m.metadata.source && m.metadata.source.startsWith('http')) groupName = `🌐 ${new URL(m.metadata.source).hostname}`
    else if (m.metadata.source) groupName = `🏷️ ${m.metadata.source}`

    if (!grouped[groupName]) grouped[groupName] = []
    grouped[groupName].push(m)
  })

  if (loading) return <div className="flex h-full items-center justify-center text-zinc-500 animate-pulse">Accessing Neural Core...</div>

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="space-y-4 h-full flex flex-col"
    >
      {/* Search & Filter Bar */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 text-zinc-500 w-4 h-4" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search neural patterns..."
            className="w-full bg-zinc-900/50 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500/50 focus:bg-zinc-900 transition-all font-mono"
          />
        </div>
        <div className="flex bg-zinc-900/50 p-1 rounded-xl border border-white/5">
          {['all', 'file', 'web', 'manual'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${filter === f ? 'bg-white/10 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Content Grid */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-zinc-800">
        {Object.keys(grouped).length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-zinc-500 text-sm">
            <Database className="w-8 h-8 mb-3 opacity-20" />
            No memory patterns found.
          </div>
        ) : (
          Object.entries(grouped).map(([group, items]) => (
            <div key={group} className="space-y-3">
              <h3 className="text-zinc-400 text-xs font-bold uppercase tracking-wider pl-1 flex items-center gap-2 sticky top-0 bg-background/80 backdrop-blur pb-2 pt-2 z-10">
                {group}
                <span className="text-zinc-600 text-[10px] bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded-md">{items.length} nodes</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {items.map(mem => (
                  <MemoryCard key={mem.id} memory={mem} />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}

function MemoryCard({ memory }: { memory: Memory }) {
  const isCode = memory.metadata.type === 'code' || memory.content.includes('def ') || memory.content.includes('function')

  return (
    <div className="group bg-zinc-900/30 border border-white/5 hover:border-indigo-500/30 rounded-xl p-4 transition-all hover:bg-zinc-900/60 flex flex-col gap-3 h-48">
      <div className="flex-1 overflow-hidden relative">
        <code className={`block text-xs leading-relaxed ${isCode ? 'text-blue-300 font-mono' : 'text-zinc-300 font-sans'}`}>
          {memory.content.slice(0, 200)}
          {memory.content.length > 200 && "..."}
        </code>
        <div className="absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-zinc-950/80 to-transparent" />
      </div>

      <div className="flex items-center gap-2 mt-auto pt-2 border-t border-white/5">
        {isCode ? <Code size={12} className="text-blue-400" /> : <FileText size={12} className="text-zinc-500" />}
        <span className="text-[10px] text-zinc-500 font-mono truncate max-w-[150px]">
          {memory.id.slice(0, 8)} • {memory.metadata.source || 'Direct Input'}
        </span>
      </div>
    </div>
  )
}

function IngestView() {
  const [text, setText] = useState('')
  const [status, setStatus] = useState('')

  const handleIngest = async () => {
    if (!text.trim()) return
    setStatus('Processing neural connections...')
    try {
      const res = await fetch(`${API_BASE}/memory/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })

      if (res.ok) {
        setStatus('Success: Neural pathway established.')
        setText('')
        setTimeout(() => setStatus(''), 3000)
      } else {
        setStatus('Error: Neural Interface Rejected Input.')
      }
    } catch (e) {
      setStatus('Critical Error: Backend Disconnected.')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="h-full flex flex-col bg-zinc-900/30 border border-white/5 rounded-2xl p-1 shadow-inner"
    >
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter raw data for neural integration..."
        className="flex-1 bg-transparent border-0 p-6 text-zinc-200 placeholder:text-zinc-700 resize-none focus:ring-0 font-mono text-sm leading-relaxed"
        spellCheck={false}
      />
      <div className="p-4 border-t border-white/5 flex justify-between items-center bg-zinc-950/30 rounded-b-xl">
        <span className={`text-xs font-mono transition-colors ${status.includes('Success') ? 'text-emerald-400' : 'text-zinc-500'}`}>
          {status || "Ready to ingest"}
        </span>
        <button
          onClick={handleIngest}
          disabled={!text.trim()}
          className="flex items-center gap-2 px-6 py-2 rounded-xl bg-indigo-600 text-white font-semibold text-xs hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-all shadow-lg shadow-indigo-500/20"
        >
          <Save size={14} />
          Integrate Data
        </button>
      </div>
    </motion.div>
  )
}
