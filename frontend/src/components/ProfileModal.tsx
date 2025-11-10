import { X, MessageSquare, FileText, Database } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

import { useAuth } from '@/context/AuthContext'

export default function ProfileModal({ isOpen, onClose }: ProfileModalProps) {
  const { user, logout } = useAuth()
  const [profile, setProfile] = useState({
    name: 'Operator',
    role: 'System Administrator',
    avatar: 'OP',
    stats: {
      total_conversations: 0,
      total_messages: 0,
      documents_indexed: 0
    }
  })

  useEffect(() => {
    if (isOpen) {
      fetchProfile()
    }
  }, [isOpen])

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/profile`)
      if (res.ok) {
        const data = await res.json()
        setProfile(data)
      }
    } catch (e) {
      console.error('Failed to fetch profile:', e)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-card w-full max-w-lg rounded-2xl shadow-xl overflow-hidden border border-border"
        >
          {/* Header */}
          <div className="relative">
            {/* Cover gradient */}
            <div className="h-32 bg-gradient-to-br from-primary/80 via-accent to-primary rounded-t-2xl opacity-90" />

            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 bg-black/20 hover:bg-black/30 backdrop-blur-md rounded-lg transition-colors text-white"
            >
              <X size={20} />
            </button>

            {/* Avatar */}
            <div className="absolute -bottom-12 left-6">
              <div className="w-24 h-24 rounded-2xl bg-card border-4 border-card shadow-xl flex items-center justify-center">
                <span className="text-3xl font-bold text-primary">{profile.avatar}</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="pt-16 px-6 pb-6 space-y-6">
            {/* User Info */}
            <div>
              <h2 className="text-2xl font-display font-bold text-foreground">{profile.name}</h2>
              <p className="text-sm text-muted-foreground font-medium">{profile.role}</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <StatCard
                icon={MessageSquare}
                label="Conversations"
                value={profile.stats.total_conversations}
              />
              <StatCard
                icon={FileText}
                label="Messages"
                value={profile.stats.total_messages}
              />
              <StatCard
                icon={Database}
                label="Documents"
                value={profile.stats.documents_indexed}
              />
            </div>

            {/* Status */}
            <div className="p-4 rounded-xl border border-border bg-emerald-500/5">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                <div>
                  <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">System Status: Online</p>
                  <p className="text-xs text-emerald-600/80 dark:text-emerald-400/80">All systems operational</p>
                </div>
              </div>
            </div>

            {/* Info */}
            <div className="space-y-2">
              <InfoRow label="Access Level" value="Administrator" />
              <InfoRow label="Encryption" value="AES-256" />
              <InfoRow label="Connection" value="Secure Local Network" />
              <InfoRow label="Version" value="Aether OS v1.0.0" />
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-border px-6 py-4 bg-muted/20">
            <div className="flex justify-between items-center">
              <p className="text-xs text-muted-foreground font-medium">
                Authenticated: {user?.username}
              </p>
              <button
                onClick={() => { logout(); onClose() }}
                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 text-xs font-bold rounded-lg transition-colors border border-red-500/20"
              >
                LOGOUT
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

function StatCard({ icon: Icon, label, value }: { icon: any, label: string, value: number }) {
  return (
    <div className="p-4 rounded-xl border border-border bg-card hover:bg-muted/50 transition-colors">
      <div className={`w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-2`}>
        <Icon size={16} />
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground font-medium">{label}</p>
    </div>
  )
}

function InfoRow({ label, value }: { label: string, value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-border last:border-0">
      <span className="text-sm text-muted-foreground font-medium">{label}</span>
      <span className="text-sm font-semibold text-foreground">{value}</span>
    </div>
  )
}
