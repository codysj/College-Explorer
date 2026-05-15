import type { Metadata } from "next";

import { SavedSchoolsDashboard } from "@/components/dashboard/saved-schools-dashboard";

export const metadata: Metadata = {
  title: "Saved Schools",
  description: "Manage saved schools and decision statuses.",
};

export default function DashboardPage() {
  return <SavedSchoolsDashboard />;
}
