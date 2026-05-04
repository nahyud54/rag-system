"use client";

import SourcePanel from "./SourcePanel";
import type { Message } from "@/lib/types";

interface Props {
  message: Message;
}

function renderMarkdown(text: string) {
  // Very lightweight markdown: bold, code, bullet lists, headers
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/^[•\-\*] (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>");
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] bg-accent text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed shadow-lg">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 mb-6">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-bg-card border border-border flex items-center justify-center text-base shrink-0 mt-0.5">
        🧠
      </div>

      <div className="flex-1 min-w-0">
        <div className="bg-bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-md">
          {message.streaming && !message.content ? (
            <span className="cursor-blink text-muted text-sm">Đang suy nghĩ</span>
          ) : (
            <div
              className="prose-chat text-sm text-slate-200"
              dangerouslySetInnerHTML={{
                __html: `<p>${renderMarkdown(message.content)}</p>`,
              }}
            />
          )}
          {message.streaming && message.content && (
            <span className="cursor-blink" />
          )}
        </div>

        {/* Sources */}
        {!message.streaming && message.sources && message.sources.length > 0 && (
          <div className="mt-1 px-1">
            <SourcePanel sources={message.sources} />
          </div>
        )}

        <p className="text-xs text-muted mt-1 px-1">
          {new Date(message.timestamp).toLocaleTimeString("vi-VN")}
        </p>
      </div>
    </div>
  );
}
