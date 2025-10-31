'use client'

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { FaBoxArchive } from "react-icons/fa6";
import { SlPresent } from "react-icons/sl";
import { TiHome } from "react-icons/ti";
import { CgProfile } from "react-icons/cg";

const NavBar: React.FC = () => {

    const pathname = usePathname();

    const buttons = [
    { icon: <FaBoxArchive />, label: "Storage", href: "/storage" },
    { icon: <SlPresent />, label: "Cases", href: "/cases" },
    { icon: <TiHome className="scale-[1.3]" />, label: "Home", href: "/home" },
    { icon: <CgProfile />, label: "Profile", href: "/profile" },
    ];

    return(
        <div className="w-full bg-second-background text-secondary-text rounded-2xl flex justify-around py-3 px-4 text-2xl">
            {buttons.map(({ icon, label, href }) => {
                const isActive = pathname === href;
                return (
                <Link
                    key={href}
                    href={href}
                    className={`flex flex-col items-center justify-center transition-colors ${
                    isActive ? "text-btn-active-navbar" : "text-secondary-text"
                    }`}
                >
                    {icon}
                    <span className="text-xs mt-1">{label}</span>
                </Link>
                );
            })}
        </div>
    );
};

export default NavBar;