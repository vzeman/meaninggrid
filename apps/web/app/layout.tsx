import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "MeaningGrid",
  description: "Semantic intelligence and context management for AI agents."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
