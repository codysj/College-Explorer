import type { RankingResponse, SchoolSearchResponse } from "@/types/api";
import { apiFetch } from "@/lib/api-client";
import { toApiPreferenceProfile, type PreferenceProfile } from "@/lib/preferences";

export const PAGE_SIZE = 10;

type SortOption = {
  value: string;
  label: string;
  apiSort: "name" | "net_price" | "graduation_rate" | "acceptance_rate" | "enrollment";
  direction: "asc" | "desc";
  note?: string;
};

export const sortOptions = [
  {
    value: "best_fit",
    label: "Best fit",
    // Only used as the fallback ordering when no preference profile exists; with a
    // profile, POST /rankings decides the order and these are ignored.
    apiSort: "name",
    direction: "asc",
    note: undefined,
  },
  {
    value: "lowest_cost",
    label: "Lowest cost",
    apiSort: "net_price",
    direction: "asc",
    note: undefined,
  },
  {
    value: "highest_graduation",
    label: "Highest graduation",
    apiSort: "graduation_rate",
    direction: "desc",
    note: undefined,
  },
  {
    value: "most_accessible",
    label: "Most accessible",
    apiSort: "acceptance_rate",
    direction: "desc",
    note: undefined,
  },
  {
    value: "largest",
    label: "Largest enrollment",
    apiSort: "enrollment",
    direction: "desc",
    note: undefined,
  },
] as const satisfies readonly SortOption[];

export type SortValue = (typeof sortOptions)[number]["value"];

export type SearchFilters = {
  query: string;
  state: string;
  type: string;
  setting: string;
  maxNetPrice: string;
  minGraduationRate: string;
  sort: SortValue;
  page: number;
};

const defaultSort = sortOptions[0];

export const defaultFilters: SearchFilters = {
  query: "",
  state: "",
  type: "",
  setting: "",
  maxNetPrice: "",
  minGraduationRate: "",
  sort: defaultSort.value,
  page: 1,
};

export function parseSearchFilters(params: URLSearchParams): SearchFilters {
  const sort = sortOptions.some((option) => option.value === params.get("sort_ui"))
    ? (params.get("sort_ui") as SortValue)
    : defaultSort.value;
  const page = Number(params.get("page"));

  return {
    query: params.get("query") ?? "",
    state: params.get("state") ?? "",
    type: params.get("type") ?? "",
    setting: params.get("setting") ?? "",
    maxNetPrice: params.get("max_net_price") ?? "",
    minGraduationRate: params.get("min_graduation_rate")
      ? String(Math.round(Number(params.get("min_graduation_rate")) * 100))
      : "",
    sort,
    page: Number.isInteger(page) && page > 0 ? page : 1,
  };
}

export function buildSearchParams(filters: SearchFilters) {
  const params = new URLSearchParams();
  const selectedSort = sortOptions.find((option) => option.value === filters.sort) ?? defaultSort;

  params.set("sort_ui", selectedSort.value);
  params.set("sort", selectedSort.apiSort);
  params.set("direction", selectedSort.direction);
  params.set("page", String(filters.page));
  params.set("page_size", String(PAGE_SIZE));

  if (filters.query.trim()) params.set("query", filters.query.trim());
  if (filters.state.trim()) params.set("state", filters.state.trim().toUpperCase());
  if (filters.type) params.set("type", filters.type);
  if (filters.setting) params.set("setting", filters.setting);
  if (filters.maxNetPrice) params.set("max_net_price", filters.maxNetPrice);
  if (filters.minGraduationRate) {
    params.set("min_graduation_rate", (Number(filters.minGraduationRate) / 100).toFixed(2));
  }

  return params;
}

export function buildApiSearchPath(params: URLSearchParams) {
  const apiParams = new URLSearchParams(params);
  apiParams.delete("sort_ui");
  return `/schools/search?${apiParams.toString()}` as const;
}

export function searchSchools(params: URLSearchParams, signal?: AbortSignal) {
  return apiFetch<SchoolSearchResponse>(buildApiSearchPath(params), { signal });
}

/**
 * Ranked mode needs both halves: the "Best fit" sort and a stored preference profile.
 * Without a profile there is nothing to rank against, so search stays structured.
 */
export function isRankedMode(filters: SearchFilters, profile: PreferenceProfile | null) {
  return filters.sort === "best_fit" && profile !== null;
}

export function buildRankingBody(filters: SearchFilters, profile: PreferenceProfile) {
  return {
    preferences: toApiPreferenceProfile(profile),
    // The ranking engine applies these as hard constraints before scoring, so the
    // filter panel keeps working exactly as it does in structured search.
    filters: {
      ...(filters.query.trim() ? { query: filters.query.trim() } : {}),
      ...(filters.state.trim() ? { state: filters.state.trim().toUpperCase() } : {}),
      ...(filters.type ? { type: filters.type } : {}),
      ...(filters.setting ? { setting: filters.setting } : {}),
      ...(filters.maxNetPrice ? { max_net_price: Number(filters.maxNetPrice) } : {}),
      ...(filters.minGraduationRate
        ? { min_graduation_rate: Number(filters.minGraduationRate) / 100 }
        : {}),
      page: filters.page,
      page_size: PAGE_SIZE,
    },
  };
}

export function rankSchools(
  filters: SearchFilters,
  profile: PreferenceProfile,
  signal?: AbortSignal,
) {
  return apiFetch<RankingResponse>("/rankings", {
    method: "POST",
    body: buildRankingBody(filters, profile),
    signal,
  });
}
