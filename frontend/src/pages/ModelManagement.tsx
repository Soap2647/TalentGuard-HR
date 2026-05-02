import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Brain, CheckCircle2, Play } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Button, Card, CardBody, CardHeader, CardTitle, Spinner } from "@/components/ui";

export default function ModelManagement() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["models"],
    queryFn: () => api.get("/admin/models").then((r) => r.data),
  });

  const activate = useMutation({
    mutationFn: (id: number) => api.post(`/admin/models/${id}/activate`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["models"] }),
  });
  const retrain = useMutation({
    mutationFn: () => api.post("/admin/models/retrain").then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["models"] }),
  });
  const batch = useMutation({
    mutationFn: () => api.post("/predictions/batch").then((r) => r.data),
  });

  return (
    <div className="p-6 max-w-[1300px] mx-auto space-y-4">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Model Yönetimi</h1>
          <p className="text-sm text-slate-500">Model versiyonları, aktivasyon ve yeniden eğitim.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => batch.mutate()} disabled={batch.isPending}>
            <Play className="h-4 w-4" />
            {batch.isPending ? "Çalışıyor..." : "Batch Tahmin"}
          </Button>
          <Button onClick={() => retrain.mutate()} disabled={retrain.isPending}>
            <Brain className="h-4 w-4" />
            {retrain.isPending ? "Eğitiliyor..." : "Yeniden Eğit"}
          </Button>
        </div>
      </header>

      {batch.data && (
        <div className="rounded-lg bg-emerald-50 dark:bg-emerald-900/20 px-4 py-3 text-sm text-emerald-700 dark:text-emerald-300">
          Batch tamamlandı: {batch.data.processed} başarılı / {batch.data.failed} başarısız (toplam {batch.data.total}).
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Eğitilmiş Modeller</CardTitle></CardHeader>
        <CardBody className="p-0">
          {isLoading ? <div className="p-12 grid place-items-center"><Spinner /></div>
            : !data?.length ? <div className="p-12 text-center text-sm text-slate-500">Henüz model yok. Önce 'Yeniden Eğit' butonuna basın.</div>
            : (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="text-left p-3">Versiyon</th>
                    <th className="text-left p-3">Algoritma</th>
                    <th className="text-right p-3">AUC</th>
                    <th className="text-right p-3">F1</th>
                    <th className="text-right p-3">Accuracy</th>
                    <th className="text-left p-3">Eğitim Tarihi</th>
                    <th className="text-center p-3">Durum</th>
                    <th className="text-right p-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((m: any) => (
                    <tr key={m.id} className="border-t border-slate-100 dark:border-slate-800">
                      <td className="p-3 font-mono text-xs">{m.version}</td>
                      <td className="p-3">{m.algorithm}</td>
                      <td className="p-3 text-right tabular-nums">{m.metrics?.roc_auc?.toFixed(4) ?? "-"}</td>
                      <td className="p-3 text-right tabular-nums">{m.metrics?.f1?.toFixed(4) ?? "-"}</td>
                      <td className="p-3 text-right tabular-nums">{m.metrics?.accuracy?.toFixed(4) ?? "-"}</td>
                      <td className="p-3 text-xs text-slate-500">{new Date(m.trained_at).toLocaleString()}</td>
                      <td className="p-3 text-center">
                        {m.is_active ? (
                          <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                            <CheckCircle2 className="inline h-3 w-3 mr-1" />Aktif
                          </Badge>
                        ) : <Badge className="bg-slate-100 text-slate-600">Pasif</Badge>}
                      </td>
                      <td className="p-3 text-right">
                        {!m.is_active && (
                          <button
                            onClick={() => activate.mutate(m.id)}
                            className="text-xs text-brand-600 hover:underline"
                          >
                            Aktive et
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
        </CardBody>
      </Card>
    </div>
  );
}
