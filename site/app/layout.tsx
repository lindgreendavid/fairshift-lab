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
  metadataBase: new URL("https://fairshift-lab.lindgreendavid.chatgpt.site"),
  title: "Fairshift Lab — Verified fairness-under-shift research",
  description:
    "A verified, accessible research laboratory with a frozen 300-experiment report on calibration, decisions, performance, and group-fairness measurements under distribution shift.",
  applicationName: "Fairshift Lab",
  keywords: [
    "responsible AI",
    "algorithmic fairness",
    "distribution shift",
    "machine learning",
    "uncertainty",
    "probability calibration",
    "threshold sensitivity",
    "reproducible research",
    "web accessibility",
  ],
  openGraph: {
    title: "Fairshift Lab",
    description:
      "Move a population, trace every decision, and inspect the frozen 300-experiment report.",
    type: "website",
    images: [
      {
        url: "/og-v1.png",
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
      "Move a population, trace every decision, and inspect the frozen 300-experiment report.",
    images: ["/og-v1.png"],
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
