import { apiFetch } from "@/lib/api-client";
import type { SchoolProfile, SimilarSchoolVariant, SimilarSchoolsResponse } from "@/types/api";

export function getSchoolProfile(schoolId: number, signal?: AbortSignal) {
  return apiFetch<SchoolProfile>(`/schools/${schoolId}`, { signal });
}

export function getSchoolProfiles(schoolIds: number[], signal?: AbortSignal) {
  return Promise.all(schoolIds.map((schoolId) => getSchoolProfile(schoolId, signal)));
}

export function getSimilarSchools(
  schoolId: number,
  variant: SimilarSchoolVariant,
  homeState?: string,
  signal?: AbortSignal,
) {
  const params = new URLSearchParams({
    variant,
    page_size: "3",
  });
  if (homeState) params.set("home_state", homeState);
  return apiFetch<SimilarSchoolsResponse>(`/schools/${schoolId}/similar?${params.toString()}`, { signal });
}
