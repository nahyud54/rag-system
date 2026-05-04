"use client";

import { useEffect, useState } from "react";
import { getIndexingStatus, indexRawPptx, resetIndex } from "@/lib/api";
import type { IndexingStatus } from "@/lib/types";

export default function Sidebar() {
  const [status, setStatus] = useState<IndexingStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  const fetchStatus = async () => {
    try {
      const s = await getIndexingStatus();
      setStatus(s);
      if (s.status === "running" || s.status === "queued") {
        setPolling(true);
      } else {
        setPolling(false);
      }
    } catch {
      // backend may not be up yet
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    if (!polling) return;
    const id = setInterval(fetchStatus, 2000);
    return () => clearInterval(id);
  }, [polling]);

  const handleIndex = async () => {
    setLoading(true);
    try {
      await indexRawPptx();
      setPolling(true);
      fetchStatus();
    } catch (e: unknown) {
      alert("Lỗi: " + (e instanceof Error ? e.message : "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Xóa toàn bộ index? Cần chạy lại indexing sau.")) return;
    await resetIndex();
    fetchStatus();
  };

  const statusColor: Record<string, string> = {
    idle: "text-slate-400",
    queued: "text-yellow-400",
    running: "text-blue-400",
    done: "text-green-400",
    error: "text-red-400",
  };

  const docCount = status?.total_documents ?? 0;

  return (
    <aside className="w-72 flex-shrink-0 bg-bg-surface border-r border-border flex flex-col h-full">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <div>
            <h1 className="text-sm font-semibold text-white leading-none">RAG System</h1>
            <p className="text-xs text-muted mt-0.5">AI Study Assistant</p>
          </div>
        </div>
      </div>

      {/* Indexing section */}
      <div className="px-4 py-4 border-b border-border">
        <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Tài Liệu
        </p>

        {/* Stats */}
        <div className="bg-bg-card rounded-lg p-3 mb-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Vectors</span>
            <span className="text-accent font-mono font-semibold">{docCount.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Trạng thái</span>
            <span className={`font-medium ${statusColor[status?.status ?? "idle"]}`}>
              {status?.status === "running" && (
                <span className="inline-block w-2 h-2 rounded-full bg-blue-400 mr-1 animate-pulse" />
              )}
              {status?.status ?? "—"}
            </span>
          </div>
          {status?.last_result && !status.last_result.error && status.status === "done" && (
            <div className="mt-2 pt-2 border-t border-border text-xs text-slate-500">
              {status.last_result.files_processed} files •{" "}
              {status.last_result.chunks_created} chunks
            </div>
          )}
          {status?.last_result?.error && (
            <p className="mt-2 text-xs text-red-400">{status.last_result.error}</p>
          )}
        </div>

        {/* Index button */}
        <button
          onClick={handleIndex}
          disabled={loading || status?.status === "running" || status?.status === "queued"}
          className="w-full py-2 px-3 bg-accent hover:bg-accent-hover disabled:opacity-50
                     disabled:cursor-not-allowed text-white text-sm rounded-lg font-medium
                     transition-colors duration-150 flex items-center justify-center gap-2"
        >
          {loading || status?.status === "running" ? (
            <>
              <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Đang Index...
            </>
          ) : (
            <>⚡ Index raw_pptx/</>
          )}
        </button>
      </div>

      {/* Course list */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Khóa Học
        </p>
        <div className="space-y-1 text-xs text-slate-400">
          {[
            { icon: "1️⃣", label: "Intro to Deep Learning", slides: 4 },
            { icon: "2️⃣", label: "Practical Aspects", slides: 3 },
            { icon: "3️⃣", label: "ML Strategy", slides: 2 },
            { icon: "4️⃣", label: "Convolutional Networks", slides: 4 },
            { icon: "5️⃣", label: "Sequence Models", slides: 4 },
          ].map((c) => (
            <div
              key={c.label}
              className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-bg-hover cursor-default"
            >
              <span>{c.icon}</span>
              <span className="flex-1 truncate">{c.label}</span>
              <span className="text-muted">{c.slides}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border">
        <button
          onClick={handleReset}
          className="w-full py-1.5 px-3 text-xs text-red-400 hover:text-red-300
                     hover:bg-red-900/20 rounded-lg transition-colors"
        >
          🗑 Xóa toàn bộ index
        </button>
      </div>
    </aside>
  );
}
