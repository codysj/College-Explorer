import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Turn a snake_case code from the API into readable text: "cost_within_budget" -> "Cost within budget". */
export function humanize(value: string) {
  const spaced = value.replaceAll("_", " ");
  return spaced.charAt(0).toUpperCase() + spaced.slice(1);
}
