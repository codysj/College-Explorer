import type { SchoolSearchResponse } from "@/types/api";
import { apiFetch } from "@/lib/api-client";

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
    apiSort: "name",
    direction: "asc",
    note: "Uses name until ranking exists",
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
