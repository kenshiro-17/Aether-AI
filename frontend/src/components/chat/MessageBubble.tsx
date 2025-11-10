import React, { useState } from 'react'
import { Brain, Copy, Check, Volume2, StopCircle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark, prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import { motion } from 'framer-motion'
import ThinkingBlock from '@/components/ThinkingBlock'

interface Message {
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
}

interface MessageBubbleProps {
    message: Message
    onOpenArtifact?: (code: string, lang: string) => void
    isDarkMode: boolean
}

export function MessageBubble({ message, isDarkMode }: MessageBubbleProps) {
    const isUser = message.role === 'user'
    const [isSpeaking, setIsSpeaking] = useState(false)

    const [copied, setCopied] = React.useState(false)
    const copyContent = () => {
        navigator.clipboard.writeText(message.content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const displayText = message.role === 'assistant'
        ? message.content.replace(/<thinking>[\s\S]*?(?:<\/thinking>|$)/g, '').trim()
        : message.content

    const toggleSpeech = () => {
        const synth = window.speechSynthesis
        if (!synth) return

        if (isSpeaking) {
            synth.cancel()
            setIsSpeaking(false)
        } else {
            // Cancel any ongoing speech first
            synth.cancel()

            // Strip markdown chars for better reading (basic)
            const cleanText = displayText
                .replace(/[#*`]/g, '') // Remove basic markdown symbols
                .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Keep link text, remove url

            const utterance = new SpeechSynthesisUtterance(cleanText)
            utterance.onend = () => setIsSpeaking(false)
            utterance.onerror = () => setIsSpeaking(false)

            synth.speak(utterance)
            setIsSpeaking(true)
        }
    }

    // Stop speaking when unmounting
    React.useEffect(() => {
        return () => {
            if (isSpeaking) {
                window.speechSynthesis.cancel()
            }
        }
    }, [isSpeaking])

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`group flex gap-6 w-full ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            {/* Assistant Avatar - Clean & Minimal */}
            {!isUser && (
                <div className="flex-shrink-0 mt-1">
                    <div className="w-8 h-8 rounded-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 flex items-center justify-center text-primary shadow-sm">
                        <Brain size={14} strokeWidth={2.5} />
                    </div>
                </div>
            )}

            {/* Message Content */}
            <div className={`relative max-w-[85%] lg:max-w-[75%] ${isUser ? 'order-first' : ''}`}>

                {/* Name Label - Only for AI, User doesn't need it repeatedly */}
                {!isUser && (
                    <div className="flex items-center gap-2 mb-1.5 pl-1">
                        <span className="text-[12px] font-semibold text-foreground">
                            Aether
                        </span>
                        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">AI</span>
                    </div>
                )}

                <div
                    className={`text-base leading-loose ${isUser
                        ? 'bg-zinc-100 dark:bg-zinc-800/80 backdrop-blur-sm text-foreground px-6 py-4 rounded-3xl rounded-tr-sm shadow-sm'
                        : 'text-foreground px-1 py-1' // AI text is cleaner without heavy bubble
                        }`}
                >

                    {/* Render Thought Process if present */}
                    {message.role === 'assistant' && message.content.includes('<thinking>') && (
                        <ThinkingBlock
                            content={(() => {
                                const match = message.content.match(/<thinking>([\s\S]*?)(?:<\/thinking>|$)/);
                                return match ? match[1] : '';
                            })()}
                        />
                    )}

                    <div className={`prose-custom max-w-none ${isUser ? 'text-zinc-800 dark:text-zinc-100 select-text' : ''}`}>
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                p({ children }) {
                                    return <p className={`mb-2 last:mb-0 ${isUser ? 'text-inherit' : 'text-foreground'}`}>{children}</p>
                                },
                                a({ node, className, children, ...props }) {
                                    return (
                                        <a
                                            className={`font-medium underline underline-offset-4 decoration-2 ${isUser ? 'text-white/90 decoration-white/30' : 'text-primary decoration-primary/30 hover:decoration-primary'}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            {...props}
                                        >
                                            {children}
                                        </a>
                                    )
                                },
                                code({ node, className, children, ...props }: any) {
                                    const match = /language-(\w+)/.exec(className || '')
                                    const inline = !match

                                    if (inline) {
                                        return (
                                            <code className={`${isUser ? 'bg-white/20 text-white' : 'bg-muted text-foreground'} px-1.5 py-0.5 rounded text-xs font-mono`} {...props}>
                                                {children}
                                            </code>
                                        )
                                    }

                                    return (
                                        <div className="relative group/code my-4 rounded-xl overflow-hidden border border-border bg-zinc-50 dark:bg-zinc-950/50">
                                            <div className="absolute right-2 top-2 z-10 opacity-0 group-hover/code:opacity-100 transition-opacity flex gap-1">
                                                <button
                                                    onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                                                    className="p-1.5 rounded-md bg-zinc-200 dark:bg-zinc-800 text-foreground backdrop-blur-md transition-colors hover:bg-zinc-300 dark:hover:bg-zinc-700"
                                                    title="Copy Code"
                                                >
                                                    <Copy size={14} />
                                                </button>
                                            </div>
                                            <div className="bg-zinc-100 dark:bg-zinc-900/50 px-4 py-2 border-b border-border flex items-center justify-between">
                                                <span className="text-xs text-muted-foreground font-mono font-medium">{match?.[1] || 'code'}</span>
                                            </div>
                                            <SyntaxHighlighter
                                                style={isDarkMode ? atomDark : prism}
                                                language={match?.[1]}
                                                PreTag="div"
                                                customStyle={{
                                                    margin: 0,
                                                    background: 'transparent',
                                                    padding: '1.5rem',
                                                    fontSize: '0.85rem',
                                                    lineHeight: '1.7',
                                                }}
                                                codeTagProps={{
                                                    style: { background: 'transparent' }
                                                }}
                                            >
                                                {String(children).replace(/\n$/, '')}
                                            </SyntaxHighlighter>
                                        </div>
                                    )
                                }
                            }}
                        >
                            {/* Remove thinking block from display text */}
                            {displayText}
                        </ReactMarkdown>
                    </div>
                </div>

                {/* Helper Actions (Copy, Retry, etc) - appearing on hover */}
                {!isUser && (
                    <div className="absolute -bottom-5 left-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                        <button onClick={copyContent} className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
                            {copied ? <Check size={10} /> : <Copy size={10} />}
                            {copied ? 'Copied' : 'Copy'}
                        </button>
                        <button onClick={toggleSpeech} className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
                            {isSpeaking ? <StopCircle size={10} className="text-red-500" /> : <Volume2 size={10} />}
                            {isSpeaking ? 'Stop' : 'Read'}
                        </button>
                    </div>
                )}

            </div>
        </motion.div>
    )
}
