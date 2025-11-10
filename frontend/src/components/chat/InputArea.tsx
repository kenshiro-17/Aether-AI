import React, { useRef, useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Paperclip, Send, Brain, Wifi, WifiOff, Globe, Mic, MicOff, Monitor } from 'lucide-react'

// Browser Speech Recognition Helper


interface InputAreaProps {
    input: string
    setInput: React.Dispatch<React.SetStateAction<string>>
    onSubmit: () => void
    disabled?: boolean
    isThinkingEnabled: boolean
    setIsThinkingEnabled: (v: boolean) => void
    isSearchEnabled: boolean
    setIsSearchEnabled: (v: boolean) => void
    webSearchStatus: 'connected' | 'disconnected' | null
    onFileSelect: (file: File) => void
}

export function InputArea({
    input,
    setInput,
    onSubmit,
    disabled,
    isThinkingEnabled,
    setIsThinkingEnabled,
    isSearchEnabled,
    setIsSearchEnabled,
    webSearchStatus,
    onFileSelect
}: InputAreaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const [isDragging, setIsDragging] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const [isCapturing, setIsCapturing] = useState(false)

    // Audio Context Refs for raw WAV recording
    const audioContextRef = useRef<AudioContext | null>(null)
    const processorRef = useRef<ScriptProcessorNode | null>(null)
    const mediaStreamRef = useRef<MediaStream | null>(null)
    const audioDataRef = useRef<Float32Array[]>([])

    const handleScreenCapture = async () => {
        setIsCapturing(true);
        try {
            // Get sources from main process
            const sources = await (window as any).electron.getSources();
            // Prefer entire screen
            const screenSource = sources.find((s: any) => s.name === 'Entire Screen' || s.name === 'Screen 1') || sources[0];

            if (!screenSource) throw new Error("No screen source found");

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: false,
                video: {
                    mandatory: {
                        chromeMediaSource: 'desktop',
                        chromeMediaSourceId: screenSource.id,
                        minWidth: 1280,
                        maxWidth: 1920,
                        minHeight: 720,
                        maxHeight: 1080
                    }
                } as any
            });

            // Capture single frame
            const track = stream.getVideoTracks()[0];
            const imageCapture = new (window as any).ImageCapture(track);
            const bitmap = await imageCapture.grabFrame();

            // Convert to blob
            const canvas = document.createElement('canvas');
            canvas.width = bitmap.width;
            canvas.height = bitmap.height;
            const context = canvas.getContext('2d');
            context?.drawImage(bitmap, 0, 0);

            canvas.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], "screenshot.png", { type: "image/png" });
                    onFileSelect(file);
                }

                // Stop stream
                stream.getTracks().forEach(t => t.stop());
                setIsCapturing(false);
            }, 'image/png');

        } catch (e) {
            console.error("Screen capture failed:", e);
            alert("Failed to capture screen.");
            setIsCapturing(false);
        }
    };

    const toggleListening = async () => {
        if (isListening) {
            stopRecording()
        } else {
            await startRecording()
        }
    }

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaStreamRef.current = stream

            // 16kHz sample rate is standard for STT
            const context = new AudioContext({ sampleRate: 16000 })
            audioContextRef.current = context

            const source = context.createMediaStreamSource(stream)
            const processor = context.createScriptProcessor(4096, 1, 1)
            processorRef.current = processor

            audioDataRef.current = []

            processor.onaudioprocess = (e) => {
                const input = e.inputBuffer.getChannelData(0)
                // Clone data because the buffer is reused
                audioDataRef.current.push(new Float32Array(input))
            }

            source.connect(processor)
            processor.connect(context.destination)

            setIsListening(true)
        } catch (e) {
            console.error("Mic Error:", e)
            alert("Could not start recording. Check permissions.")
        }
    }

    const stopRecording = async () => {
        if (processorRef.current && audioContextRef.current) {
            processorRef.current.disconnect()
            audioContextRef.current.close()
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop())
        }

        setIsListening(false)
        await processAudio()
    }

    const processAudio = async () => {
        if (audioDataRef.current.length === 0) return

        // Flatten chunks
        const length = audioDataRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
        const result = new Float32Array(length)
        let offset = 0
        for (const chunk of audioDataRef.current) {
            result.set(chunk, offset)
            offset += chunk.length
        }

        // Convert to WAV Blob
        const wavBlob = encodeWAV(result, 16000)

        // Send to Backend
        const formData = new FormData()
        formData.append('file', wavBlob, 'recording.wav')

        setInput(prev => prev + (prev ? ' ' : '') + "[Transcribing...]")

        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/stt`, {
                method: 'POST',
                body: formData
            })

            if (!res.ok) throw new Error("Transcription server error")

            const data = await res.json()
            if (data.text) {
                setInput(prev => prev.replace("[Transcribing...]", "").trim() + " " + data.text)
            } else {
                setInput(prev => prev.replace("[Transcribing...]", "").trim())
            }
        } catch (e) {
            console.error(e)
            setInput(prev => prev.replace("[Transcribing...]", "[No Speech Detected]"))
        }
    }

    // Helper: Float32 PCM -> WAV Blob
    const encodeWAV = (samples: Float32Array, sampleRate: number) => {
        const buffer = new ArrayBuffer(44 + samples.length * 2)
        const view = new DataView(buffer)

        // RIFF chunk descriptor
        writeString(view, 0, 'RIFF')
        view.setUint32(4, 36 + samples.length * 2, true)
        writeString(view, 8, 'WAVE')
        // fmt sub-chunk
        writeString(view, 12, 'fmt ')
        view.setUint32(16, 16, true)
        view.setUint16(20, 1, true)
        view.setUint16(22, 1, true) // Mono
        view.setUint32(24, sampleRate, true)
        view.setUint32(28, sampleRate * 2, true)
        view.setUint16(32, 2, true)
        view.setUint16(34, 16, true)
        // data sub-chunk
        writeString(view, 36, 'data')
        view.setUint32(40, samples.length * 2, true)

        // Write PCM samples
        floatTo16BitPCM(view, 44, samples)

        return new Blob([view], { type: 'audio/wav' })
    }

    const writeString = (view: DataView, offset: number, string: string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i))
        }
    }

    const floatTo16BitPCM = (output: DataView, offset: number, input: Float32Array) => {
        for (let i = 0; i < input.length; i++, offset += 2) {
            const s = Math.max(-1, Math.min(1, input[i]))
            output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
        }
    }

    // Auto-resize
    React.useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
        }
    }, [input])

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        const files = e.dataTransfer.files
        if (files && files.length > 0) {
            onFileSelect(files[0])
        }
    }

    return (
        <div className="absolute bottom-0 left-0 right-0 px-4 pb-6 pt-10 flex justify-center z-50 pointer-events-none bg-gradient-to-t from-background via-background/80 to-transparent">
            <div className="w-full max-w-3xl pointer-events-auto flex flex-col gap-3">

                {/* Helper toggles - Floating above input */}
                <div className="flex justify-center gap-2">
                    <button
                        onClick={() => setIsThinkingEnabled(!isThinkingEnabled)}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium transition-all shadow-sm border ${isThinkingEnabled
                            ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 border-transparent'
                            : 'bg-background text-muted-foreground border-border hover:bg-muted'
                            }`}
                    >
                        <Brain size={12} />
                        {isThinkingEnabled ? 'Thinking On' : 'Reasoning'}
                    </button>
                    <button
                        onClick={() => setIsSearchEnabled(!isSearchEnabled)}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium transition-all shadow-sm border ${isSearchEnabled
                            ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                            : 'bg-background text-muted-foreground border-border hover:bg-muted'
                            }`}
                    >
                        {webSearchStatus === 'connected' ? (
                            <Wifi size={12} className="text-emerald-500" />
                        ) : (
                            <Globe size={12} />
                        )}
                        Web Search
                    </button>
                </div>


                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
            relative backdrop-blur-xl bg-background/60 dark:bg-zinc-900/60 border rounded-[26px] shadow-2xl transition-all duration-200
            ${isDragging ? 'border-primary ring-2 ring-primary/20' : 'border-zinc-200/50 dark:border-white/10'}
            focus-within:border-zinc-300 dark:focus-within:border-white/20
            focus-within:ring-1 focus-within:ring-white/5
          `}
                >
                    {/* File Input */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files?.[0]) onFileSelect(e.target.files[0])
                            e.target.value = ''
                        }}
                    />

                    <div className="flex items-end p-2 gap-2">
                        {/* Action Bar (Left) */}
                        <div className="flex items-center gap-1 p-1 rounded-full bg-zinc-100/50 dark:bg-white/5 border border-white/5">
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="p-2 rounded-full text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-white/10 transition-colors"
                                title="Attach file"
                            >
                                <Paperclip size={16} strokeWidth={2.5} />
                            </button>

                            <button
                                onClick={handleScreenCapture}
                                disabled={isCapturing}
                                className={`p-2 rounded-full text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-white/10 transition-colors ${isCapturing ? 'animate-pulse text-primary' : ''}`}
                                title="Capture Screen"
                            >
                                <Monitor size={16} strokeWidth={2.5} />
                            </button>

                            <button
                                onClick={toggleListening}
                                className={`p-2 rounded-full transition-colors ${isListening
                                    ? 'text-red-500 bg-red-500/10 animate-pulse'
                                    : 'text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-white/10'}`}
                                title={isListening ? "Stop listening" : "Voice Input"}
                            >
                                {isListening ? <MicOff size={16} strokeWidth={2.5} /> : <Mic size={16} strokeWidth={2.5} />}
                            </button>
                        </div>

                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Message Aether..."
                            rows={1}
                            className="flex-1 bg-transparent border-0 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 resize-none py-3 px-2 focus:outline-none max-h-[200px] text-[15px] leading-6 font-medium scrollbar-none"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    if (input.trim()) onSubmit()
                                }
                            }}
                        />

                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            disabled={!input.trim() || disabled}
                            onClick={onSubmit}
                            className={`p-2.5 rounded-full transition-all mb-0.5 ${input.trim()
                                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:opacity-90'
                                : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-600'
                                }`}
                        >
                            <Send size={16} strokeWidth={2.5} />
                        </motion.button>
                    </div>
                </div>

                <div className="text-center">
                    <span className="text-[10px] text-zinc-400 font-medium">Auto-Learning Active • Personal AI</span>
                </div>

            </div>
        </div>
    )
}

