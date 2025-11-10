import { motion } from 'framer-motion'
import { Terminal, FileText, Globe, Zap, Brain, Code, PenTool, LayoutTemplate } from 'lucide-react'
import { useEffect, useState } from 'react'

// Capability Card
function CapabilityCard({ icon: Icon, title, desc, prompt, onClick }: {
    icon: any,
    title: string,
    desc: string,
    prompt: string,
    onClick: (prompt: string) => void
}) {
    return (
        <motion.button
            whileHover={{ y: -2, boxShadow: "0 10px 30px -10px rgba(0,0,0,0.1)" }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onClick(prompt)}
            className="p-4 text-left flex flex-col items-start h-full border border-border/50 bg-background/50 hover:bg-background hover:border-border transition-all rounded-2xl group shadow-sm"
        >
            <div className="w-9 h-9 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-3 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-300">
                <Icon size={16} className="text-foreground group-hover:text-white" />
            </div>
            <h3 className="text-[13px] font-semibold text-foreground mb-0.5">{title}</h3>
            <p className="text-[11px] text-muted-foreground/80 font-medium leading-normal">{desc}</p>
        </motion.button>
    )
}

interface WelcomeScreenProps {
    onCapabilityClick: (prompt: string) => void
}

export function WelcomeScreen({ onCapabilityClick }: WelcomeScreenProps) {
    const [greeting, setGreeting] = useState('Good Day')

    useEffect(() => {
        const hour = new Date().getHours()
        if (hour < 12) setGreeting('Good Morning')
        else if (hour < 18) setGreeting('Good Afternoon')
        else setGreeting('Good Evening')
    }, [])

    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-16rem)] space-y-10 w-full">

            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="relative flex flex-col items-center text-center max-w-lg"
            >

                <div className="w-16 h-16 rounded-2xl bg-zinc-900 dark:bg-zinc-100 flex items-center justify-center mb-6 shadow-2xl shadow-zinc-500/20">
                    <Brain size={32} className="text-white dark:text-zinc-900" strokeWidth={2.5} />
                </div>

                <h1 className="text-3xl font-display font-bold text-foreground tracking-tight mb-3">
                    {greeting}, User.
                </h1>
                <p className="text-muted-foreground text-[15px] leading-relaxed max-w-sm">
                    I'm Aether, your proactive intelligence. <br />
                    Ready to accelerate your workflow.
                </p>
            </motion.div>

            {/* Capability Cards */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
                className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-3xl px-6"
            >
                <CapabilityCard
                    icon={Code}
                    title="Code Expert"
                    desc="Architect systems"
                    prompt="Code a "
                    onClick={onCapabilityClick}
                />
                <CapabilityCard
                    icon={FileText}
                    title="Draft"
                    desc="Documents & emails"
                    prompt="Draft a proposal for "
                    onClick={onCapabilityClick}
                />
                <CapabilityCard
                    icon={Globe}
                    title="Research"
                    desc="Deep web synthesis"
                    prompt="Research the latest "
                    onClick={onCapabilityClick}
                />
                <CapabilityCard
                    icon={LayoutTemplate}
                    title="Design"
                    desc="UI/UX Concepts"
                    prompt="Design a UI for "
                    onClick={onCapabilityClick}
                />
            </motion.div>
        </div>
    )
}
