"use client";

import { apiFetch } from "@/lib/api-client";
import {
  defaultWeights,
  loadPreferenceProfile,
  toApiPreferenceProfile,
  type ApiPreferenceProfile,
  type PreferenceWeights,
} from "@/lib/preferences";
import type { SensitivityResponse } from "@/types/api";

export type SensitivitySliderWeights = PreferenceWeights & {
  cost_value: number;
  career_outcomes: number;
  campus_lifestyle: number;
  prestige_selectivity: number;
};

export const defaultSensitivityWeights: SensitivitySliderWeights = {
  ...defaultWeights,
  cost_value: defaultWeights.cost,
  career_outcomes: defaultWeights.career,
  campus_lifestyle: defaultWeights.campus,
  prestige_selectivity: 0.12,
};

export function loadBasePreferenceForSensitivity(): ApiPreferenceProfile {
  const profile = loadPreferenceProfile();
  if (profile) return toApiPreferenceProfile(profile);
  return {
    intended_major: null,
    home_state: null,
    max_annual_cost: null,
    weights: defaultWeights,
    constraints: {},
  };
}

export function sliderWeightsFromProfile(): SensitivitySliderWeights {
  const profile = loadPreferenceProfile();
  if (!profile) return defaultSensitivityWeights;
  return {
    ...defaultSensitivityWeights,
    ...profile.weights,
    cost_value: profile.weights.cost,
    career_outcomes: profile.weights.career,
    campus_lifestyle: profile.weights.campus,
  };
}

export async function requestSensitivity(
  schoolIds: number[],
  basePreference: ApiPreferenceProfile,
  weights: SensitivitySliderWeights,
  signal?: AbortSignal,
) {
  return apiFetch<SensitivityResponse>("/sensitivity", {
    method: "POST",
    signal,
    body: {
      preferences: basePreference,
      candidate_school_ids: schoolIds,
      filters: { page: 1, page_size: Math.max(1, Math.min(20, schoolIds.length || 1)) },
      scenarios: [
        {
          scenario_id: "current_slider",
          label: "Current slider priorities",
          weight_adjustments: {
            academic_fit: weights.academic,
            cost_value: weights.cost_value,
            career_outcomes: weights.career_outcomes,
            campus_lifestyle: weights.campus_lifestyle,
            location: weights.location,
            prestige_selectivity: weights.prestige_selectivity,
            admissions_realism: weights.admissions_realism,
          },
        },
        {
          scenario_id: "cost_focus",
          label: "Cost sensitivity raised",
          weight_adjustments: { cost_value: 0.5 },
        },
        {
          scenario_id: "prestige_focus",
          label: "Prestige/selectivity raised",
          weight_adjustments: { prestige_selectivity: 0.5 },
        },
      ],
    },
  });
}
