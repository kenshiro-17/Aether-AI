import { Plus, MessageSquare, Menu, X, ChevronLeft, ChevronRight, Settings, Command, Sparkles, User } from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface SidebarProps {
  onNewChat: () => void
  onSelectChat: (id: string) => void
  onDeleteChat: (id: string) => void
  onOpenSettings: () => void
  onOpenProfile: () => void
  chats: { id: string; title: string }[]
  activeChatId: string | null
}

export default function Sidebar({ onNewChat, onSelectChat, onDeleteChat, onOpenSettings, onOpenProfile, chats, activeChatId }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const sidebarVariants = {
    expanded: { width: 280 },
    collapsed: { width: 72 }
  }

  return (
    <>
      {/* Mobile Toggle */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          className="p-2.5 bg-background shadow-sm rounded-lg border border-border text-foreground transition-colors hover:bg-muted"
        >
          {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Sidebar Container */}
      <motion.aside
        initial={false}
        animate={isCollapsed ? 'collapsed' : 'expanded'}
        variants={sidebarVariants}
        transition={{ duration: 0.3, ease: [0.33, 1, 0.68, 1] }} // smooth cubic bezier
        className={`
          h-full flex flex-col z-40 border-r border-border
          backdrop-blur-xl bg-zinc-50/80 dark:bg-black/40
          ${isMobileOpen ? 'fixed inset-y-0 left-0 w-72 shadow-2xl' : 'hidden md:flex relative'}
        `}
      >
        {/* Header */}
        <div
          className="h-16 flex items-center px-4 title-drag-region cursor-default"
          onDoubleClick={() => {
            const ipc = (window as any).require ? (window as any).require('electron').ipcRenderer : null
            ipc?.send('window-maximize')
          }}
        >
          <AnimatePresence mode="wait">
            {!isCollapsed ? (
              <motion.button
                onClick={onNewChat}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex flex-1 items-center gap-2 group cursor-pointer"
              >
                <div className="w-8 h-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center shadow-sm group-hover:bg-primary/90 transition-colors">
                  <Command size={18} strokeWidth={2.5} />
                </div>
                <span className="font-display font-semibold text-lg tracking-tight text-foreground">
                  Aether
                </span>
                <span className="ml-2 text-[10px] font-mono bg-zinc-200 dark:bg-zinc-800 text-muted-foreground px-1.5 py-0.5 rounded">
                  v1.5
                </span>
              </motion.button>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full flex justify-center"
              >
                <div className="w-8 h-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center shadow-sm">
                  <Command size={18} strokeWidth={2.5} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {!isCollapsed && (
            <button
              onClick={() => setIsCollapsed(true)}
              className="p-2 rounded-md text-muted-foreground hover:bg-zinc-200 dark:hover:bg-zinc-800 hover:text-foreground transition-all ml-auto opacity-0 group-hover/sidebar:opacity-100"
            >
              <ChevronLeft size={16} />
            </button>
          )}
        </div>

        {/* Start New Chat (Collapsed only) */}
        {isCollapsed && (
          <div className="flex justify-center mb-4">
            <button
              onClick={onNewChat}
              className="w-10 h-10 rounded-xl bg-zinc-200 dark:bg-zinc-800 text-foreground hover:bg-zinc-300 dark:hover:bg-zinc-700 flex items-center justify-center transition-colors"
              title="New Chat"
            >
              <Plus size={20} />
            </button>
          </div>
        )}

        {/* Collapsed Expand Button */}
        {isCollapsed && (
          <button
            onClick={() => setIsCollapsed(false)}
            className="absolute top-1/2 -right-3 transform -translate-y-1/2 w-6 h-6 bg-background border border-border shadow-sm rounded-full flex items-center justify-center text-muted-foreground hover:text-primary z-50 transition-colors"
            title="Expand"
          >
            <ChevronRight size={14} />
          </button>
        )}


        {/* Navigation / Active Learning */}
        <div className="px-3 space-y-1 mt-2">
          {!isCollapsed && (
            <button
              onClick={onNewChat}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-background border border-border/80 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:border-border text-foreground transition-all shadow-sm group"
            >
              <Plus size={16} className="text-muted-foreground group-hover:text-foreground" />
              <span>New Chat</span>
            </button>
          )}

          <button
            onClick={() => onSelectChat('learning')}
            className={`
                w-full flex items-center gap-3
                text-foreground
                rounded-lg transition-all duration-200
                group relative
                ${isCollapsed ? 'justify-center p-2 mt-4' : 'px-3 py-2.5 hover:bg-zinc-200/50 dark:hover:bg-zinc-800/50'}
            `}
            title="Auto-Learning"
          >
            <div className={`
                flex items-center justify-center w-5 h-5 rounded-md
                ${activeChatId === 'learning' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-transparent text-muted-foreground group-hover:text-foreground'}
            `}>
              <Sparkles size={16} strokeWidth={2} />
            </div>
            {!isCollapsed && <span className="text-sm font-medium">Auto-Learning</span>}
          </button>
        </div>


        {/* Chat List Label */}
        {!isCollapsed && (
          <div className="px-6 mt-6 mb-2 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-muted-foreground/60 uppercase tracking-widest">History</span>
          </div>
        )}

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5 scrollbar-none">
          {chats.map((chat) => (
            <motion.div
              layout
              key={chat.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative group"
            >
              <div
                onClick={() => { onSelectChat(chat.id); setIsMobileOpen(false); }}
                className={`
                        w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-colors relative z-10
                        ${activeChatId === chat.id
                    ? 'bg-zinc-200 dark:bg-zinc-800 text-foreground font-medium'
                    : 'text-muted-foreground hover:bg-zinc-100 dark:hover:bg-zinc-900 hover:text-foreground'}
                        ${isCollapsed ? 'justify-center px-0' : ''}
                    `}
                title={isCollapsed ? chat.title : undefined}
              >
                {isCollapsed ? (
                  <div className={`w-2 h-2 rounded-full ${activeChatId === chat.id ? 'bg-primary' : 'bg-zinc-300 dark:bg-zinc-700'}`} />
                ) : (
                  <>
                    <span className="truncate flex-1">{chat.title}</span>
                  </>
                )}
              </div>

              {/* Delete Action (Float on Hover) */}
              {!isCollapsed && activeChatId === chat.id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('Delete log file?')) onDeleteChat(chat.id)
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 z-20 opacity-0 group-hover:opacity-100 p-1.5 text-muted-foreground hover:text-red-500 transition-all hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-md"
                >
                  <X size={14} />
                </button>
              )}
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border mt-auto">
          <button
            onClick={onOpenProfile}
            className={`flex items-center gap-3 w-full hover:bg-zinc-100 dark:hover:bg-zinc-900 rounded-xl p-2 transition-colors group ${isCollapsed ? 'justify-center p-0 hover:bg-transparent' : ''}`}
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shrink-0 shadow-sm border border-white/10">
              <User size={16} className="text-white" />
            </div>

            {!isCollapsed && (
              <div className="flex flex-col items-start overflow-hidden">
                <span className="text-sm font-medium text-foreground truncate max-w-[140px]">User Profile</span>
                <span className="text-[11px] text-muted-foreground truncate">Local Account</span>
              </div>
            )}

            {!isCollapsed && (
              <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
                <Settings size={16} className="text-muted-foreground" onClick={(e) => { e.stopPropagation(); onOpenSettings() }} />
              </div>
            )}
          </button>

          {isCollapsed && (
            <button onClick={onOpenSettings} className="mt-4 mx-auto block text-muted-foreground hover:text-foreground">
              <Settings size={20} />
            </button>
          )}

        </div>
      </motion.aside>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="md:hidden fixed inset-0 z-30 bg-black/50 backdrop-blur-sm"
            onClick={() => setIsMobileOpen(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}
