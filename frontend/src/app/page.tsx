import React from "react";
import TelegramUserCard from "@/components/auth/TelegramUserCard";

export default function Home() {
  return (
    <main className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <h1>Landing</h1>
      <TelegramUserCard />
    </main>
  );
}