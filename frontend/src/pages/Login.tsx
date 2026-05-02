import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, CardBody, Input, Label } from "@/components/ui";

export default function Login() {
  const nav = useNavigate();
  const [username, setU] = useState("admin");
  const [password, setP] = useState("admin123");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { username, password });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({ username: data.username, full_name: data.full_name, role: data.role }),
      );
      nav("/");
    } catch (e: any) {
      setErr(e?.response?.data?.detail || "Giriş başarısız");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center relative overflow-hidden bg-slate-50 dark:bg-slate-950 p-4">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/20 dark:bg-brand-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/20 dark:bg-indigo-500/10 rounded-full blur-3xl animate-float"></div>
      
      <Card className="w-full max-w-md relative z-10 glass-panel border-white/50 dark:border-slate-700/50 shadow-2xl backdrop-blur-xl animate-fade-in-up">
        <CardBody className="p-8 sm:p-10">
          <div className="flex flex-col items-center text-center gap-4 mb-8">
            <div className="rounded-2xl bg-gradient-to-br from-brand-500 to-brand-600 text-white p-4 shadow-lg shadow-brand-500/30 ring-4 ring-white dark:ring-slate-900">
              <ShieldCheck className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-2xl font-heading font-bold tracking-tight text-slate-800 dark:text-white">TalentGuard</h1>
              <p className="text-sm text-brand-600 dark:text-brand-400 font-medium uppercase tracking-widest mt-1">Predictive Analytics</p>
            </div>
          </div>

          <form onSubmit={submit} className="space-y-5">
            <div>
              <Label className="ml-1 mb-1.5 block">Kullanıcı Adı</Label>
              <Input value={username} onChange={(e) => setU(e.target.value)} autoFocus placeholder="admin" />
            </div>
            <div>
              <Label className="ml-1 mb-1.5 block">Şifre</Label>
              <Input type="password" value={password} onChange={(e) => setP(e.target.value)} placeholder="••••••••" />
            </div>
            {err && (
              <div className="rounded-xl bg-red-50/80 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-300 px-4 py-3 text-sm flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
                {err}
              </div>
            )}
            <Button type="submit" disabled={loading} className="w-full mt-2 h-12 text-base">
              {loading ? "Giriş yapılıyor..." : "Sisteme Giriş"}
            </Button>
          </form>

          <div className="mt-8 rounded-xl bg-slate-100/50 dark:bg-slate-800/30 p-4 text-xs text-slate-600 dark:text-slate-400 border border-slate-200/50 dark:border-slate-700/50">
            <div className="font-semibold mb-2 text-slate-800 dark:text-slate-200">Demo Hesaplar</div>
            <div className="space-y-1.5">
              <div className="flex justify-between"><span className="font-medium text-slate-700 dark:text-slate-300">admin / admin123</span><span className="opacity-70">Tüm yetkiler</span></div>
              <div className="flex justify-between"><span className="font-medium text-slate-700 dark:text-slate-300">hr_user / hr123</span><span className="opacity-70">İnsan Kaynakları</span></div>
              <div className="flex justify-between"><span className="font-medium text-slate-700 dark:text-slate-300">manager / manager123</span><span className="opacity-70">Departman Yöneticisi</span></div>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
