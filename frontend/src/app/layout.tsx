import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../contexts/AuthContext";

export const metadata: Metadata = {
  title: "Trading Insights",
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
      <body className="bg-gray-50 min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
