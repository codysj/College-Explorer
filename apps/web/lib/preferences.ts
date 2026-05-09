export const PREFERENCE_STORAGE_KEY = "college-exploration.preference-profile.v1";

export type PreferenceWeights = {
  academic: number;
  cost: number;
  career: number;
  campus: number;
  location: number;
  admissions_realism: number;
};

export type PreferenceProfile = {
  profile_version: "v1.local";
  intended_major: string;
  academic_interests: string[];
  home_state: string;
  preferred_regions: string[];
  preferred_states: string[];
  preferred_settings: string[];
  preferred_school_types: string[];
  max_annual_cost: number | null;
  aid_importance: "low" | "medium" | "high" | "";
  career_priorities: string[];
  campus_preferences: string[];
  admissions_strategy: "balanced" | "likely" | "reach" | "";
  target_acceptance_rate_min: number | null;
  weights: PreferenceWeights;
  completion: {
    completed_steps: number;
    total_steps: number;
    percent: number;
  };
  updated_at: string;
};

export type ApiPreferenceProfile = {
  intended_major: string | null;
  home_state: string | null;
  max_annual_cost: number | null;
  weights: Record<string, number>;
  constraints: Record<string, string | number | boolean | null>;
};

export type PreferenceDraft = Omit<PreferenceProfile, "completion" | "profile_version" | "updated_at">;

export const totalPreferenceSteps = 7;

export const defaultWeights: PreferenceWeights = {
  academic: 0.2,
  cost: 0.2,
  career: 0.18,
  campus: 0.14,
  location: 0.14,
  admissions_realism: 0.14,
};

export const defaultPreferenceDraft: PreferenceDraft = {
  intended_major: "",
  academic_interests: [],
  home_state: "",
  preferred_regions: [],
  preferred_states: [],
  preferred_settings: [],
  preferred_school_types: [],
  max_annual_cost: null,
  aid_importance: "",
  career_priorities: [],
  campus_preferences: [],
  admissions_strategy: "",
  target_acceptance_rate_min: null,
  weights: defaultWeights,
};

export function buildPreferenceProfile(draft: PreferenceDraft): PreferenceProfile {
  const completion = calculatePreferenceCompletion(draft);
  return {
    ...draft,
    home_state: draft.home_state.toUpperCase(),
    preferred_states: draft.preferred_states.map((state) => state.toUpperCase()),
    profile_version: "v1.local",
    completion,
    updated_at: new Date().toISOString(),
  };
}

export function calculatePreferenceCompletion(draft: PreferenceDraft) {
  const completed = [
    Boolean(draft.intended_major.trim() || draft.academic_interests.length > 0),
    Boolean(draft.max_annual_cost !== null || draft.aid_importance),
    draft.career_priorities.length > 0,
    Boolean(draft.home_state.trim() || draft.preferred_regions.length > 0 || draft.preferred_states.length > 0),
    Boolean(draft.preferred_settings.length > 0 || draft.preferred_school_types.length > 0 || draft.campus_preferences.length > 0),
    Boolean(draft.admissions_strategy || draft.target_acceptance_rate_min !== null),
    Object.values(draft.weights).every((weight) => weight >= 0 && weight <= 1),
  ].filter(Boolean).length;

  return {
    completed_steps: completed,
    total_steps: totalPreferenceSteps,
    percent: Math.round((completed / totalPreferenceSteps) * 100),
  };
}

export function toApiPreferenceProfile(profile: PreferenceProfile): ApiPreferenceProfile {
  return {
    intended_major: profile.intended_major.trim() || null,
    home_state: profile.home_state.trim() || null,
    max_annual_cost: profile.max_annual_cost,
    weights: profile.weights,
    constraints: {
      preferred_region: profile.preferred_regions[0] ?? null,
      preferred_state: profile.preferred_states[0] ?? (profile.home_state || null),
      preferred_setting: profile.preferred_settings[0] ?? null,
      preferred_school_type: profile.preferred_school_types[0] ?? null,
      aid_importance: profile.aid_importance,
      admissions_strategy: profile.admissions_strategy || null,
      target_acceptance_rate_min: profile.target_acceptance_rate_min,
    },
  };
}

export function savePreferenceProfile(profile: PreferenceProfile) {
  window.localStorage.setItem(PREFERENCE_STORAGE_KEY, JSON.stringify(profile));
}

export function loadPreferenceProfile() {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(PREFERENCE_STORAGE_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as PreferenceProfile;
    return parsed.profile_version === "v1.local" ? parsed : null;
  } catch {
    return null;
  }
}

export function buildSearchParamsFromPreference(profile: PreferenceProfile) {
  const params = new URLSearchParams();
  params.set("from_onboarding", "1");
  if (profile.preferred_states[0] || profile.home_state) {
    params.set("state", profile.preferred_states[0] ?? profile.home_state);
  }
  if (profile.preferred_settings[0]) params.set("setting", profile.preferred_settings[0]);
  if (profile.preferred_school_types[0]) params.set("type", profile.preferred_school_types[0]);
  if (profile.max_annual_cost !== null) params.set("max_net_price", String(profile.max_annual_cost));
  return params;
}
