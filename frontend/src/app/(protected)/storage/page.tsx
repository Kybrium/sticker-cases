'use client';

import BottomActions from "@/components/storage/BottomActions";
import SearchBar from "@/components/storage/SearchBar";
import Stickers from "@/components/storage/Stickers";
import StorageHeader from "@/components/storage/StorageHeader";
import React, { useEffect, useState } from "react";
import { AiOutlineShoppingCart } from "react-icons/ai";
import { FaRegArrowAltCircleRight } from "react-icons/fa";

const Storage: React.FC = () => {

    const data: any[] = [];
    for (let i = 0; i < 50; i++) {
        data.push({
            id: i,
            pack_name: "Extra Eyes",
            collection_name: "DOGS OG",
            contributor: "Sticker Pack",
            floor_price: 3.413,
            image_url: "https://cdn.stickerdom.store/1/p/4/1.png?v=3",
            cases: [
                {
                    chance: 0.9457013574660634,
                    case_name: "Sigma Case"
                }
            ]
        });
    }

    const [isActionsMenuOpen, setIsActionsMenuOpen] = useState<boolean>(false);
    const [currentlySelectedId, setCurrentlySelectedId] = useState<number | null>(null);

    const handleOpenMenu: (v: number) => void = (v) => {
        setCurrentlySelectedId(v);
        setIsActionsMenuOpen(true);
    }

    useEffect(() => {
        if (isActionsMenuOpen) {
            const originalStyle = window.getComputedStyle(document.body).overflow;
            document.body.style.overflow = "hidden";
            return () => {
                document.body.style.overflow = originalStyle;
            };
        }
    }, [isActionsMenuOpen]);

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

            <Stickers data={data} handleOpenMenu={handleOpenMenu} />

            <BottomActions open={isActionsMenuOpen} onClose={() => setIsActionsMenuOpen(false)}>
                <button className="flex items-center gap-3 py-3 text-primary-text w-full text-left"><AiOutlineShoppingCart className="text-blue-500" /> <span>Sell Stickers</span></button>
                <button className="flex items-center gap-3 py-3 text-primary-text w-full text-left"><FaRegArrowAltCircleRight className="text-blue-500" /> <span>Transfer stickers</span></button>
            </BottomActions>

        </div>
    )
}

export default Storage;