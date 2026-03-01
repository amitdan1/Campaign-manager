"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { clsx } from "clsx";

interface Message {
  role: "user" | "agent";
  agentName?: string;
  content: string;
}

export function ChatPanel() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "agent",
      agentName: "Orchestrator",
      content: "שלום! אני מנהל הסוכנים. איך אפשר לעזור?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async () => {
    const msg = input.trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();
      if (data.success) {
        setMessages((prev) => [
          ...prev,
          {
            role: "agent",
            agentName: data.agent || "Orchestrator",
            content: data.response,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "agent",
            agentName: "System",
            content: `שגיאה: ${data.error || "נסה שוב"}`,
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          agentName: "System",
          content: "לא ניתן להתחבר לשרת",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 left-6 w-[52px] h-[52px] bg-accent text-white rounded-full shadow-card-md z-[200] flex items-center justify-center text-xl hover:scale-[1.08] transition-transform cursor-pointer border-none"
        title="צ'אט עם הסוכנים"
      >
        <i className="fas fa-comments" />
      </button>

      {/* Panel */}
      <div
        className={clsx(
          "fixed left-0 top-0 bottom-0 w-chat max-md:w-full bg-card-bg border-r border-border shadow-[4px_0_20px_rgba(0,0,0,.08)] z-[150] flex flex-col transition-transform duration-300",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-border flex justify-between items-center font-semibold text-[.95rem]">
          <span>
            <i className="fas fa-robot ml-2" />
            צ'אט עם הסוכנים
          </span>
          <button
            onClick={() => setOpen(false)}
            className="text-text-secondary text-2xl font-bold cursor-pointer leading-none bg-transparent border-none hover:text-text-primary"
          >
            &times;
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
          {messages.map((m, i) => (
            <div
              key={i}
              className={clsx(
                "max-w-[85%] px-3 py-2.5 rounded-sm text-[.85rem] leading-relaxed",
                m.role === "user"
                  ? "self-end bg-accent text-white"
                  : "self-start bg-bg text-text-primary"
              )}
            >
              {m.role === "agent" && m.agentName && (
                <div className="text-[.7rem] font-semibold text-accent mb-0.5">
                  {m.agentName}
                </div>
              )}
              {m.content}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t border-border flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="שלח הודעה..."
            className="flex-1 px-3 py-2 border border-border rounded-sm text-[.85rem] bg-bg focus:outline-none focus:border-accent"
            disabled={loading}
          />
          <button
            onClick={send}
            disabled={loading}
            className="bg-accent text-white border-none rounded-sm px-3 py-2 cursor-pointer text-[.85rem] disabled:opacity-50"
          >
            <i className="fas fa-paper-plane" />
          </button>
        </div>
      </div>
    </>
  );
}
