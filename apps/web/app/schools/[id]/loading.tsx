import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-16 pt-8 sm:px-8">
      <Skeleton className="h-5 w-32" />
      <section className="mt-6 rounded-lg border border-border bg-white p-6 shadow-soft">
        <Skeleton className="h-6 w-36" />
        <Skeleton className="mt-5 h-12 w-3/4" />
        <Skeleton className="mt-3 h-5 w-72" />
      </section>
      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          {Array.from({ length: 4 }, (_, index) => (
            <Card key={index}>
              <CardHeader>
                <Skeleton className="h-7 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-40 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    </main>
  );
}
