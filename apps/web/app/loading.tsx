import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-5 py-8 sm:px-8">
      <Skeleton className="h-10 w-48" />
      <section className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-5">
          <Skeleton className="h-14 w-full max-w-2xl" />
          <Skeleton className="h-24 w-full max-w-3xl" />
          <Skeleton className="h-12 w-72" />
        </div>
        <Skeleton className="h-80 w-full" />
      </section>
    </main>
  );
}
