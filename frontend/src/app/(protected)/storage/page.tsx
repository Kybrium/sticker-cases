'use client';

import SearchBar from "@/components/storage/SearchBar";
import StorageHeader from "@/components/storage/StorageHeader";
import React from "react";

const Storage: React.FC = () => {
    return (
        <div className="min-h-screen bg-background px-4 py-2">
            <StorageHeader />

            <main className="mt-8 space-y-4">
                <div className="flex flex-row items-center justify-center w-full bg-second-background p-1 rounded-xl">
                    <button className="bg-btn-stickers font-semibold text-white p-1 text-sm rounded-2xl w-full">My stickers <span className="bg-btn-stickers-details rounded-full p-1 text-xs">17</span></button>
                    <button className="bg-second-background font-semibold text-white p-1 text-sm rounded-2xl w-full">Not Games <span className="bg-third-background rounded-full p-1 text-xs">0</span></button>
                </div>
                <SearchBar />
            </main>
        </div>
    )
}

export default Storage;