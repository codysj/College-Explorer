// One set of display formatters, so a missing value reads the same on every page.
// Missing is "Unknown", never 0: the data contract keeps unreported values null.
const MISSING = "Unknown";

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const integer = new Intl.NumberFormat("en-US");

export function formatCurrency(value: number | null | undefined) {
  return value === null || value === undefined ? MISSING : currency.format(value);
}

export function formatNumber(value: number | null | undefined) {
  return value === null || value === undefined ? MISSING : integer.format(value);
}

/** A 0-1 rate as a whole percentage. */
export function formatPercent(value: number | null | undefined) {
  return value === null || value === undefined ? MISSING : `${Math.round(value * 100)}%`;
}
