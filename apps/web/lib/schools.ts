import { apiFetch } from "@/lib/api-client";
import type { SchoolProfile } from "@/types/api";

export function getSchoolProfile(schoolId: number, signal?: AbortSignal) {
  return apiFetch<SchoolProfile>(`/schools/${schoolId}`, { signal });
}

export function getSchoolProfiles(schoolIds: number[], signal?: AbortSignal) {
  return Promise.all(schoolIds.map((schoolId) => getSchoolProfile(schoolId, signal)));
}
