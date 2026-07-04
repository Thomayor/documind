import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DocuMind",
  description: "Interrogez vos documents avec l'IA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${geistSans.variable} ${geistMono.variable} dark`}>
      <body className="antialiased h-screen flex flex-col overflow-hidden">
        {/* Top header — pleine largeur */}
        <header className="h-14 shrink-0 border-b border-border flex items-center px-4 gap-4">
          <div className="flex items-center gap-2 w-48 shrink-0">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect width="16" height="16" rx="4" fill="currentColor" className="text-primary"/>
              <path d="M4 5h8M4 8h5.5M4 11h3" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
            <span className="font-semibold text-sm">DocuMind</span>
          </div>
          <div className="h-5 w-px bg-border" />
          <nav className="flex items-center gap-1">
            <a href="/" className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-foreground bg-accent">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M2 1.5h6l2.5 2.5V12H2V1.5Z" stroke="currentColor" strokeWidth="1.2" fill="none"/>
                <path d="M4.5 5h4M4.5 7h2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
              </svg>
              Documents
            </a>
            <a href="/chat" className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent/60 transition-colors">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M1.5 2h10v6.5H7L4.5 11V8.5H1.5V2Z" stroke="currentColor" strokeWidth="1.2" fill="none"/>
              </svg>
              Chat
            </a>
            <a href="/history" className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent/60 transition-colors">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.2"/>
                <path d="M6.5 4V6.5l1.5 1.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
              </svg>
              Historique
            </a>
          </nav>
        </header>

        {/* Content */}
        <div className="flex-1 min-h-0">
          {children}
        </div>
      </body>
    </html>
  );
}
