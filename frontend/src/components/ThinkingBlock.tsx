
import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Brain } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ThinkingBlockProps {
    content: string;
}

const ThinkingBlock: React.FC<ThinkingBlockProps> = ({ content }) => {
    const [isOpen, setIsOpen] = useState(false);

    // If content is empty, don't render anything
    if (!content || !content.trim()) return null;

    return (
        <div className="mb-4 w-full">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-primary hover:text-primary/80 transition-colors mb-2 select-none"
            >
                <span className="p-1 rounded-md bg-primary/10 text-primary">
                    <Brain size={14} />
                </span>
                <span>Aether's Thought Process</span>
                {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="p-4 rounded-xl bg-zinc-100/50 dark:bg-zinc-900/50 backdrop-blur-md border border-border/50 text-sm text-muted-foreground font-mono leading-relaxed whitespace-pre-wrap shadow-sm">
                            {content}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ThinkingBlock;
