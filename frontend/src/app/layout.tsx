import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trading Dashboard",
  description:
    "A comprehensive trading dashboard for tracking trades and getting AI insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
