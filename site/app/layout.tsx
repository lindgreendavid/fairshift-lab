import type { Metadata } from "next";
import "./globals.css";

// Sets the theme before first paint: the saved choice, else the system preference.
const themeScript = `(function(){var d=false;try{var s=localStorage.getItem("theme");d=s?s==="dark":matchMedia("(prefers-color-scheme: dark)").matches}catch(e){d=matchMedia("(prefers-color-scheme: dark)").matches}document.documentElement.dataset.theme=d?"dark":"light"})();`;

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
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <link rel="preload" href="/fonts/geist-latin-wght-normal.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
