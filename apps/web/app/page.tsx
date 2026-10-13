import { ArrowRight, CheckCircle2, Compass, Search } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricRow } from "@/components/ui/metric-row";
import { ScorePill } from "@/components/ui/score-pill";

// A real engine result, not a mock-up: UC San Diego scored by ranking v1.4 on data version
// scorecard-2023.4 for the sample student named on the card. Re-run it if either changes.
const reasons = [
  "Net price is inside the $25,000 budget",
  "Offers Biology, one of its three largest programs",
  "Median earnings of $84,943 ten years after entry",
];

export default function Home() {
  return (
    <main className="min-h-screen">
      <section className="mx-auto grid w-full max-w-6xl gap-10 px-5 pb-14 pt-8 sm:px-8 lg:grid-cols-[1fr_390px] lg:pb-20 lg:pt-10">
        <div className="flex flex-col justify-center">
          <div className="mb-7 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Compass className="h-5 w-5" aria-hidden="true" />
            </div>
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
              College Exploration
            </span>
          </div>

          <Badge className="mb-5 w-fit" variant="outline">
            Transparent college decision support
          </Badge>
          <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-foreground sm:text-5xl lg:text-6xl">
            Build a college shortlist from fit, facts, and honest tradeoffs.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg">
            Rank US universities by what matters to you, using federal College Scorecard
            data. Every score shows its reasons, its tradeoffs, and what the data does not cover.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/onboarding">
                Build my shortlist
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link href="/search">
                <Search className="h-4 w-4" aria-hidden="true" />
                Explore schools
              </Link>
            </Button>
          </div>

          <p className="mt-6 max-w-2xl text-sm leading-6 text-muted-foreground">
            This product is data-driven decision support. It is not admissions
            advice, a guarantee of admission, financial advice, or a promise of
            return on investment.
          </p>
        </div>

        <Card className="self-center">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <Badge variant="accent">Sample result</Badge>
                <CardTitle className="mt-4">University of California-San Diego</CardTitle>
                <p className="mt-1 text-sm text-muted-foreground">
                  Public, urban, 33,787 undergraduates
                </p>
              </div>
              <ScorePill score={91} label="Fit" />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              {reasons.map((reason) => (
                <div key={reason} className="flex gap-3 text-sm leading-6">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>

            <div className="rounded-md border border-border bg-warning p-4 text-warning-foreground">
              <p className="text-sm font-semibold">Tradeoff to inspect</p>
              <p className="mt-1 text-sm leading-6">
                A 25% admit rate is more selective than a balanced list calls for, so pair it
                with likelier options.
              </p>
            </div>

            <div className="space-y-3 border-t border-border pt-5">
              <MetricRow label="Net price" value="$11,750" detail="2023" />
              <MetricRow label="Graduation rate" value="88%" detail="2023" />
              <MetricRow label="Median debt" value="$15,500" detail="2020" />
            </div>
            <p className="text-xs leading-5 text-muted-foreground">
              For a sample student: Biology, from California, up to $25,000 a year.
            </p>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
