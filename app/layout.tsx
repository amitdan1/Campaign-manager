import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/layout/ChatPanel";
import { ToastProvider } from "@/components/ui/Toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Marketing Agent | Ofir Assulin",
  description: "Performance Marketing System — Autonomous Agent Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl">
      <body
        className={`${inter.className} bg-bg text-text-primary min-h-screen flex`}
      >
        <ToastProvider>
          <Sidebar />
          <div className="mr-sidebar flex-1 flex flex-col min-h-screen max-md:mr-[60px]">
            <main className="flex-1 p-8 max-w-[1400px] w-full max-md:p-5">
              {children}
            </main>
          </div>
          <ChatPanel />
        </ToastProvider>
      </body>
    </html>
  );
}
