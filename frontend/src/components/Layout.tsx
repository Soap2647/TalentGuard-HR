import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Sparkles,
  ShieldCheck,
  History,
  UserCog,
  LogOut,
  Moon,
  Sun,
  Brain,
} from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { getUser } from "@/lib/api";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "hr", "manager"] },
  { to: "/employees", label: "Çalışanlar", icon: Users, roles: ["admin", "hr", "manager"] },
  { to: "/predict", label: "Tahmin", icon: Sparkles, roles: ["admin", "hr", "manager"] },
  { to: "/models", label: "Model Yönetimi", icon: Brain, roles: ["admin"] },
  { to: "/audit", label: "Audit Log", icon: History, roles: ["admin"] },
  { to: "/users", label: "Kullanıcılar", icon: UserCog, roles: ["admin"] },
];

export default function Layout() {
  const nav = useNavigate();
  const user = getUser();
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    nav("/login");
  };

  if (!user) {
    nav("/login");
    return null;
  }

  return (
    <div className="flex min-h-screen bg-transparent">
      <aside className="w-64 shrink-0 m-4 rounded-3xl glass-panel flex flex-col overflow-hidden relative z-20 shadow-glass">
        <div className="p-6 flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/50 relative z-10">
          <div className="p-2.5 bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl shadow-lg shadow-brand-500/30">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="text-base font-heading font-bold leading-tight text-slate-800 dark:text-white">TalentGuard</div>
            <div className="text-[10px] text-brand-600 dark:text-brand-400 font-bold uppercase tracking-widest mt-0.5">Enterprise</div>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-1.5 relative z-10">
          {NAV.filter((n) => n.roles.includes(user.role)).map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300 group",
                  isActive
                    ? "bg-brand-500/10 text-brand-700 dark:text-brand-300 shadow-[inset_4px_0_0_0_rgba(139,92,246,1)]"
                    : "text-slate-600 hover:bg-slate-100/50 dark:text-slate-400 dark:hover:bg-slate-800/50 hover:translate-x-1",
                )
              }
            >
              {({ isActive }) => (
                <>
                  <n.icon className={cn("h-5 w-5 transition-colors", isActive ? "text-brand-600 dark:text-brand-400" : "text-slate-400 group-hover:text-brand-500/70")} />
                  {n.label}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-200/50 dark:border-slate-800/50 relative z-10 bg-slate-50/30 dark:bg-slate-900/30">
          <div className="px-3 py-3">
            <div className="font-heading font-semibold text-sm text-slate-800 dark:text-slate-200">{user.full_name}</div>
            <div className="text-xs text-brand-600 dark:text-brand-400 font-medium mt-0.5 capitalize">{user.role}</div>
          </div>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setDark((d) => !d)}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl p-2.5 text-xs font-medium bg-white/60 dark:bg-slate-800/60 hover:bg-white dark:hover:bg-slate-700 transition-all border border-slate-200/50 dark:border-slate-700/50 shadow-sm hover:shadow-md"
            >
              {dark ? <Sun className="h-4 w-4 text-amber-500" /> : <Moon className="h-4 w-4 text-brand-500" />}
              {dark ? "Açık" : "Koyu"}
            </button>
            <button
              onClick={logout}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl p-2.5 text-xs font-medium text-red-600 bg-red-50/60 dark:bg-red-900/30 hover:bg-red-100 dark:hover:bg-red-900/50 transition-all border border-red-200/50 dark:border-red-900/50 shadow-sm hover:shadow-md"
            >
              <LogOut className="h-4 w-4" />
              Çıkış
            </button>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto animate-fade-in-up relative z-10 py-4 pr-4">
        <Outlet />
      </main>
    </div>
  );
}
