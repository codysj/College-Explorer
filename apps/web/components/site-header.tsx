"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

// The journey in order: tell us what matters, explore, keep a shortlist, compare, decide.
const links = [
  { href: "/onboarding", label: "Preferences" },
  { href: "/search", label: "Explore" },
  { href: "/dashboard", label: "Saved" },
  { href: "/compare", label: "Compare" },
  { href: "/decision", label: "Decide" },
] as const;

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="border-b border-border bg-white/80 backdrop-blur print:hidden">
      <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-3 sm:px-8">
        <Link className="text-sm font-semibold text-foreground" href="/">
          College Exploration
        </Link>
        <nav aria-label="Main">
          <ul className="flex flex-wrap gap-1">
            {links.map(({ href, label }) => {
              const active = pathname === href || pathname.startsWith(`${href}/`);
              return (
                <li key={href}>
                  <Link
                    aria-current={active ? "page" : undefined}
                    className={cn(
                      "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:text-foreground",
                    )}
                    href={href}
                  >
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </header>
  );
}
