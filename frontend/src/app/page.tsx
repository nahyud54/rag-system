"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import ChatInterface from "@/components/ChatInterface";
import { getLLMStatus } from "@/lib/api";
import type { LLMStatus } from "@/lib/types";

export default function Home() {
  const [llm, setLlm] = useState<LLMStatus | null>(null);

  useEffect(() => {
    getLLMStatus()
      .then(setLlm)
      .catch(() => setLlm({ available: false, base_url: "", current_model: "", models: [] }));
  }, []);

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <Sidebar />

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top status bar */}
        <div className="flex items-center gap-3 px-6 py-2 bg-bg-surface border-b border-border text-xs">
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                llm?.available ? "bg-green-400" : "bg-red-400"
              }`}
            />
            <span className="text-muted">
              Ollama: {llm?.available ? llm.current_model : "offline"}
            </span>
          </div>
          {llm?.available && llm.models.length > 1 && (
            <span className="text-muted">·</span>
          )}
          {llm?.available && llm.models.length > 0 && (
            <span className="text-muted">{llm.models.length} models</span>
          )}
          <div className="ml-auto text-muted">
            RAG System v1.0 · Deep Learning Course
          </div>
        </div>

        {/* Chat */}
        <div className="flex-1 min-h-0">
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}
