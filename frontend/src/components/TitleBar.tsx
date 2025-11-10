
import React from 'react';
import WindowControls from './WindowControls';

const TitleBar: React.FC = () => {
    return (
        <div className="h-8 w-full flex items-center justify-between bg-transparent z-50 select-none title-drag-region">
            {/* Left side (App Name / Icon could go here) - Draggable */}
            <div className="flex-1 h-full" style={{ WebkitAppRegion: 'drag' } as any} />

            {/* Right side - Window Controls - Non-draggable */}
            <div className="flex-shrink-0" style={{ WebkitAppRegion: 'no-drag' } as any}>
                <WindowControls />
            </div>
        </div>
    );
};

export default TitleBar;
