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
  title: "Fairshift Lab — Synthetic experiments, external evidence, and a robustness lab",
  description:
    "An accessible research laboratory separating synthetic distribution-shift experiments, governed historical observational evidence, and a preregistered synthetic specification-stress study.",
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
    "decision policy",
    "Pareto frontier",
    "external validation",
    "dataset governance",
    "robustness",
    "label noise",
    "specification stress",
  ],
  openGraph: {
    title: "Fairshift Lab",
    description:
      "Move from controlled synthetic shifts to governed historical evidence to a preregistered synthetic robustness stress test—without confusing any of the three for the real world.",
    type: "website",
    images: [
      {
        url: "/og-v1-2.png",
        width: 1672,
        height: 941,
        alt: "Fairshift Lab — separated synthetic, observational, and robustness-stress evidence areas",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Fairshift Lab",
    description:
      "Controlled synthetic experiments, governed historical evidence, a synthetic robustness lab, and no automatic best policy.",
    images: ["/og-v1-2.png"],
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
