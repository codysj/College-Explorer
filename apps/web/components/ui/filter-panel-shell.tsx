import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type FilterPanelShellProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function FilterPanelShell({
  actions,
  children,
  className,
  description,
  title,
}: FilterPanelShellProps) {
  return (
    <aside className={cn("rounded-lg border border-border bg-white p-5", className)}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold tracking-normal text-foreground">{title}</h2>
          {description ? (
            <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      <div className="mt-5 space-y-5">{children}</div>
    </aside>
  );
}
