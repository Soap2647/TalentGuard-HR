import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Link } from "react-router-dom";
import { TrendingUp, AlertTriangle, Clock, Users as UsersIcon } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Card, CardBody, CardHeader, CardTitle, KpiCard, Spinner } from "@/components/ui";
import { fmtPct, riskColor } from "@/lib/utils";

const RISK_COLORS: Record<string, string> = { high: "#dc2626", medium: "#f59e0b", low: "#10b981" };

export default function Dashboard() {
  const kpis = useQuery({ queryKey: ["kpis"], queryFn: () => api.get("/dashboard/kpis").then((r) => r.data) });
  const dept = useQuery({
    queryKey: ["dept-attrition"],
    queryFn: () => api.get("/dashboard/department-attrition").then((r) => r.data),
  });
  const monthly = useQuery({
    queryKey: ["monthly"],
    queryFn: () => api.get("/dashboard/monthly-predictions").then((r) => r.data),
  });
  const risk = useQuery({
    queryKey: ["risk-dist"],
    queryFn: () => api.get("/dashboard/risk-distribution").then((r) => r.data),
  });
  const high = useQuery({
    queryKey: ["high-risk"],
    queryFn: () => api.get("/dashboard/high-risk?limit=10").then((r) => r.data),
  });

  if (kpis.isLoading) return <Centered><Spinner /></Centered>;

  const k = kpis.data || {};

  return (
    <div className="p-6 space-y-8 max-w-[1400px] mx-auto animate-fade-in-up">
      <header className="mb-2">
        <h1 className="text-3xl font-heading font-bold tracking-tight text-slate-800 dark:text-white">Genel Bakış</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Çalışan ayrılma riskine genel bakış ve son tahminler.</p>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard label="Toplam Çalışan" value={k.total_employees ?? "-"} hint={<><UsersIcon className="inline h-3 w-3 mr-1" />Aktif kayıt</>} />
        <KpiCard label="Yüksek Risk" value={k.high_risk_count ?? "-"} hint="risk_level = high" />
        <KpiCard label="Ortalama Tenure" value={k.avg_tenure ? `${k.avg_tenure} yıl` : "-"} hint={<><Clock className="inline h-3 w-3 mr-1" />years_at_company</>} />
        <KpiCard label="Genel Attrition" value={k.overall_attrition ? `%${k.overall_attrition}` : "-"} hint={<><TrendingUp className="inline h-3 w-3 mr-1" />Tarihsel</>} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Departman Bazlı Attrition Oranı (%)</CardTitle></CardHeader>
          <CardBody>
            {dept.data && dept.data.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={dept.data}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                  <XAxis dataKey="department" tick={{ fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={60} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="attrition_rate_pct" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <Empty />}
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Risk Dağılımı</CardTitle></CardHeader>
          <CardBody>
            {risk.data && risk.data.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={risk.data}
                    dataKey="count"
                    nameKey="risk"
                    innerRadius={60}
                    outerRadius={95}
                    paddingAngle={3}
                  >
                    {risk.data.map((d: any, i: number) => (
                      <Cell key={i} fill={RISK_COLORS[d.risk] || "#94a3b8"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : <Empty msg="Henüz tahmin yok. Çalışan detayında 'Tahmin Et' butonunu kullanın." />}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Aylık Tahmin Trendi</CardTitle></CardHeader>
        <CardBody>
          {monthly.data && monthly.data.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={[...monthly.data].reverse()}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200/50 dark:stroke-slate-800/50" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="high_risk" name="Yüksek Risk" fill="#dc2626" radius={[4, 4, 0, 0]} maxBarSize={40} />
                <Bar dataKey="medium_risk" name="Orta Risk" fill="#f59e0b" radius={[4, 4, 0, 0]} maxBarSize={40} />
                <Bar dataKey="low_risk" name="Düşük Risk" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          ) : <Empty />}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle><AlertTriangle className="inline h-4 w-4 mr-2 text-red-600" />En Yüksek Riskli Çalışanlar</CardTitle>
            <Link to="/employees?risk=high" className="text-xs text-brand-600 hover:underline">Tümü</Link>
          </div>
        </CardHeader>
        <CardBody className="p-0">
          {high.data && high.data.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="bg-slate-100/50 dark:bg-slate-800/30 text-[10px] font-heading font-semibold tracking-wider text-slate-500 dark:text-slate-400 uppercase">
                <tr>
                  <th className="text-left p-4">Çalışan</th>
                  <th className="text-left p-4">Departman</th>
                  <th className="text-left p-4">Pozisyon</th>
                  <th className="text-right p-4">Churn Olasılığı</th>
                  <th className="text-center p-4">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
                {high.data.map((r: any) => (
                  <tr key={r.employee_id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors group">
                    <td className="p-4 font-medium">
                      <Link to={`/employees/${r.employee_id}`} className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">{r.full_name}</Link>
                    </td>
                    <td className="p-3 text-slate-600 dark:text-slate-400">{r.department}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-400">{r.job_role}</td>
                    <td className="p-3 text-right font-semibold">{fmtPct(Number(r.churn_prob))}</td>
                    <td className="p-3 text-center"><Badge className={riskColor(r.risk_level)}>{r.risk_level}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <div className="p-6"><Empty msg="Henüz yüksek riskli kayıt yok. /api/predictions/batch ile toplu tahmin tetikleyebilirsiniz." /></div>}
        </CardBody>
      </Card>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="min-h-[60vh] grid place-items-center">{children}</div>;
}
function Empty({ msg = "Veri yok" }: { msg?: string }) {
  return <div className="text-center text-sm text-slate-500 py-10">{msg}</div>;
}
