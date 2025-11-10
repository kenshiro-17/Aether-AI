import { useState, useRef, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import TitleBar from '@/components/TitleBar'
import KnowledgePage from '@/screens/KnowledgePage'
import LearningPage from '@/screens/LearningPage'
import SettingsModal from '@/components/SettingsModal'
import ProfileModal from '@/components/ProfileModal'
import { Database, Sun, Moon, Sparkles } from 'lucide-react'
import { AnimatePresence } from 'framer-motion'

// New Components
import { MessageBubble } from '@/components/chat/MessageBubble'
import { ArtifactPanel } from '@/components/chat/ArtifactPanel'
import { WelcomeScreen } from '@/components/chat/WelcomeScreen'
import { InputArea } from '@/components/chat/InputArea'

// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Types
interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
}

interface Chat {
  id: string;
  title: string;
}

// Helper: Loading Indicator
function LoadingIndicator({ text }: { text: string }) {
  return (
    <div className="flex gap-4 items-center animate-in fade-in duration-300 pl-2">
      <div className="flex gap-1 items-center h-5">
        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce"></div>
      </div>
      <span className="text-sm text-muted-foreground font-medium animate-pulse">{text}</span>
    </div>
  )
}

import { LoadingScreen } from '@/components/LoadingScreen'
import { useAuth } from '@/context/AuthContext'
import AuthScreen from '@/screens/AuthScreen'

export default function App() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth()

  // State
  const [view, setView] = useState<'chat' | 'knowledge' | 'learning'>('chat')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [chats, setChats] = useState<Chat[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [thinkingStatus, setThinkingStatus] = useState<string | null>(null)

  // UI State
  const [activeArtifact, setActiveArtifact] = useState<{ code: string, language: string } | null>(null)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  // Features
  const [webSearchStatus, setWebSearchStatus] = useState<'connected' | 'disconnected' | null>(null)
  const [learningStats, setLearningStats] = useState<{ enabled: boolean, total_learned: number, status: string } | null>(null)
  const [isThinkingEnabled, setIsThinkingEnabled] = useState(false)
  const [isSearchEnabled, setIsSearchEnabled] = useState(true)

  // Theme
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme')
      if (saved) return saved === 'dark'
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDarkMode])

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Side Effects
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isProcessing])

  useEffect(() => { fetchChats() }, [])

  useEffect(() => {
    const fetchLearningStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/learning/stats`)
        if (res.ok) setLearningStats(await res.json())
      } catch (e) {
        console.error('Failed to fetch learning stats:', e)
      }
    }
    fetchLearningStats()
  }, [messages])

  useEffect(() => {
    if (isSearchEnabled) {
      checkWebConnection()
    } else {
      setWebSearchStatus(null)
    }
  }, [isSearchEnabled])

  // Actions
  const checkWebConnection = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/check-internet`)
      if (res.ok) {
        const data = await res.json()
        setWebSearchStatus(data.connected ? 'connected' : 'disconnected')
      } else {
        setWebSearchStatus('disconnected')
      }
    } catch {
      setWebSearchStatus('disconnected')
    }
  }

  const fetchChats = async () => {
    try {
      const res = await fetch(`${API_BASE}/history/conversations`)
      if (res.ok) setChats(await res.json())
    } catch (e) { console.error(e) }
  }

  const loadChat = async (id: string) => {
    setConversationId(id)
    setView('chat')
    setActiveArtifact(null)
    try {
      const res = await fetch(`${API_BASE}/history/conversation/${id}`)
      if (res.ok) setMessages(await res.json())
    } catch (e) { console.error(e) }
  }

  const handleDeleteChat = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/history/conversation/${id}`, { method: 'DELETE' })
      if (res.ok) {
        setChats(prev => prev.filter(c => c.id !== id))
        if (conversationId === id) {
          setConversationId(null)
          setMessages([])
        }
      }
    } catch (e) { console.error(e) }
  }

  const handleSubmit = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsProcessing(true)

    try {
      const response = await fetch(`${API_BASE}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          conversation_id: conversationId,
          enable_search: isSearchEnabled,
          enable_thinking: isThinkingEnabled
        }),
      })

      if (!response.ok) throw new Error(response.statusText)

      // Streaming implementation
      if (!response.body) throw new Error("No response body")
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let aiContent = ""
      let currentConvId = conversationId

      // Add initial empty message
      setMessages(prev => [...prev, { role: 'assistant', content: "" }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim()
            if (dataStr === '[DONE]') break

            try {
              const data = JSON.parse(dataStr)

              if (data.conversation_id) {
                currentConvId = data.conversation_id
                if (!conversationId) {
                  setConversationId(currentConvId)
                  fetchChats()
                }
              }

              if (data.status) {
                setThinkingStatus(data.status)
              }

              if (data.content) {
                // Clear thinking status once content starts flowing
                setThinkingStatus(null)
                aiContent += data.content

                // Update getLast message
                setMessages(prev => {
                  const newMsgs = [...prev]
                  newMsgs[newMsgs.length - 1] = {
                    ...newMsgs[newMsgs.length - 1],
                    content: aiContent
                  }
                  return newMsgs
                })

                // Auto-detect artifact during stream
                const codeMatch = aiContent.match(/```(\w+)\n([\s\S]+?)```/)
                if (codeMatch) {
                  // Update artifact if it exists or create new one
                  setActiveArtifact({ language: codeMatch[1], code: codeMatch[2] })
                }
              }

              if (data.error) {
                console.error("Stream Error:", data.error)
              }

            } catch (e) {
              // Ignore parse errors for partial chunks (rare with SSE but possible)
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error)
      alert("Failed to send message.")
    } finally {
      setIsProcessing(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    try {
      const isImage = file.type.startsWith('image/')
      setInput(prev => {
        const prefix = prev ? prev + ' ' : ''
        return prefix + (isImage ? `[Analyzing Vision: ${file.name}...]` : `[Uploading ${file.name}...]`)
      })

      const formData = new FormData()
      formData.append('file', file)
      const endpoint = isImage ? `${API_BASE}/api/upload` : `${API_BASE}/ingest/file`

      const res = await fetch(endpoint, { method: 'POST', body: formData })
      if (!res.ok) throw new Error('Upload failed')

      const data = await res.json()
      if (isImage) {
        setInput(prev => prev.replace(
          `[Analyzing Vision: ${file.name}...]`,
          `[Attached Image: ${file.name}]\n\n> [!NOTE] Vision Cortex Analysis\n> ${data.description}\n`
        ))
      } else {
        setInput(prev => prev.replace(`[Uploading ${file.name}...]`, `[Indexed: ${file.name}]`))
      }
    } catch (error) {
      alert("Failed to upload file.")
      setInput(prev => prev.replace(/\[(Uploading|Analyzing Vision) .*?\]/, ''))
    }
  }

  if (isAuthLoading) return <LoadingScreen />
  if (!isAuthenticated) return <AuthScreen />

  return (
    <div className="flex flex-col h-screen w-screen bg-background text-foreground overflow-hidden selection:bg-primary/20 selection:text-primary transition-colors duration-300">

      <TitleBar />

      <div className="flex flex-1 overflow-hidden relative">

        {/* Sidebar */}
        <Sidebar
          onNewChat={() => { setConversationId(null); setMessages([]); setView('chat'); setActiveArtifact(null) }}
          onSelectChat={(id) => {
            if (id === 'learning') setView('learning')
            else loadChat(id)
          }}
          onDeleteChat={handleDeleteChat}
          onOpenSettings={() => setIsSettingsOpen(true)}
          onOpenProfile={() => setIsProfileOpen(true)}
          chats={chats}
          activeChatId={conversationId}
        />

        {/* Main Content */}
        <div className="flex flex-1 flex-col h-full min-w-0 relative bg-background/50">

          {/* Header */}
          <header className="h-14 flex-shrink-0 flex items-center justify-between px-6 border-b border-border/40 z-10 w-full bg-background/50 backdrop-blur-sm">
            <div className="flex items-center gap-2">
              {/* Breadcrumbs or Title could go here */}
              {learningStats?.enabled && (
                <div className="flex items-center gap-2 px-2 py-1 bg-secondary/50 rounded-full text-[10px] font-bold text-secondary-foreground border border-border/50">
                  <Sparkles size={10} className="text-amber-400" />
                  <span>{learningStats.total_learned} Memories</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
              >
                {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <button
                onClick={() => setView(view === 'knowledge' ? 'chat' : 'knowledge')}
                className={`p-2 rounded-lg transition-colors ${view === 'knowledge' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                title="Knowledge Base"
              >
                <Database size={18} />
              </button>
            </div>
          </header>

          {/* Scroll Area */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden relative scroll-smooth">
            {view === 'knowledge' ? (
              <div className="p-8 max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-2 duration-300">
                <KnowledgePage />
              </div>
            ) : view === 'learning' ? (
              <div className="flex-1 h-full animate-in fade-in slide-in-from-bottom-2 duration-300">
                <LearningPage />
              </div>
            ) : (
              <div className="max-w-3xl mx-auto w-full pb-48 pt-8 px-4 flex flex-col justify-end min-h-0">
                {messages.length === 0 ? (
                  <WelcomeScreen onCapabilityClick={(prompt) => setInput(prompt)} />
                ) : (
                  <div className="space-y-6">
                    {messages.map((msg, idx) => (
                      <MessageBubble
                        key={idx}
                        message={msg}
                        isDarkMode={isDarkMode}
                        onOpenArtifact={(code, lang) => setActiveArtifact({ code, language: lang })}
                      />
                    ))}
                    {isProcessing && <LoadingIndicator text={thinkingStatus || "Thinking..."} />}
                    <div ref={messagesEndRef} className="h-4" />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Floating Input Area */}
          {view === 'chat' && (
            <InputArea
              input={input}
              setInput={setInput}
              onSubmit={handleSubmit}
              isThinkingEnabled={isThinkingEnabled}
              setIsThinkingEnabled={setIsThinkingEnabled}
              isSearchEnabled={isSearchEnabled}
              setIsSearchEnabled={setIsSearchEnabled}
              webSearchStatus={webSearchStatus}
              onFileSelect={handleFileUpload}
            />
          )}
        </div>

        {/* Artifact Panel - Slide Over */}
        <AnimatePresence>
          {activeArtifact && view === 'chat' && (
            <ArtifactPanel
              code={activeArtifact.code}
              language={activeArtifact.language}
              onClose={() => setActiveArtifact(null)}
              isDarkMode={isDarkMode}
            />
          )}
        </AnimatePresence>

        {/* Modals */}
        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          conversationCount={chats.length}
        />
        <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />

      </div>
    </div>
  )
}
