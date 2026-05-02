import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function riskColor(level?: string | null): string {
  if (level === "high") return "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300";
  if (level === "medium") return "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300";
  if (level === "low") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300";
  return "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400";
}

export function fmtPct(n?: number | null): string {
  if (n == null) return "-";
  return (n * 100).toFixed(1) + "%";
}
