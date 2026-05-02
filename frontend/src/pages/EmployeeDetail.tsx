import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Sparkles } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { Badge, Button, Card, CardBody, CardHeader, CardTitle, Spinner } from "@/components/ui";
import { fmtPct, riskColor } from "@/lib/utils";

export default function EmployeeDetail() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["employee", id],
    queryFn: () => api.get(`/employees/${id}`).then((r) => r.data),
  });

  const predict = useMutation({
    mutationFn: () => api.post(`/predictions/employee/${id}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["employee", id] }),
  });

  if (isLoading) return <div className="min-h-[60vh] grid place-items-center"><Spinner /></div>;
  if (!data) return <div className="p-6">Bulunamadı</div>;

  const e = data.employee;
  const m = data.metric;
  const latest = data.risk_history?.[0];
  const shapTop = latest?.shap_values?.top_features || predict.data?.shap_values?.top_features || [];

  return (
    <div className="p-6 max-w-[1300px] mx-auto space-y-6">
      <Link to="/employees" className="inline-flex items-center text-sm text-slate-500 hover:text-brand-600">
        <ArrowLeft className="h-4 w-4 mr-1" /> Listeye dön
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {e.first_name} {e.last_name}
          </h1>
          <p className="text-sm text-slate-500">
            #{e.employee_number} • {data.department} • {data.job_role}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {latest && (
            <div className="text-right">
              <div className="text-xs text-slate-500">Son tahmin</div>
              <div className="text-lg font-bold">{fmtPct(Number(latest.churn_prob))}</div>
              <Badge className={riskColor(latest.risk_level)}>{latest.risk_level}</Badge>
            </div>
          )}
          <Button onClick={() => predict.mutate()} disabled={predict.isPending}>
            <Sparkles className="h-4 w-4" />
            {predict.isPending ? "Hesaplanıyor..." : "Yeniden Tahmin Et"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader><CardTitle>Profil</CardTitle></CardHeader>
          <CardBody className="space-y-2 text-sm">
            <Row k="Yaş" v={e.age} />
            <Row k="Cinsiyet" v={e.gender} />
            <Row k="Medeni Durum" v={e.marital_status} />
            <Row k="Eğitim Seviyesi" v={e.education} />
            <Row k="Eğitim Alanı" v={e.education_field} />
            <Row k="İşe Başlama" v={e.hire_date} />
            <Row k="Şirkette Kıdem" v={`${e.years_at_company} yıl`} />
            <Row k="Mesai" v={e.overtime ? "Evet" : "Hayır"} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Güncel Metrikler</CardTitle></CardHeader>
          <CardBody className="space-y-2 text-sm">
            {m ? (
              <>
                <Row k="Aylık Maaş" v={`$${Number(m.monthly_income).toLocaleString()}`} />
                <Row k="Zam %" v={`${m.percent_salary_hike ?? "-"}`} />
                <Row k="İş Tatmini" v={`${m.job_satisfaction ?? "-"} / 4`} />
                <Row k="İş Yaşam Dengesi" v={`${m.work_life_balance ?? "-"} / 4`} />
                <Row k="Çevre Tatmini" v={`${m.environment_satisfaction ?? "-"} / 4`} />
                <Row k="Performans" v={`${m.performance_rating ?? "-"} / 4`} />
                <Row k="Eğitim Sayısı" v={m.training_times_last_year} />
              </>
            ) : <div className="text-slate-500">Metrik kaydı yok.</div>}
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Risk Geçmişi</CardTitle></CardHeader>
          <CardBody>
            {data.risk_history?.length ? (
              <div className="space-y-2 text-sm">
                {data.risk_history.slice(0, 8).map((h: any, i: number) => (
                  <div key={i} className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2 last:border-0">
                    <div>
                      <div className="text-xs text-slate-500">{new Date(h.predicted_at).toLocaleString()}</div>
                      <div className="text-xs text-slate-400">{h.model_version}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{fmtPct(Number(h.churn_prob))}</span>
                      <Badge className={riskColor(h.risk_level)}>{h.risk_level}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : <div className="text-sm text-slate-500">Henüz tahmin yok. Sağ üstten 'Yeniden Tahmin Et' butonuna basın.</div>}
          </CardBody>
        </Card>
      </div>

      {shapTop.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Risk Faktörleri (SHAP)</CardTitle></CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={shapTop} layout="vertical" margin={{ left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="feature" tick={{ fontSize: 11 }} width={150} />
                <Tooltip />
                <Bar dataKey="shap" radius={[0, 6, 6, 0]}>
                  {shapTop.map((d: any, i: number) => (
                    <Cell key={i} fill={d.shap > 0 ? "#dc2626" : "#10b981"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-slate-500 mt-2">
              Pozitif (kırmızı) değerler riski artırıyor; negatif (yeşil) değerler azaltıyor.
            </p>
          </CardBody>
        </Card>
      )}
    </div>
  );
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-1.5 last:border-0">
      <span className="text-slate-500">{k}</span>
      <span className="font-medium text-right">{v ?? "-"}</span>
    </div>
  );
}
