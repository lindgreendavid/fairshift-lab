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
  title: "Fairshift Lab — Fairness under distribution shift",
  description:
    "An interactive research laboratory for exploring how distribution shift changes calibration, threshold-sensitive decisions, performance, and group-fairness measurements.",
  applicationName: "Fairshift Lab",
  keywords: [
    "responsible AI",
    "algorithmic fairness",
    "distribution shift",
    "machine learning",
    "uncertainty",
    "probability calibration",
    "threshold sensitivity",
  ],
  openGraph: {
    title: "Fairshift Lab",
    description:
      "Move a population. Trace calibration and fairness across every decision threshold.",
    type: "website",
    images: [
      {
        url: "/og-v0.3.png",
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
      "Move a population. Trace calibration and fairness across every decision threshold.",
    images: ["/og-v0.3.png"],
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
