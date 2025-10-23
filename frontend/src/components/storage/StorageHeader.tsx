'use client';

import React from "react";
import { MdOutlineAddCircle } from "react-icons/md";

const StorageHeader: React.FC = () => {
    return (
        <header className="flex flex-row items-center w-full justify-between">
            <div className="flex flex-row items-center gap-1">
                <img src='https://www.shutterstock.com/image-photo/portrait-beautiful-tall-elegant-young-600nw-1267238698.jpg' className="object-cover w-12 rounded-full h-12" />
                <div className="flex flex-row items-center gap-2 bg-additional-bg p-1 rounded-2xl">
                    <img src='https://ton.org/download/ton_symbol.png' className="object-cover w-4 h-4 rounded-full" />
                    <p className="text-primary-text text-xs">1.03 TON</p>
                    <MdOutlineAddCircle className="text-white text-base" />
                </div>
            </div>
            <div className="flex flex-row items-center bg-ton rounded-2xl py-1 px-2 gap-1">
                <img src='https://ton.app/assets/images/what-is-ton/ton-logo.png' className="object-cover w-3 rounded-full" />
                <p className="text-white text-sm">Connect Wallet</p>
            </div>
        </header>
    )
}

export default StorageHeader;