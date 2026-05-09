import type { Metadata } from "next";

import { SearchExperience } from "@/components/search/search-experience";

export const metadata: Metadata = {
  title: "Search Schools",
  description: "Filter and compare schools using structured decision-support data.",
};

export default function SearchPage() {
  return <SearchExperience />;
}
