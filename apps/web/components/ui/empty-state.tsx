import { Inbox } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
  /** h2 by default: most pages already have their own h1. */
  headingLevel?: "h1" | "h2";
};

export function EmptyState({ action, className, description, headingLevel = "h2", title }: EmptyStateProps) {
  const Heading = headingLevel;
  return (
    <div
      className={cn(
        "flex flex-col items-center rounded-lg border border-dashed border-border bg-white p-8 text-center",
        className,
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-md bg-muted text-muted-foreground">
        <Inbox className="h-6 w-6" aria-hidden="true" />
      </div>
      <Heading className="mt-5 text-xl font-semibold tracking-normal text-foreground">{title}</Heading>
      <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">{description}</p>
      {action ? (
        <Button asChild className="mt-6" variant="secondary">
          {action}
        </Button>
      ) : null}
    </div>
  );
}
