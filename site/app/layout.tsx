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
  title: "Fairshift Lab — Transparent policy trade-offs under shift",
  description:
    "An accessible research laboratory for declaring error costs, comparing mitigation policies, and inspecting fairness–utility Pareto frontiers under distribution shift.",
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
  ],
  openGraph: {
    title: "Fairshift Lab",
    description:
      "Declare the stakes, compare eight policies, and inspect every fairness–utility trade-off.",
    type: "website",
    images: [
      {
        url: "/og-v1-1.png",
        width: 1672,
        height: 941,
        alt: "Fairshift Lab Policy Studio — source and target shift above a policy Pareto field",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Fairshift Lab",
    description:
      "Declare the stakes, compare eight policies, and inspect every fairness–utility trade-off.",
    images: ["/og-v1-1.png"],
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
