import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "sonner";

// Using system fonts to avoid Google Fonts timeout issues
// Montserrat font family is defined in tailwind.config.ts as fallback

export const metadata: Metadata = {
  title: "Maverick Ascend - AI-Powered Talent Platform",
  description: "Empowering fresh minds with AI-driven training, assessment, and career growth",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
