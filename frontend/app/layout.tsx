import type { ReactNode } from 'react';
import './style.css';
export const metadata = { title: 'AURA Agent', description: 'Autonomous Unified Reasoning Agent' };
export default function RootLayout({children}:{children:ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
