import type { Metadata } from "next";

import { AnalyticsDashboard } from "@/components/analytics/analytics-dashboard";

export const metadata: Metadata = {
  title: "Analytics | College Exploration Platform",
  description: "Internal product analytics and deterministic ranking evaluation.",
};

export default function Page() {
  return <AnalyticsDashboard />;
}
