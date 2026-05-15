import type { Metadata } from "next";

import { ComparisonWorkspace } from "@/components/compare/comparison-workspace";

export const metadata: Metadata = {
  title: "Compare Schools",
  description: "Compare selected schools side by side.",
};

export default function ComparePage() {
  return <ComparisonWorkspace />;
}
