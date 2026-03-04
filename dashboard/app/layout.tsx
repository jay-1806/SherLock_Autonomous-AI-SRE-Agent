import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'SherLock — Autonomous SRE Platform',
  description: 'AI-powered incident investigation and remediation platform',
};

const navLinks = [
  { href: '/', label: 'Incidents', icon: '🔥' },
  { href: '/services', label: 'Services', icon: '🖥️' },
  { href: '/remediation', label: 'Remediation', icon: '⚡' },
  { href: '/kpis', label: 'KPIs', icon: '📊' },
  { href: '/feedback', label: 'Feedback', icon: '💬' },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-gray-950">
          {/* Top Navigation */}
          <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <Link href="/" className="text-xl font-bold text-emerald-400 flex items-center gap-2">
                    <span className="text-2xl">🔍</span>
                    <span>SherLock</span>
                    <span className="text-xs bg-emerald-400/10 text-emerald-400 px-2 py-0.5 rounded-full font-medium ml-2">
                      SRE Platform
                    </span>
                  </Link>
                </div>
                <div className="flex items-center space-x-1">
                  {navLinks.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      className="text-gray-400 hover:text-white hover:bg-gray-800 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5"
                    >
                      <span>{link.icon}</span>
                      {link.label}
                    </Link>
                  ))}
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                    API Connected
                  </div>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
