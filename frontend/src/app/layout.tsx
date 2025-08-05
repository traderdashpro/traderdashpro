import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../contexts/AuthContext";

export const metadata: Metadata = {
  title: "TradeDashPro - Master Your Trading Performance",
  description:
    "Import your trading data, visualize your performance, and get AI-powered insights to improve your trading strategy. Take your trading to the next level with TradeDashPro.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
