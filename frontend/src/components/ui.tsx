import React, { ButtonHTMLAttributes, HTMLAttributes, InputHTMLAttributes, SelectHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

/* ---------------- Card ---------------- */
export function Card({ className, ...p }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl glass-panel transition-all duration-300 hover:shadow-glass-hover hover:-translate-y-1",
        className,
      )}
      {...p}
    />
  );
}
export function CardHeader({ className, ...p }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 border-b border-slate-200/50 dark:border-slate-800/50", className)} {...p} />;
}
export function CardTitle({ className, ...p }: HTMLAttributes<HTMLDivElement>) {
  return <h3 className={cn("text-lg font-heading font-semibold tracking-tight text-slate-800 dark:text-white", className)} {...p} />;
}
export function CardBody({ className, ...p }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6", className)} {...p} />;
}

/* ---------------- Button ---------------- */
type Variant = "primary" | "secondary" | "ghost" | "danger";
const variants: Record<Variant, string> = {
  primary: "bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white shadow-lg shadow-brand-500/30 hover:shadow-brand-500/50 border border-brand-400/20",
  secondary: "bg-slate-100/80 hover:bg-slate-200 text-slate-900 dark:bg-slate-800/80 dark:hover:bg-slate-700 dark:text-slate-100 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50",
  ghost: "hover:bg-slate-100/50 dark:hover:bg-slate-800/50 backdrop-blur-sm",
  danger: "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 border border-red-400/20",
};

export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }>(
  ({ className, variant = "primary", ...p }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] active:scale-[0.98]",
        variants[variant],
        className,
      )}
      {...p}
    />
  ),
);
Button.displayName = "Button";

/* ---------------- Input / Select / Label ---------------- */
export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(({ className, ...p }, ref) => (
  <input
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-slate-200/60 dark:border-slate-700/60 bg-white/50 dark:bg-slate-900/50 px-4 py-2.5 text-sm backdrop-blur-sm transition-all duration-300",
      "focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/20 focus:bg-white dark:focus:bg-slate-900",
      className,
    )}
    {...p}
  />
));
Input.displayName = "Input";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(({ className, ...p }, ref) => (
  <select
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-slate-200/60 dark:border-slate-700/60 bg-white/50 dark:bg-slate-900/50 px-4 py-2.5 text-sm backdrop-blur-sm transition-all duration-300",
      "focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/20 focus:bg-white dark:focus:bg-slate-900",
      className,
    )}
    {...p}
  />
));
Select.displayName = "Select";

export function Label({ className, ...p }: HTMLAttributes<HTMLLabelElement>) {
  return <label className={cn("text-xs font-medium text-slate-600 dark:text-slate-400", className)} {...p} />;
}

/* ---------------- Badge ---------------- */
export function Badge({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        className,
      )}
    >
      {children}
    </span>
  );
}

/* ---------------- KPI ---------------- */
export function KpiCard({ label, value, hint }: { label: string; value: string | number; hint?: React.ReactNode }) {
  return (
    <Card className="overflow-hidden relative group">
      <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 rounded-full bg-brand-500/10 blur-2xl group-hover:bg-brand-500/20 transition-all duration-500" />
      <CardBody className="relative z-10">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 font-heading">{label}</div>
        <div className="mt-3 text-4xl font-bold tracking-tight text-slate-800 dark:text-white">{value}</div>
        {hint && <div className="mt-2 text-xs font-medium text-slate-500 dark:text-slate-400">{hint}</div>}
      </CardBody>
    </Card>
  );
}

/* ---------------- Spinner ---------------- */
export function Spinner({ className }: { className?: string }) {
  return (
    <div
      className={cn("h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600", className)}
    />
  );
}
