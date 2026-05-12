"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

const savedKey = "college-exploration.saved-school-ids.v1";
const compareKey = "college-exploration.compare-school-ids.v1";
const maxCompareSchools = 5;

type SchoolActionState = {
  savedIds: Set<number>;
  compareIds: Set<number>;
  toggleSaved: (schoolId: number) => void;
  toggleCompare: (schoolId: number) => void;
  clearCompare: () => void;
  compareLimit: number;
};

export function useSchoolActionState(): SchoolActionState {
  const [savedIds, setSavedIds] = useState<Set<number>>(() => new Set());
  const [compareIds, setCompareIds] = useState<Set<number>>(() => new Set());

  useEffect(() => {
    setSavedIds(readIdSet(savedKey));
    setCompareIds(readIdSet(compareKey));
  }, []);

  const persistSaved = useCallback((updater: (current: Set<number>) => Set<number>) => {
    setSavedIds((current) => {
      const next = updater(current);
      writeIdSet(savedKey, next);
      return next;
    });
  }, []);

  const persistCompare = useCallback((updater: (current: Set<number>) => Set<number>) => {
    setCompareIds((current) => {
      const next = updater(current);
      writeIdSet(compareKey, next);
      return next;
    });
  }, []);

  const toggleSaved = useCallback(
    (schoolId: number) => {
      persistSaved((current) => toggleSetValue(current, schoolId));
    },
    [persistSaved],
  );

  const toggleCompare = useCallback(
    (schoolId: number) => {
      persistCompare((current) => {
        if (current.has(schoolId)) return toggleSetValue(current, schoolId);
        if (current.size >= maxCompareSchools) return current;
        return toggleSetValue(current, schoolId);
      });
    },
    [persistCompare],
  );

  const clearCompare = useCallback(() => {
    persistCompare(() => new Set());
  }, [persistCompare]);

  return useMemo(
    () => ({
      savedIds,
      compareIds,
      toggleSaved,
      toggleCompare,
      clearCompare,
      compareLimit: maxCompareSchools,
    }),
    [clearCompare, compareIds, savedIds, toggleCompare, toggleSaved],
  );
}

function toggleSetValue(current: Set<number>, value: number) {
  const next = new Set(current);
  if (next.has(value)) next.delete(value);
  else next.add(value);
  return next;
}

function readIdSet(key: string) {
  if (typeof window === "undefined") return new Set<number>();

  try {
    const parsed = JSON.parse(window.localStorage.getItem(key) ?? "[]");
    if (!Array.isArray(parsed)) return new Set<number>();
    return new Set(parsed.filter((value): value is number => Number.isInteger(value)));
  } catch {
    return new Set<number>();
  }
}

function writeIdSet(key: string, ids: Set<number>) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(Array.from(ids)));
}
