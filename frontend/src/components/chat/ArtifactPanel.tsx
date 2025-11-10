import { useState, useEffect } from 'react'
import { Check, Copy, X, Code, Eye } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { motion } from 'framer-motion'

interface ArtifactPanelProps {
    code: string
    language: string
    onClose: () => void
    isDarkMode: boolean
}

export function ArtifactPanel({ code, language, onClose, isDarkMode }: ArtifactPanelProps) {
    const [activeTab, setActiveTab] = useState<'code' | 'preview'>('code')
    const [copied, setCopied] = useState(false)

    // Reset to code view when content changes
    useEffect(() => {
        setActiveTab('code')
    }, [code])

    const copyToClipboard = () => {
        navigator.clipboard.writeText(code)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const canPreview = ['html', 'svg', 'xml'].includes(language.toLowerCase())

    return (
        <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: '45%', opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="h-full border-l border-border bg-card shadow-2xl z-20 flex flex-col flex-shrink-0"
        >
            {/* Header */}
            <div className="h-14 flex items-center justify-between px-4 border-b border-border bg-muted/30">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3">
                        <div className="p-1.5 bg-primary/10 rounded-md text-primary">
                            {activeTab === 'code' ? <Code size={16} /> : <Eye size={16} />}
                        </div>
                        <div>
                            <span className="text-sm font-semibold text-foreground block">
                                {activeTab === 'code' ? 'Code Source' : 'Live Preview'}
                            </span>
                            <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-wider">{language}</span>
                        </div>
                    </div>

                    {/* Tabs */}
                    {canPreview && (
                        <div className="flex bg-muted/50 p-0.5 rounded-lg border border-border/50 overflow-hidden">
                            <button
                                onClick={() => setActiveTab('code')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'code'
                                        ? 'bg-background shadow-sm text-foreground'
                                        : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                Code
                            </button>
                            <button
                                onClick={() => setActiveTab('preview')}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'preview'
                                        ? 'bg-background shadow-sm text-foreground'
                                        : 'text-muted-foreground hover:text-foreground'
                                    }`}
                            >
                                Preview
                            </button>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-1">
                    <button
                        onClick={copyToClipboard}
                        className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-all"
                        title="Copy code"
                    >
                        {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                    </button>
                    <button
                        onClick={onClose}
                        className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-all"
                    >
                        <X size={16} />
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto bg-background/50 relative group">
                {activeTab === 'code' ? (
                    <div className="absolute inset-0 p-4">
                        <SyntaxHighlighter
                            style={isDarkMode ? oneDark : oneLight}
                            language={language}
                            customStyle={{
                                margin: 0,
                                height: '100%',
                                fontSize: '13px',
                                lineHeight: '1.6',
                                background: 'transparent',
                            }}
                            showLineNumbers={true}
                            lineNumberStyle={{ color: 'rgba(120,120,120,0.4)', minWidth: '2.5em' }}
                        >
                            {code}
                        </SyntaxHighlighter>
                    </div>
                ) : (
                    <div className="w-full h-full bg-white relative">
                        <iframe
                            className="w-full h-full border-none"
                            sandbox="allow-scripts allow-popups allow-modals" // Secure sandbox
                            srcDoc={code}
                            title="Preview"
                        />
                        <div className="absolute top-2 right-2 px-2 py-1 bg-black/10 text-black/50 text-[10px] rounded pointer-events-none">
                            Interactive Preview
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    )
}
