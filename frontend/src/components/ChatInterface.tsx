"use client";

import { useEffect, useRef, useState } from "react";
import { useChatStore } from "@/lib/store";
import { clearHistory, createChatSocket, sendMessage } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import type { Source } from "@/lib/types";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [useStream, setUseStream] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const { messages, sessionId, isLoading, setSessionId, addMessage, updateMessage, appendToken, clearMessages, setLoading } =
    useChatStore();

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submit = async () => {
    const query = input.trim();
    if (!query || isLoading) return;
    setInput("");
    setLoading(true);

    addMessage({ role: "user", content: query });

    if (useStream) {
      await submitStreaming(query);
    } else {
      await submitHTTP(query);
    }

    setLoading(false);
  };

  const submitHTTP = async (query: string) => {
    const assistantId = addMessage({ role: "assistant", content: "", streaming: true });
    try {
      const resp = await sendMessage(query, sessionId);
      if (!sessionId) setSessionId(resp.session_id);
      updateMessage(assistantId, {
        content: resp.answer,
        sources: resp.sources,
        streaming: false,
      });
    } catch (e: unknown) {
      updateMessage(assistantId, {
        content: "Lỗi kết nối tới server. Hãy kiểm tra backend đang chạy.",
        streaming: false,
      });
    }
  };

  const submitStreaming = async (query: string) => {
    const sid = sessionId || Math.random().toString(36).slice(2);
    if (!sessionId) setSessionId(sid);

    const assistantId = addMessage({ role: "assistant", content: "", streaming: true });

    return new Promise<void>((resolve) => {
      const ws = createChatSocket(sid);
      socketRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({ query }));
      };

      ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data);
        if (data.type === "token") {
          appendToken(assistantId, data.token);
        } else if (data.type === "done") {
          updateMessage(assistantId, {
            content: data.answer,
            sources: data.sources as Source[],
            streaming: false,
          });
          ws.close();
          resolve();
        } else if (data.type === "error") {
          updateMessage(assistantId, {
            content: `Lỗi: ${data.message}`,
            streaming: false,
          });
          ws.close();
          resolve();
        }
      };

      ws.onerror = () => {
        // Fallback to HTTP if WebSocket fails
        updateMessage(assistantId, {
          content: "",
          streaming: true,
        });
        submitHTTP(query).then(resolve);
        ws.close();
      };
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const handleClear = async () => {
    if (sessionId) await clearHistory(sessionId).catch(() => {});
    clearMessages();
    setSessionId("");
  };

  const suggestions = [
    "Gradient Descent là gì?",
    "Giải thích Backpropagation",
    "CNN khác RNN như thế nào?",
    "Attention mechanism hoạt động ra sao?",
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-border bg-bg-surface">
        <div>
          <h2 className="text-sm font-semibold text-white">Chat với AI</h2>
          {sessionId && (
            <p className="text-xs text-muted font-mono mt-0.5">
              Session: {sessionId.slice(0, 8)}...
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {/* Stream toggle */}
          <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer">
            <div
              onClick={() => setUseStream((v) => !v)}
              className={`w-8 h-4 rounded-full transition-colors relative cursor-pointer ${
                useStream ? "bg-accent" : "bg-bg-hover"
              }`}
            >
              <div
                className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${
                  useStream ? "translate-x-4" : "translate-x-0.5"
                }`}
              />
            </div>
            Stream
          </label>

          {messages.length > 0 && (
            <button
              onClick={handleClear}
              className="text-xs text-muted hover:text-red-400 transition-colors px-2 py-1 rounded hover:bg-red-900/20"
            >
              Xóa chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="text-5xl mb-4">🧠</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Hỏi về Deep Learning
            </h3>
            <p className="text-sm text-muted mb-8 max-w-md">
              Tôi được index từ 17 slides bài giảng Deep Learning. Hỏi bất cứ điều gì về neural networks, CNN, RNN, Transformers...
            </p>
            <div className="grid grid-cols-2 gap-2 w-full max-w-lg">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setInput(s);
                    inputRef.current?.focus();
                  }}
                  className="px-3 py-2.5 text-xs text-left bg-bg-card hover:bg-bg-hover
                             border border-border hover:border-accent/50 rounded-xl
                             transition-all duration-150 text-slate-300"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-border bg-bg-surface">
        <div className="flex gap-3 items-end">
          <div className="flex-1 bg-bg-card border border-border rounded-xl focus-within:border-accent/60 transition-colors">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Hỏi về nội dung bài giảng... (Enter để gửi, Shift+Enter xuống dòng)"
              rows={1}
              disabled={isLoading}
              className="w-full bg-transparent px-4 py-3 text-sm text-slate-200 placeholder-muted
                         resize-none outline-none max-h-32 overflow-y-auto"
              style={{ minHeight: "44px" }}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = Math.min(el.scrollHeight, 128) + "px";
              }}
            />
          </div>
          <button
            onClick={submit}
            disabled={!input.trim() || isLoading}
            className="w-11 h-11 bg-accent hover:bg-accent-hover disabled:opacity-40
                       disabled:cursor-not-allowed rounded-xl flex items-center justify-center
                       transition-colors duration-150 shrink-0"
          >
            {isLoading ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22 11 13 2 9l20-7z" />
              </svg>
            )}
          </button>
        </div>
        <p className="text-xs text-muted mt-2 text-center">
          Powered by Ollama · RAG · Deep Learning Materials
        </p>
      </div>
    </div>
  );
}
