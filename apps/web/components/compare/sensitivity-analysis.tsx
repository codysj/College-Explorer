"use client";

import { ArrowDown, ArrowUp, Minus, SlidersHorizontal, Zap } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  loadBasePreferenceForSensitivity,
  requestSensitivity,
  sliderWeightsFromProfile,
  type SensitivitySliderWeights,
} from "@/lib/sensitivity";
import type { SensitivityMovement, SensitivityResponse } from "@/types/api";

type LoadState = "idle" | "loading" | "ready" | "error";

const sliderFields = [
  ["academic", "Academic fit"],
  ["cost_value", "Cost/value"],
  ["career_outcomes", "Career outcomes"],
  ["campus_lifestyle", "Campus/lifestyle"],
  ["location", "Location"],
  ["prestige_selectivity", "Prestige/selectivity"],
  ["admissions_realism", "Admissions realism"],
] as const;

export function SensitivityAnalysis({ schoolIds }: { schoolIds: number[] }) {
  const [weights, setWeights] = useState<SensitivitySliderWeights>(sliderWeightsFromProfile);
  const [report, setReport] = useState<SensitivityResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const basePreference = useMemo(() => loadBasePreferenceForSensitivity(), []);
  const currentScenario = report?.scenarios.find((scenario) => scenario.scenario_id === "current_slider") ?? report?.scenarios[0];

  useEffect(() => {
    if (schoolIds.length < 2) return;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => {
      setLoadState((state) => state === "ready" ? "ready" : "loading");
      setError(null);
      requestSensitivity(schoolIds, basePreference, weights, controller.signal)
        .then((payload) => {
          setReport(payload);
          setLoadState("ready");
        })
        .catch((reason: unknown) => {
          if (controller.signal.aborted) return;
          setError(reason instanceof Error ? reason.message : "Sensitivity analysis failed to load.");
          setLoadState("error");
        });
    }, 180);

    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [basePreference, schoolIds, weights]);

  if (schoolIds.length < 2) return null;

  return (
    <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold tracking-normal text-foreground">
            <SlidersHorizontal className="h-5 w-5 text-primary" aria-hidden="true" />
            Sensitivity analysis
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            Adjust priorities to see which recommendations stay robust and which choices depend on a single preference.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="muted">Ranking {report?.ranking_version ?? "pending"}</Badge>
          <Badge variant={report?.volatile_schools.length ? "muted" : "default"}>
            {report?.volatile_schools.length ?? 0} volatile
          </Badge>
        </div>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[340px_minmax(0,1fr)]">
        <div className="space-y-4 rounded-md border border-border p-4">
          {sliderFields.map(([key, label]) => (
            <WeightSlider
              key={key}
              label={label}
              value={weights[key]}
              onChange={(value) => setWeights((current) => ({ ...current, [key]: value }))}
            />
          ))}
        </div>

        <div className="min-w-0 space-y-4">
          {loadState === "loading" && !report ? <Skeleton className="h-80 w-full" /> : null}
          {loadState === "error" ? (
            <div className="rounded-md border border-border bg-muted p-4 text-sm leading-6 text-muted-foreground">
              {error}
            </div>
          ) : null}
          {currentScenario ? (
            <>
              <div className="grid gap-3 md:grid-cols-3">
                {(report?.summary_messages ?? [currentScenario.summary]).slice(0, 3).map((message) => (
                  <p key={message} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">
                    {message}
                  </p>
                ))}
              </div>
              <MovementTable results={currentScenario.results} />
              <StabilityPanels report={report} />
            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function WeightSlider({
  label,
  onChange,
  value,
}: {
  label: string;
  onChange: (value: number) => void;
  value: number;
}) {
  return (
    <label className="block">
      <span className="flex items-center justify-between gap-3 text-sm font-semibold text-foreground">
        {label}
        <span className="tabular-nums text-muted-foreground">{Math.round(value * 100)}%</span>
      </span>
      <input
        aria-label={`${label} weight`}
        className="mt-2 w-full accent-primary"
        max={1}
        min={0}
        step={0.05}
        type="range"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function MovementTable({ results }: { results: SensitivityMovement[] }) {
  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="min-w-[760px] w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/60">
            <th className="px-4 py-3 font-semibold text-foreground">School</th>
            <th className="px-4 py-3 font-semibold text-foreground">Rank</th>
            <th className="px-4 py-3 font-semibold text-foreground">Movement</th>
            <th className="px-4 py-3 font-semibold text-foreground">Stability</th>
            <th className="px-4 py-3 font-semibold text-foreground">Drivers</th>
            <th className="px-4 py-3 font-semibold text-foreground">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {results.map((school) => (
            <tr key={school.school_id} className="border-b border-border last:border-b-0">
              <td className="px-4 py-3">
                <p className="font-semibold text-foreground">{school.name}</p>
                <p className="mt-1 text-xs text-muted-foreground">{school.city}, {school.state}</p>
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                #{school.scenario_rank ?? "-"} <span className="text-xs">(base #{school.base_rank ?? "-"})</span>
              </td>
              <td className="px-4 py-3">
                <MovementBadge school={school} />
              </td>
              <td className="px-4 py-3">
                <Badge variant={school.stability === "stable_choice" ? "default" : "muted"}>
                  {school.stability.replaceAll("_", " ")}
                </Badge>
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {school.category_drivers.map((driver) => driver.replace("_", " ")).join(", ") || "weighted fit"}
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {Math.round(school.confidence_score * 100)}%
                {school.confidence_delta ? ` (${formatSigned(school.confidence_delta * 100)} pts)` : ""}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MovementBadge({ school }: { school: SensitivityMovement }) {
  const delta = school.rank_delta ?? 0;
  if (delta > 0) {
    return <Badge variant="default"><ArrowUp className="h-3.5 w-3.5" aria-hidden="true" /> Up {delta}</Badge>;
  }
  if (delta < 0) {
    return <Badge variant="muted"><ArrowDown className="h-3.5 w-3.5" aria-hidden="true" /> Down {Math.abs(delta)}</Badge>;
  }
  return <Badge variant="muted"><Minus className="h-3.5 w-3.5" aria-hidden="true" /> No change</Badge>;
}

function StabilityPanels({ report }: { report: SensitivityResponse | null }) {
  if (!report) return null;
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-md bg-muted p-4">
        <h3 className="flex items-center gap-2 font-semibold text-foreground">
          <Zap className="h-4 w-4 text-primary" aria-hidden="true" />
          Stable choices
        </h3>
        <p className="mt-2 text-xs leading-5 text-muted-foreground">{report.stable_choice_definition}</p>
        <div className="mt-3 space-y-2">
          {(report.stable_schools.length ? report.stable_schools : []).map((school) => (
            <p key={school.school_id} className="text-sm text-muted-foreground">
              <span className="font-semibold text-foreground">{school.name}</span> avg rank {school.average_rank}
            </p>
          ))}
          {!report.stable_schools.length ? <p className="text-sm text-muted-foreground">No clearly stable choice yet.</p> : null}
        </div>
      </div>
      <div className="rounded-md bg-muted p-4">
        <h3 className="font-semibold text-foreground">Volatile choices</h3>
        <p className="mt-2 text-xs leading-5 text-muted-foreground">{report.volatile_choice_definition}</p>
        <div className="mt-3 space-y-2">
          {report.volatile_schools.map((school) => (
            <p key={school.school_id} className="text-sm text-muted-foreground">
              <span className="font-semibold text-foreground">{school.name}</span> moved up to {school.max_rank_delta} ranks
            </p>
          ))}
          {!report.volatile_schools.length ? <p className="text-sm text-muted-foreground">No highly volatile school in these scenarios.</p> : null}
        </div>
      </div>
    </div>
  );
}

function formatSigned(value: number) {
  const rounded = Math.round(value);
  if (rounded === 0) return "0";
  return rounded > 0 ? `+${rounded}` : String(rounded);
}
