import type { Metadata } from "next";

import { AnalyticsDashboard } from "@/components/analytics/analytics-dashboard";

export const metadata: Metadata = {
  title: "Analytics",
  description: "Operator view of product analytics and ranking evaluation.",
  // An operator page, not part of the student product.
  robots: { index: false, follow: false },
};

export default function Page() {
  return <AnalyticsDashboard />;
}
