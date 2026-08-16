import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "InfraPilot — Incident Operations",
  description: "Agentic infrastructure incident investigation and remediation",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <Link href="/incidents" className="brand" aria-label="InfraPilot home">
              <span className="brand-mark">IP</span>
              <span><strong>InfraPilot</strong><small>Incident operations</small></span>
            </Link>
            <nav className="nav-list" aria-label="Primary navigation">
              <Link href="/incidents" className="nav-item nav-item-active">
                <span className="nav-dot" /> Incidents
              </Link>
            </nav>
            <div className="sidebar-foot">
              <span className="status-pulse" />
              <span><strong>Control plane</strong><small>Local environment</small></span>
            </div>
          </aside>
          <div className="main-column">
            <header className="topbar">
              <span className="eyebrow">AUTONOMOUS RESPONSE</span>
              <span className="environment-badge">DEVELOPMENT</span>
            </header>
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
