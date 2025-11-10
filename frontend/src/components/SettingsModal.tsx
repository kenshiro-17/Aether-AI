import { X, Wifi, WifiOff, Loader2, Settings as SettingsIcon, Save } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
  conversationCount: number
}

export default function SettingsModal({ isOpen, onClose, conversationCount }: SettingsModalProps) {
  const [settings, setSettings] = useState({
    model: 'Llama 3.2 3B Instruct',
    temperature: 0.7,
    max_tokens: 16384,
    context_size: 32768
  })
  const [internetStatus, setInternetStatus] = useState<{ connected: boolean, status: string, latency_ms?: number } | null>(null)
  const [checkingInternet, setCheckingInternet] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle')

  const [profileStats, setProfileStats] = useState<any>(null)

  useEffect(() => {
    if (isOpen) {
      fetchSettings()
      checkInternet()
      fetchProfile()
    }
  }, [isOpen])

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/profile`)
      if (res.ok) setProfileStats(await res.json())
    } catch (e) { console.error(e) }
  }

  const fetchSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/settings`)
      if (res.ok) {
        const data = await res.json()
        setSettings(data)
      }
    } catch (e) {
      console.error('Failed to fetch settings:', e)
    }
  }

  const checkInternet = async () => {
    setCheckingInternet(true)
    try {
      const res = await fetch(`${API_BASE}/api/check-internet`)
      if (res.ok) {
        const data = await res.json()
        setInternetStatus(data)
      }
    } catch (e) {
      setInternetStatus({ connected: false, status: 'Connection check failed' })
    } finally {
      setCheckingInternet(false)
    }
  }

  const handleSave = async () => {
    setSaveStatus('saving')
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      })
      if (res.ok) {
        setSaveStatus('saved')
        setTimeout(() => setSaveStatus('idle'), 2000)
      }
    } catch (e) {
      console.error('Failed to save settings:', e)
      setSaveStatus('idle')
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
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-card border border-border rounded-xl shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <SettingsIcon size={20} className="text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-foreground">System Settings</h2>
                <p className="text-xs text-muted-foreground">Configure AI parameters</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-8">
            {/* Internet Status */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Internet Connection</h3>
              <div className="p-4 rounded-lg border border-border bg-muted/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {checkingInternet ? (
                      <Loader2 size={18} className="text-primary animate-spin" />
                    ) : internetStatus?.connected ? (
                      <Wifi size={18} className="text-green-500" />
                    ) : (
                      <WifiOff size={18} className="text-destructive" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {checkingInternet ? 'Checking connection...' : internetStatus?.status || 'Unknown'}
                      </p>
                      {internetStatus?.latency_ms && (
                        <p className="text-xs text-muted-foreground">
                          Latency: {internetStatus.latency_ms}ms
                        </p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={checkInternet}
                    disabled={checkingInternet}
                    className="px-3 py-1.5 text-xs font-semibold text-foreground bg-background border border-border rounded hover:bg-muted transition-colors disabled:opacity-50"
                  >
                    Recheck
                  </button>
                </div>
              </div>
            </div>

            {/* Model Settings */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Model Configuration</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Model
                  </label>
                  <input
                    type="text"
                    value={settings.model}
                    disabled
                    className="w-full px-3 py-2 rounded-lg border border-border bg-muted/50 text-muted-foreground text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Temperature: {settings.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                    className="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>Precise</span>
                    <span>Creative</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={settings.max_tokens}
                      onChange={(e) => setSettings({ ...settings, max_tokens: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:ring-2 focus:ring-ring focus:border-input outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Context Size
                    </label>
                    <input
                      type="number"
                      value={settings.context_size}
                      disabled
                      className="w-full px-3 py-2 rounded-lg border border-border bg-muted/50 text-muted-foreground text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
            {/* Memory / Stats */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">System Memory (Cortex)</h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="p-4 rounded-xl border border-border bg-muted/20 flex flex-col items-center justify-center text-center">
                  <span className="text-2xl font-bold text-foreground">{profileStats?.stats?.total_conversations || conversationCount}</span>
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground mt-1 font-semibold">Chats</span>
                </div>
                <div className="p-4 rounded-xl border border-border bg-muted/20 flex flex-col items-center justify-center text-center">
                  <span className="text-2xl font-bold text-foreground">{profileStats?.stats?.total_messages || 0}</span>
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground mt-1 font-semibold">Messages</span>
                </div>
                <div className="p-4 rounded-xl border border-border bg-muted/20 flex flex-col items-center justify-center text-center">
                  <span className="text-2xl font-bold text-foreground">{profileStats?.stats?.documents_indexed || 0}</span>
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground mt-1 font-semibold">Documents</span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-card border-t border-border px-6 py-4 flex items-center justify-between rounded-b-xl">
            <p className="text-xs text-muted-foreground">
              Changes apply to new conversations
            </p>
            <div className="flex gap-2">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-semibold text-foreground hover:bg-muted rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saveStatus === 'saving'}
                className="px-4 py-2 text-sm font-semibold bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2 shadow-sm"
              >
                {saveStatus === 'saving' ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Saving...
                  </>
                ) : saveStatus === 'saved' ? (
                  <>
                    <Save size={16} />
                    Saved!
                  </>
                ) : (
                  <>
                    <Save size={16} />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence >
  )
}
