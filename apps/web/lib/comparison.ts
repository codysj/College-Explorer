import type { SchoolProfile } from "@/types/api";

export type ComparisonWinner = {
  category: "academic fit" | "cost fit" | "career fit" | "campus fit";
  school: SchoolProfile | null;
  reason: string;
};

export type ComparisonSummary = {
  bestOverallFit: SchoolProfile | null;
  bestValue: SchoolProfile | null;
  strongestCareerOutcome: SchoolProfile | null;
  biggestTradeoff: string;
  winners: ComparisonWinner[];
  tradeoffs: string[];
};

export function buildComparisonSummary(schools: SchoolProfile[]): ComparisonSummary {
  const bestOverallFit = maxBy(schools, (school) => school.fit_score ?? school.data_confidence_score * 100);
  const bestValue = minBy(schools, (school) => school.cost.net_price);
  const strongestCareerOutcome = maxBy(schools, (school) => school.outcomes.median_earnings);

  return {
    bestOverallFit,
    bestValue,
    strongestCareerOutcome,
    biggestTradeoff: buildBiggestTradeoff(schools),
    winners: [
      {
        category: "academic fit",
        school: maxBy(schools, (school) => school.academics.graduation_rate),
        reason: "Highest known graduation rate.",
      },
      {
        category: "cost fit",
        school: bestValue,
        reason: "Lowest known net price.",
      },
      {
        category: "career fit",
        school: strongestCareerOutcome,
        reason: "Highest known median earnings.",
      },
      {
        category: "campus fit",
        school: maxBy(schools, (school) => {
          const housingScore = school.campus_life.housing ? 1 : 0;
          const cultureScore = school.campus_life.culture_tags?.length ?? 0;
          return housingScore + cultureScore / 10;
        }),
        reason: "Most known campus-life signals in the current profile data.",
      },
    ],
    tradeoffs: buildTradeoffs(schools),
  };
}

function buildBiggestTradeoff(schools: SchoolProfile[]) {
  if (schools.length < 2) return "Add at least two schools to compare tradeoffs.";

  const cheapest = minBy(schools, (school) => school.cost.net_price);
  const highestEarnings = maxBy(schools, (school) => school.outcomes.median_earnings);
  if (cheapest && highestEarnings && cheapest.school_id !== highestEarnings.school_id) {
    return `${cheapest.name} has the lowest known net price, while ${highestEarnings.name} has the strongest known earnings outcome.`;
  }

  const highestGrad = maxBy(schools, (school) => school.academics.graduation_rate);
  const mostAccessible = maxBy(schools, (school) => school.acceptance_rate);
  if (highestGrad && mostAccessible && highestGrad.school_id !== mostAccessible.school_id) {
    return `${highestGrad.name} leads on graduation rate, while ${mostAccessible.name} is the most accessible by acceptance rate.`;
  }

  return "The selected schools are close on the currently available V1 comparison signals.";
}

function buildTradeoffs(schools: SchoolProfile[]) {
  if (schools.length < 2) return ["Select another school to generate deterministic side-by-side tradeoffs."];

  const tradeoffs: string[] = [];
  const cheapest = minBy(schools, (school) => school.cost.net_price);
  const highestCost = maxBy(schools, (school) => school.cost.net_price);
  const highestGrad = maxBy(schools, (school) => school.academics.graduation_rate);
  const mostAccessible = maxBy(schools, (school) => school.acceptance_rate);
  const highestEarnings = maxBy(schools, (school) => school.outcomes.median_earnings);

  if (cheapest && highestCost && cheapest.school_id !== highestCost.school_id) {
    tradeoffs.push(`${cheapest.name} is the lowest known net price; ${highestCost.name} is the highest among this set.`);
  }
  if (highestGrad && mostAccessible && highestGrad.school_id !== mostAccessible.school_id) {
    tradeoffs.push(`${highestGrad.name} has the strongest graduation rate; ${mostAccessible.name} has the highest acceptance rate.`);
  }
  if (highestEarnings) {
    tradeoffs.push(`${highestEarnings.name} leads on known median earnings, using deterministic profile data only.`);
  }

  return tradeoffs.length > 0
    ? tradeoffs
    : ["Current profile data is too sparse to identify a clear tradeoff without inventing facts."];
}

function maxBy(schools: SchoolProfile[], selector: (school: SchoolProfile) => number | null | undefined) {
  return schools.reduce<SchoolProfile | null>((best, school) => {
    const value = selector(school);
    if (value === null || value === undefined) return best;
    if (!best) return school;
    const bestValue = selector(best);
    if (bestValue === null || bestValue === undefined) return school;
    return value > bestValue ? school : best;
  }, null);
}

function minBy(schools: SchoolProfile[], selector: (school: SchoolProfile) => number | null | undefined) {
  return schools.reduce<SchoolProfile | null>((best, school) => {
    const value = selector(school);
    if (value === null || value === undefined) return best;
    if (!best) return school;
    const bestValue = selector(best);
    if (bestValue === null || bestValue === undefined) return school;
    return value < bestValue ? school : best;
  }, null);
}
