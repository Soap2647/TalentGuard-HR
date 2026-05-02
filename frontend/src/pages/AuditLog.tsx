import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge, Card, CardBody, CardHeader, CardTitle, Select, Spinner } from "@/components/ui";

const OP_COLORS: Record<string, string> = {
  INSERT: "bg-emerald-100 text-emerald-700",
  UPDATE: "bg-amber-100 text-amber-700",
  DELETE: "bg-red-100 text-red-700",
};

export default function AuditLog() {
  const [table, setTable] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["audit", table],
    queryFn: () => api.get("/admin/audit-log", { params: { table: table || undefined, limit: 200 } }).then((r) => r.data),
  });

  return (
    <div className="p-6 max-w-[1400px] mx-auto space-y-4">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Audit Log</h1>
        <p className="text-sm text-slate-500">PostgreSQL trigger'ları ile otomatik üretilir.</p>
      </header>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <CardTitle>Değişiklik Kayıtları</CardTitle>
            <Select value={table} onChange={(e) => setTable(e.target.value)} className="w-48">
              <option value="">Tüm Tablolar</option>
              <option value="employees">employees</option>
              <option value="users">users</option>
              <option value="predictions">predictions</option>
              <option value="model_registry">model_registry</option>
            </Select>
          </div>
        </CardHeader>
        <CardBody className="p-0">
          {isLoading ? <div className="p-12 grid place-items-center"><Spinner /></div>
            : !data?.length ? <div className="p-12 text-center text-sm text-slate-500">Kayıt yok.</div>
            : (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="text-left p-3">Tarih</th>
                    <th className="text-left p-3">Tablo</th>
                    <th className="text-left p-3">İşlem</th>
                    <th className="text-left p-3">Kayıt</th>
                    <th className="text-left p-3">Kullanıcı</th>
                    <th className="text-left p-3">Detay</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((r: any) => (
                    <tr key={r.id} className="border-t border-slate-100 dark:border-slate-800 align-top">
                      <td className="p-3 text-xs text-slate-500">{new Date(r.changed_at).toLocaleString()}</td>
                      <td className="p-3 font-mono text-xs">{r.table_name}</td>
                      <td className="p-3"><Badge className={OP_COLORS[r.operation] || ""}>{r.operation}</Badge></td>
                      <td className="p-3 font-mono text-xs">#{r.record_id}</td>
                      <td className="p-3 text-xs">{r.changed_by}</td>
                      <td className="p-3">
                        <details>
                          <summary className="cursor-pointer text-xs text-brand-600">Görüntüle</summary>
                          <pre className="mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded text-[10px] overflow-x-auto max-w-md">
                            {JSON.stringify({ old: r.old_data, new: r.new_data }, null, 2)}
                          </pre>
                        </details>
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
