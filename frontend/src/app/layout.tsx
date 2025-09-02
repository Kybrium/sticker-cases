import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sticker Cases",
  description: "Open and win some stickers!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}