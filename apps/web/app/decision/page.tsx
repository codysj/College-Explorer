import type { Metadata } from "next";

import { AcceptedSchoolsWorkspace } from "@/components/decision/accepted-schools-workspace";

export const metadata: Metadata = {
  title: "Accepted Schools",
  description: "Compare accepted schools and generate an explainable decision summary.",
};

export default function DecisionPage() {
  return <AcceptedSchoolsWorkspace />;
}
