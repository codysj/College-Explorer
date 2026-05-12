import type { Metadata } from "next";

import { SchoolProfilePage } from "@/components/schools/school-profile";
import { getSchoolProfile } from "@/lib/schools";

type SchoolPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export async function generateMetadata({ params }: SchoolPageProps): Promise<Metadata> {
  const { id } = await params;
  const schoolId = Number(id);

  if (!Number.isInteger(schoolId) || schoolId <= 0) {
    return {
      title: "School Profile",
      description: "Explore a structured school profile.",
    };
  }

  try {
    const profile = await getSchoolProfile(schoolId);
    return {
      title: profile.name,
      description: `${profile.name} profile, fit summary, academics, cost, outcomes, and campus life.`,
    };
  } catch {
    return {
      title: "School Profile",
      description: "Explore a structured school profile.",
    };
  }
}

export default async function SchoolPage({ params }: SchoolPageProps) {
  const { id } = await params;
  const schoolId = Number(id);

  return <SchoolProfilePage schoolId={Number.isInteger(schoolId) && schoolId > 0 ? schoolId : 0} />;
}
