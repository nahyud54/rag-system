import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG System – AI Study Assistant",
  description: "Retrieval-Augmented Generation for Deep Learning course materials",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className="h-full">
      <body className="h-full bg-bg-base text-slate-200">{children}</body>
    </html>
  );
}
