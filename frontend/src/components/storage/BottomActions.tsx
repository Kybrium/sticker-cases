"use client";

import React, { useEffect, useRef, useState } from "react";
import clsx from "clsx";

interface BottomActionsProps {
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

const BottomActions: React.FC<BottomActionsProps> = ({ open, onClose, children }) => {
    const sheetRef = useRef<HTMLDivElement | null>(null);
    const startY = useRef<number | null>(null);
    const [translateY, setTranslateY] = useState(0);

    // close on click outside
    const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
        // if user clicked directly on overlay (not on content)
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    // touch drag
    const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
        startY.current = e.touches[0].clientY;
    };

    const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
        if (startY.current === null) return;
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY.current;
        // only drag down
        if (diff > 0) {
            setTranslateY(diff);
        }
    };

    const handleTouchEnd = () => {
        if (translateY > 80) {
            onClose();
        }
        setTranslateY(0);
        startY.current = null;
    };

    return (
        <>
            {/* overlay */}
            <div
                onClick={handleOverlayClick}
                className={clsx(
                    "fixed inset-0 z-40 bg-black/40 transition-opacity duration-200",
                    open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
                )}
            />

            {/* sheet */}
            <div
                ref={sheetRef}
                className={clsx(
                    "fixed inset-x-0 bottom-0 z-50 rounded-t-2xl bg-background px-4 pb-8 pt-3 shadow-2xl transition-transform duration-200",
                    open ? "translate-y-0" : "translate-y-full"
                )}
                style={{
                    transform: open
                        ? `translateY(${translateY}px)`
                        : "translateY(100%)",
                }}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
            >
                {/* drag handle */}
                <div className="mx-auto mb-4 h-1.5 w-14 rounded-full bg-zinc-500/50" />
                {children}
            </div>
        </>
    );
};

export default BottomActions;