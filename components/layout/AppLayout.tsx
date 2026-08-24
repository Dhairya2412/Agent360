"use client";

import { Sidebar } from "./Sidebar";
import { Toaster } from "@/components/ui/toaster";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <Toaster>
      <div className="min-h-screen">
        <Sidebar />
        <main className="ml-64 min-h-screen">{children}</main>
      </div>
    </Toaster>
  );
}
