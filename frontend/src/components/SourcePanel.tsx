"use client";

import { useState } from "react";
import type { Source } from "@/lib/types";

interface Props {
  sources: Source[];
}

export default function SourcePanel({ sources }: Props) {
  const [open, setOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover
                   transition-colors"
      >
        <span>{open ? "▾" : "▸"}</span>
        <span>{sources.length} nguồn tài liệu</span>
      </button>

      {open && (
        <div className="mt-2 grid gap-2">
          {sources.map((src, i) => (
            <div
              key={i}
              className="bg-bg-card border border-border rounded-lg p-3 text-xs"
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-accent font-semibold shrink-0">[{i + 1}]</span>
                  <span className="text-slate-300 font-medium truncate">{src.file}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-muted">Slide {src.slide}</span>
                  <span
                    className={`font-mono px-1.5 py-0.5 rounded text-xs ${
                      src.score > 0.7
                        ? "bg-green-900/40 text-green-400"
                        : src.score > 0.4
                        ? "bg-yellow-900/40 text-yellow-400"
                        : "bg-bg-hover text-muted"
                    }`}
                  >
                    {src.score.toFixed(2)}
                  </span>
                </div>
              </div>
              <p className="text-slate-400 leading-relaxed line-clamp-3">{src.preview}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
