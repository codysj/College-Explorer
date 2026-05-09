import type { Metadata } from "next";

import { PreferenceQuiz } from "@/components/onboarding/preference-quiz";

export const metadata: Metadata = {
  title: "Build My Shortlist",
  description: "Create a local preference profile for college search and ranking.",
};

export default function OnboardingPage() {
  return <PreferenceQuiz />;
}
