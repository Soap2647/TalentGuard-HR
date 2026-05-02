import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { Search, Filter } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Card, CardBody, Input, Select, Spinner } from "@/components/ui";
import { fmtPct, riskColor } from "@/lib/utils";

const PAGE = 25;

export default function Employees() {
  const [sp, setSp] = useSearchParams();
  const [q, setQ] = useState(sp.get("q") || "");
  const [risk, setRisk] = useState(sp.get("risk") || "");
  const [page, setPage] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ["employees", q, risk, page],
    queryFn: () =>
      api
        .get("/employees", { params: { q: q || undefined, risk: risk || undefined, limit: PAGE, offset: page * PAGE } })
        .then((r) => r.data),
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const pages = Math.ceil(total / PAGE);

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-4">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Çalışanlar</h1>
          <p className="text-sm text-slate-500">Toplam {total} kayıt</p>
        </div>
      </header>

      <Card>
        <CardBody>
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[220px]">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="İsim veya e-posta ara..."
                value={q}
                onChange={(e) => {
                  setQ(e.target.value);
                  setPage(0);
                  const next = new URLSearchParams(sp);
                  e.target.value ? next.set("q", e.target.value) : next.delete("q");
                  setSp(next);
                }}
                className="pl-9"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-slate-400" />
              <Select
                value={risk}
                onChange={(e) => {
                  setRisk(e.target.value);
                  setPage(0);
                  const next = new URLSearchParams(sp);
                  e.target.value ? next.set("risk", e.target.value) : next.delete("risk");
                  setSp(next);
                }}
                className="w-44"
              >
                <option value="">Tüm Riskler</option>
                <option value="high">Yüksek</option>
                <option value="medium">Orta</option>
                <option value="low">Düşük</option>
              </Select>
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardBody className="p-0 overflow-x-auto">
          {isLoading ? (
            <div className="p-12 grid place-items-center"><Spinner /></div>
          ) : items.length === 0 ? (
            <div className="p-12 text-center text-sm text-slate-500">Sonuç yok.</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="text-left p-3">No</th>
                  <th className="text-left p-3">Ad Soyad</th>
                  <th className="text-left p-3">Departman</th>
                  <th className="text-left p-3">Pozisyon</th>
                  <th className="text-right p-3">Maaş</th>
                  <th className="text-center p-3">Memnun.</th>
                  <th className="text-right p-3">Risk</th>
                  <th className="text-center p-3">Seviye</th>
                </tr>
              </thead>
              <tbody>
                {items.map((e: any) => (
                  <tr key={e.id} className="border-t border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/30">
                    <td className="p-3 text-slate-500">#{e.employee_number}</td>
                    <td className="p-3 font-medium">
                      <Link to={`/employees/${e.id}`} className="hover:text-brand-600">{e.full_name}</Link>
                    </td>
                    <td className="p-3 text-slate-600 dark:text-slate-400">{e.department}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-400">{e.job_role}</td>
                    <td className="p-3 text-right tabular-nums">${Number(e.monthly_income || 0).toLocaleString()}</td>
                    <td className="p-3 text-center">{e.job_satisfaction ?? "-"}/4</td>
                    <td className="p-3 text-right tabular-nums font-medium">
                      {e.latest_churn_prob != null ? fmtPct(Number(e.latest_churn_prob)) : "—"}
                    </td>
                    <td className="p-3 text-center">
                      {e.latest_risk_level ? <Badge className={riskColor(e.latest_risk_level)}>{e.latest_risk_level}</Badge> : <span className="text-xs text-slate-400">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>

      {pages > 1 && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">Sayfa {page + 1} / {pages}</span>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1.5 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-50"
            >
              Önceki
            </button>
            <button
              disabled={page + 1 >= pages}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1.5 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-50"
            >
              Sonraki
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
