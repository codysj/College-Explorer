"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { trackAnalyticsEvent } from "@/lib/analytics";
import type { SchoolProfile, SchoolSearchCard } from "@/types/api";

const savedKey = "college-exploration.saved-schools.v1";
const legacySavedIdsKey = "college-exploration.saved-school-ids.v1";
const compareKey = "college-exploration.compare-schools.v1";
const legacyCompareIdsKey = "college-exploration.compare-school-ids.v1";
const maxCompareSchools = 5;

export const savedSchoolStatuses = [
  "interested",
  "applying",
  "accepted",
  "finalist",
  "removed",
] as const;

export type SavedSchoolStatus = (typeof savedSchoolStatuses)[number];

export type SchoolSnapshot = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  type: string;
  setting: string;
  enrollment: number | null;
  acceptance_rate: number | null;
  net_price: number | null;
  graduation_rate: number | null;
  median_earnings?: number | null;
  fit_score?: number | null;
  category_scores?: Record<string, number>;
};

export type SavedSchoolEntry = SchoolSnapshot & {
  status: SavedSchoolStatus;
  saved_at: string;
  updated_at: string;
};

export type CompareSchoolEntry = SchoolSnapshot & {
  added_at: string;
};

type SchoolActionState = {
  savedSchools: SavedSchoolEntry[];
  comparedSchools: CompareSchoolEntry[];
  savedIds: Set<number>;
  compareIds: Set<number>;
  saveSchool: (school: SchoolActionInput, status?: SavedSchoolStatus) => void;
  removeSavedSchool: (schoolId: number) => void;
  updateSavedStatus: (schoolId: number, status: SavedSchoolStatus) => void;
  toggleSaved: (school: SchoolActionInput) => void;
  addCompareSchool: (school: SchoolActionInput) => boolean;
  removeCompareSchool: (schoolId: number) => void;
  toggleCompare: (school: SchoolActionInput) => boolean;
  clearCompare: () => void;
  compareLimit: number;
};

export type SchoolActionInput = SchoolSearchCard | SchoolProfile | SchoolSnapshot;

export function useSchoolActionState(): SchoolActionState {
  const [savedSchools, setSavedSchools] = useState<SavedSchoolEntry[]>([]);
  const [comparedSchools, setComparedSchools] = useState<CompareSchoolEntry[]>([]);

  useEffect(() => {
    setSavedSchools(readSavedSchools());
    setComparedSchools(readComparedSchools());
  }, []);

  useEffect(() => {
    const sync = (event: StorageEvent) => {
      if (!event.key || event.key === savedKey || event.key === legacySavedIdsKey) {
        setSavedSchools(readSavedSchools());
      }
      if (!event.key || event.key === compareKey || event.key === legacyCompareIdsKey) {
        setComparedSchools(readComparedSchools());
      }
    };

    window.addEventListener("storage", sync);
    window.addEventListener("college-exploration-school-actions", sync as EventListener);
    return () => {
      window.removeEventListener("storage", sync);
      window.removeEventListener("college-exploration-school-actions", sync as EventListener);
    };
  }, []);

  const persistSaved = useCallback((updater: (current: SavedSchoolEntry[]) => SavedSchoolEntry[]) => {
    setSavedSchools((current) => {
      const next = dedupeSavedSchools(updater(current));
      writeJson(savedKey, next);
      notifyLocalSubscribers();
      return next;
    });
  }, []);

  const persistCompared = useCallback((updater: (current: CompareSchoolEntry[]) => CompareSchoolEntry[]) => {
    let changed = false;
    setComparedSchools((current) => {
      const next = dedupeComparedSchools(updater(current));
      changed = next.length !== current.length || next.some((entry, index) => entry.school_id !== current[index]?.school_id);
      writeJson(compareKey, next);
      notifyLocalSubscribers();
      return next;
    });
    return changed;
  }, []);

  const saveSchool = useCallback(
    (school: SchoolActionInput, status: SavedSchoolStatus = "interested") => {
      persistSaved((current) => upsertSavedSchool(current, school, status));
      const snapshot = toSchoolSnapshot(school);
      trackAnalyticsEvent({
        event_name: "school_saved",
        entity_type: "school",
        entity_id: snapshot.school_id,
        metadata: {
          school_name: snapshot.name,
          saved_status: status,
          fit_score: snapshot.fit_score,
          category_scores: snapshot.category_scores,
        },
      });
    },
    [persistSaved],
  );

  const removeSavedSchool = useCallback(
    (schoolId: number) => {
      persistSaved((current) =>
        current.map((entry) =>
          entry.school_id === schoolId
            ? { ...entry, status: "removed", updated_at: new Date().toISOString() }
            : entry,
        ),
      );
    },
    [persistSaved],
  );

  const updateSavedStatus = useCallback(
    (schoolId: number, status: SavedSchoolStatus) => {
      persistSaved((current) =>
        current.map((entry) =>
          entry.school_id === schoolId ? { ...entry, status, updated_at: new Date().toISOString() } : entry,
        ),
      );
    },
    [persistSaved],
  );

  const toggleSaved = useCallback(
    (school: SchoolActionInput) => {
      const schoolId = getSchoolId(school);
      const current = savedSchools.find((entry) => entry.school_id === schoolId);
      if (current && current.status !== "removed") removeSavedSchool(schoolId);
      else saveSchool(school, current?.status === "removed" ? "interested" : current?.status);
    },
    [removeSavedSchool, saveSchool, savedSchools],
  );

  const addCompareSchool = useCallback(
    (school: SchoolActionInput) => {
      const schoolId = getSchoolId(school);
      if (comparedSchools.some((entry) => entry.school_id === schoolId)) return true;
      if (comparedSchools.length >= maxCompareSchools) return false;

      persistCompared((current) => [
        ...current,
        {
          ...toSchoolSnapshot(school),
          added_at: new Date().toISOString(),
        },
      ]);
      const snapshot = toSchoolSnapshot(school);
      trackAnalyticsEvent({
        event_name: "school_compared",
        entity_type: "school",
        entity_id: schoolId,
        metadata: {
          school_name: snapshot.name,
          fit_score: snapshot.fit_score,
          category_scores: snapshot.category_scores,
        },
      });
      return true;
    },
    [comparedSchools, persistCompared],
  );

  const removeCompareSchool = useCallback(
    (schoolId: number) => {
      persistCompared((current) => current.filter((entry) => entry.school_id !== schoolId));
    },
    [persistCompared],
  );

  const toggleCompare = useCallback(
    (school: SchoolActionInput) => {
      const schoolId = getSchoolId(school);
      if (comparedSchools.some((entry) => entry.school_id === schoolId)) {
        removeCompareSchool(schoolId);
        return true;
      }
      return addCompareSchool(school);
    },
    [addCompareSchool, comparedSchools, removeCompareSchool],
  );

  const clearCompare = useCallback(() => {
    persistCompared(() => []);
  }, [persistCompared]);

  const activeSavedSchools = useMemo(
    () => savedSchools.filter((entry) => entry.status !== "removed"),
    [savedSchools],
  );

  return useMemo(
    () => ({
      savedSchools,
      comparedSchools,
      savedIds: new Set(activeSavedSchools.map((school) => school.school_id)),
      compareIds: new Set(comparedSchools.map((school) => school.school_id)),
      saveSchool,
      removeSavedSchool,
      updateSavedStatus,
      toggleSaved,
      addCompareSchool,
      removeCompareSchool,
      toggleCompare,
      clearCompare,
      compareLimit: maxCompareSchools,
    }),
    [
      activeSavedSchools,
      addCompareSchool,
      clearCompare,
      comparedSchools,
      removeCompareSchool,
      removeSavedSchool,
      saveSchool,
      savedSchools,
      toggleCompare,
      toggleSaved,
      updateSavedStatus,
    ],
  );
}

export function getVisibleSavedSchools(savedSchools: SavedSchoolEntry[]) {
  return savedSchools.filter((entry) => entry.status !== "removed");
}

export function getSchoolId(school: SchoolActionInput) {
  return school.school_id;
}

export function toSchoolSnapshot(school: SchoolActionInput): SchoolSnapshot {
  const maybeProfile = school as SchoolProfile;
  const maybeSearchCard = school as SchoolSearchCard;
  const maybeSnapshot = isSchoolSnapshot(school) ? school : null;

  return {
    school_id: school.school_id,
    name: school.name,
    city: school.city,
    state: school.state,
    type: school.type,
    setting: school.setting,
    enrollment: school.enrollment,
    acceptance_rate: "acceptance_rate" in school ? school.acceptance_rate : null,
    net_price:
      "net_price" in school
        ? school.net_price
        : maybeProfile.cost?.net_price ?? maybeSnapshot?.net_price ?? null,
    graduation_rate:
      "graduation_rate" in school
        ? maybeSearchCard.graduation_rate
        : maybeProfile.academics?.graduation_rate ?? maybeSnapshot?.graduation_rate ?? null,
    median_earnings: maybeProfile.outcomes?.median_earnings ?? maybeSnapshot?.median_earnings ?? null,
    fit_score: school.fit_score ?? null,
    category_scores: school.category_scores ?? {},
  };
}

function upsertSavedSchool(
  current: SavedSchoolEntry[],
  school: SchoolActionInput,
  status: SavedSchoolStatus = "interested",
) {
  const snapshot = toSchoolSnapshot(school);
  const now = new Date().toISOString();
  const existing = current.find((entry) => entry.school_id === snapshot.school_id);

  if (!existing) {
    return [
      ...current,
      {
        ...snapshot,
        status,
        saved_at: now,
        updated_at: now,
      },
    ];
  }

  return current.map((entry) =>
    entry.school_id === snapshot.school_id
      ? {
          ...entry,
          ...snapshot,
          status,
          updated_at: now,
        }
      : entry,
  );
}

function dedupeSavedSchools(entries: SavedSchoolEntry[]) {
  const byId = new Map<number, SavedSchoolEntry>();
  for (const entry of entries) byId.set(entry.school_id, entry);
  return Array.from(byId.values());
}

function dedupeComparedSchools(entries: CompareSchoolEntry[]) {
  const byId = new Map<number, CompareSchoolEntry>();
  for (const entry of entries.slice(0, maxCompareSchools)) byId.set(entry.school_id, entry);
  return Array.from(byId.values());
}

function readSavedSchools() {
  const modern = readJson<unknown>(savedKey);
  if (Array.isArray(modern)) return normalizeSavedSchools(modern);

  return readLegacyIds(legacySavedIdsKey).map((schoolId) => {
    const now = new Date().toISOString();
    return {
      school_id: schoolId,
      name: `School ${schoolId}`,
      city: "Unknown",
      state: "--",
      type: "Unknown",
      setting: "Unknown",
      enrollment: null,
      acceptance_rate: null,
      net_price: null,
      graduation_rate: null,
      median_earnings: null,
      fit_score: null,
      category_scores: {},
      status: "interested" as const,
      saved_at: now,
      updated_at: now,
    };
  });
}

function readComparedSchools() {
  const modern = readJson<unknown>(compareKey);
  if (Array.isArray(modern)) return normalizeComparedSchools(modern);

  return readLegacyIds(legacyCompareIdsKey).slice(0, maxCompareSchools).map((schoolId) => ({
    school_id: schoolId,
    name: `School ${schoolId}`,
    city: "Unknown",
    state: "--",
    type: "Unknown",
    setting: "Unknown",
    enrollment: null,
    acceptance_rate: null,
    net_price: null,
    graduation_rate: null,
    median_earnings: null,
    fit_score: null,
    category_scores: {},
    added_at: new Date().toISOString(),
  }));
}

function normalizeSavedSchools(value: unknown[]) {
  return dedupeSavedSchools(value.flatMap((item) => {
    if (!isRecord(item)) return [];
    const snapshot = normalizeSnapshot(item);
    if (!snapshot) return [];
    const status = savedSchoolStatuses.includes(item.status as SavedSchoolStatus)
      ? (item.status as SavedSchoolStatus)
      : "interested";
    const savedAt = typeof item.saved_at === "string" ? item.saved_at : new Date().toISOString();
    const updatedAt = typeof item.updated_at === "string" ? item.updated_at : savedAt;
    return [{ ...snapshot, status, saved_at: savedAt, updated_at: updatedAt }];
  }));
}

function normalizeComparedSchools(value: unknown[]) {
  return dedupeComparedSchools(value.flatMap((item) => {
    if (!isRecord(item)) return [];
    const snapshot = normalizeSnapshot(item);
    if (!snapshot) return [];
    return [{
      ...snapshot,
      added_at: typeof item.added_at === "string" ? item.added_at : new Date().toISOString(),
    }];
  }));
}

function normalizeSnapshot(value: Record<string, unknown>): SchoolSnapshot | null {
  if (!Number.isInteger(value.school_id) || typeof value.name !== "string") return null;
  const schoolId = value.school_id as number;
  const categoryScores = isRecord(value.category_scores)
    ? Object.entries(value.category_scores).reduce<Record<string, number>>((scores, [key, score]) => {
        if (typeof score === "number") scores[key] = score;
        return scores;
      }, {})
    : {};

  return {
    school_id: schoolId,
    name: value.name,
    city: typeof value.city === "string" ? value.city : "Unknown",
    state: typeof value.state === "string" ? value.state : "--",
    type: typeof value.type === "string" ? value.type : "Unknown",
    setting: typeof value.setting === "string" ? value.setting : "Unknown",
    enrollment: nullableNumber(value.enrollment),
    acceptance_rate: nullableNumber(value.acceptance_rate),
    net_price: nullableNumber(value.net_price),
    graduation_rate: nullableNumber(value.graduation_rate),
    median_earnings: nullableNumber(value.median_earnings),
    fit_score: nullableNumber(value.fit_score),
    category_scores: categoryScores,
  };
}

function nullableNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function readLegacyIds(key: string) {
  const parsed = readJson<unknown>(key);
  if (!Array.isArray(parsed)) return [];
  return parsed.filter((value): value is number => Number.isInteger(value));
}

function readJson<T>(key: string): T | null {
  if (typeof window === "undefined") return null;

  try {
    const item = window.localStorage.getItem(key);
    return item ? (JSON.parse(item) as T) : null;
  } catch {
    return null;
  }
}

function writeJson(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

function notifyLocalSubscribers() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event("college-exploration-school-actions"));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isSchoolSnapshot(value: SchoolActionInput): value is SchoolSnapshot {
  return "net_price" in value && "graduation_rate" in value;
}
