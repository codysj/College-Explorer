import { apiFetch } from "@/lib/api-client";
import type { SchoolProfile } from "@/types/api";

export function getSchoolProfile(schoolId: number, signal?: AbortSignal) {
  return apiFetch<SchoolProfile>(`/schools/${schoolId}`, { signal });
}
