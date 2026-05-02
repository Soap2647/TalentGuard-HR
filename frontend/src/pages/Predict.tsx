import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { Badge, Button, Card, CardBody, CardHeader, CardTitle, Input, Label, Select } from "@/components/ui";
import { fmtPct, riskColor } from "@/lib/utils";

const DEFAULT = {
  age: 35,
  gender: "Male",
  marital_status: "Married",
  education: 3,
  education_field: "Life Sciences",
  department: "Research & Development",
  job_role: "Research Scientist",
  business_travel: "Travel_Rarely",
  distance_from_home: 5,
  years_at_company: 5,
  years_in_current_role: 3,
  years_since_last_promotion: 1,
  years_with_curr_manager: 3,
  total_working_years: 10,
  num_companies_worked: 2,
  monthly_income: 5000,
  percent_salary_hike: 13,
  stock_option_level: 1,
  job_satisfaction: 3,
  environment_satisfaction: 3,
  relationship_satisfaction: 3,
  work_life_balance: 3,
  job_involvement: 3,
  performance_rating: 3,
  training_times_last_year: 2,
  overtime: false,
};

export default function Predict() {
  const [form, setForm] = useState(DEFAULT);
  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const m = useMutation({
    mutationFn: () => api.post("/predictions/adhoc", form).then((r) => r.data),
  });

  const result = m.data;

  return (
    <div className="p-6 max-w-[1300px] mx-auto space-y-4">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Senaryo Tahmini (What-if)</h1>
        <p className="text-sm text-slate-500">Bir çalışan profili gir — model anında churn olasılığını ve risk faktörlerini açıklar.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Profil & Metrikler</CardTitle></CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <Field label="Yaş" type="number" v={form.age} on={(v) => set("age", +v)} />
              <FieldSelect label="Cinsiyet" v={form.gender} on={(v) => set("gender", v)} options={["Male", "Female"]} />
              <FieldSelect label="Medeni Durum" v={form.marital_status} on={(v) => set("marital_status", v)} options={["Single", "Married", "Divorced"]} />
              <FieldSelect label="Departman" v={form.department} on={(v) => set("department", v)} options={["Sales", "Research & Development", "Human Resources"]} />
              <Field label="Pozisyon" v={form.job_role} on={(v) => set("job_role", v)} />
              <FieldSelect label="Seyahat" v={form.business_travel} on={(v) => set("business_travel", v)} options={["Non-Travel", "Travel_Rarely", "Travel_Frequently"]} />
              <FieldSelect label="Eğitim Alanı" v={form.education_field} on={(v) => set("education_field", v)} options={["Life Sciences", "Medical", "Marketing", "Technical Degree", "Human Resources", "Other"]} />
              <Field label="Eğitim (1-5)" type="number" v={form.education} on={(v) => set("education", +v)} />
              <Field label="Eve Uzaklık (km)" type="number" v={form.distance_from_home} on={(v) => set("distance_from_home", +v)} />
              <Field label="Şirkette Yıl" type="number" v={form.years_at_company} on={(v) => set("years_at_company", +v)} />
              <Field label="Mevcut Rolde Yıl" type="number" v={form.years_in_current_role} on={(v) => set("years_in_current_role", +v)} />
              <Field label="Son Terfi Üzerinden" type="number" v={form.years_since_last_promotion} on={(v) => set("years_since_last_promotion", +v)} />
              <Field label="Mevcut Yöneticiyle Yıl" type="number" v={form.years_with_curr_manager} on={(v) => set("years_with_curr_manager", +v)} />
              <Field label="Toplam Çalışma Yılı" type="number" v={form.total_working_years} on={(v) => set("total_working_years", +v)} />
              <Field label="Önceki Şirket Sayısı" type="number" v={form.num_companies_worked} on={(v) => set("num_companies_worked", +v)} />
              <Field label="Aylık Maaş ($)" type="number" v={form.monthly_income} on={(v) => set("monthly_income", +v)} />
              <Field label="Zam %" type="number" v={form.percent_salary_hike} on={(v) => set("percent_salary_hike", +v)} />
              <Field label="Stock Option (0-3)" type="number" v={form.stock_option_level} on={(v) => set("stock_option_level", +v)} />
              <Field label="İş Tatmini (1-4)" type="number" v={form.job_satisfaction} on={(v) => set("job_satisfaction", +v)} />
              <Field label="Çevre Tatmini (1-4)" type="number" v={form.environment_satisfaction} on={(v) => set("environment_satisfaction", +v)} />
              <Field label="İlişki Tatmini (1-4)" type="number" v={form.relationship_satisfaction} on={(v) => set("relationship_satisfaction", +v)} />
              <Field label="İş-Yaşam Dengesi (1-4)" type="number" v={form.work_life_balance} on={(v) => set("work_life_balance", +v)} />
              <Field label="İş Bağlılığı (1-4)" type="number" v={form.job_involvement} on={(v) => set("job_involvement", +v)} />
              <Field label="Performans (1-4)" type="number" v={form.performance_rating} on={(v) => set("performance_rating", +v)} />
              <Field label="Eğitim Sayısı/Yıl" type="number" v={form.training_times_last_year} on={(v) => set("training_times_last_year", +v)} />
              <FieldSelect label="Mesai" v={form.overtime ? "Yes" : "No"} on={(v) => set("overtime", v === "Yes")} options={["No", "Yes"]} />
            </div>
            <div className="mt-5 flex justify-end">
              <Button onClick={() => m.mutate()} disabled={m.isPending}>
                <Sparkles className="h-4 w-4" />
                {m.isPending ? "Hesaplanıyor..." : "Tahmin Et"}
              </Button>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Sonuç</CardTitle></CardHeader>
          <CardBody>
            {!result && !m.isError && <div className="text-sm text-slate-500">Sol formu doldurun ve "Tahmin Et" butonuna basın.</div>}
            {m.isError && <div className="text-sm text-red-600">Tahmin başarısız: {(m.error as any)?.response?.data?.detail || "Bilinmeyen hata"}</div>}
            {result && (
              <div className="space-y-4">
                <div className="text-center py-4">
                  <div className="text-xs uppercase text-slate-500 mb-1">Churn Olasılığı</div>
                  <div className="text-5xl font-bold tracking-tight">{fmtPct(result.churn_prob)}</div>
                  <Badge className={riskColor(result.risk_level) + " mt-2"}>{result.risk_level}</Badge>
                </div>
                <div className="text-xs text-slate-500 text-center">Model: {result.model_version}</div>
                {result.shap_values?.top_features?.length > 0 && (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={result.shap_values.top_features} layout="vertical" margin={{ left: 50 }}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis type="category" dataKey="feature" tick={{ fontSize: 10 }} width={120} />
                      <Tooltip />
                      <Bar dataKey="shap" radius={[0, 6, 6, 0]}>
                        {result.shap_values.top_features.map((d: any, i: number) => (
                          <Cell key={i} fill={d.shap > 0 ? "#dc2626" : "#10b981"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}

function Field({ label, v, on, type = "text" }: { label: string; v: any; on: (v: string) => void; type?: string }) {
  return (
    <div>
      <Label>{label}</Label>
      <Input type={type} value={v} onChange={(e) => on(e.target.value)} />
    </div>
  );
}
function FieldSelect({ label, v, on, options }: { label: string; v: any; on: (v: string) => void; options: string[] }) {
  return (
    <div>
      <Label>{label}</Label>
      <Select value={v} onChange={(e) => on(e.target.value)}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </Select>
    </div>
  );
}
