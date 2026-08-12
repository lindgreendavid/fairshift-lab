import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Fairshift Lab — Fairness under distribution shift",
  description:
    "An interactive research laboratory for exploring how distribution shift changes model performance, group-fairness measurements, and uncertainty.",
  applicationName: "Fairshift Lab",
  keywords: [
    "responsible AI",
    "algorithmic fairness",
    "distribution shift",
    "machine learning",
    "uncertainty",
  ],
  openGraph: {
    title: "Fairshift Lab",
    description:
      "Move a population. Watch fairness measurements move with it.",
    type: "website",
    images: [
      {
        url: "/og.png",
        width: 1672,
        height: 941,
        alt: "Fairshift Lab — source and target distributions under shift",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Fairshift Lab",
    description:
      "Move a population. Watch fairness measurements move with it.",
    images: ["/og.png"],
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
