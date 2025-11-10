
import React from 'react';
import { Minus, Square, X } from 'lucide-react';

const WindowControls: React.FC = () => {
    // Secure Electron Bridge
    const electron = window.electron;

    const handleMinimize = () => electron?.minimize();
    const handleMaximize = () => electron?.maximize();
    const handleClose = () => electron?.close();

    // If not running in Electron (or bridge missing), hide controls
    if (!electron) return null;

    return (
        <div className="flex items-center space-x-0 h-full p-0 bg-transparent" style={{ WebkitAppRegion: 'no-drag' } as any}>
            <button
                onClick={handleMinimize}
                className="p-3 hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                title="Minimize"
            >
                <Minus size={14} />
            </button>
            <button
                onClick={handleMaximize}
                className="p-3 hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                title="Maximize"
            >
                <Square size={12} />
            </button>
            <button
                onClick={handleClose}
                className="p-3 hover:bg-[#e81123] hover:text-white transition-colors text-muted-foreground"
                title="Close"
            >
                <X size={14} />
            </button>
        </div>
    );
};

export default WindowControls;
