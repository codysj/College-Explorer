import type { Metadata } from "next";

import { DecisionReportPage } from "@/components/decision/decision-report-page";

export const metadata: Metadata = {
  title: "Decision report | College Exploration Platform",
  description: "Printable college decision briefing for finalists, tradeoffs, costs, and sensitivity highlights.",
};

export default function Page() {
  return <DecisionReportPage />;
}
