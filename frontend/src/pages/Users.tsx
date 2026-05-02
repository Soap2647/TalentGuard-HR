import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2, UserPlus } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Button, Card, CardBody, CardHeader, CardTitle, Input, Label, Select, Spinner } from "@/components/ui";

const ROLE_COLORS: Record<string, string> = {
  admin: "bg-purple-100 text-purple-700",
  hr: "bg-blue-100 text-blue-700",
  manager: "bg-amber-100 text-amber-700",
};

const EMPTY = { username: "", full_name: "", email: "", password: "", role: "hr", department_id: "" };

export default function Users() {
  const qc = useQueryClient();
  const [form, setForm] = useState({ ...EMPTY });
  const [open, setOpen] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: () => api.get("/admin/users").then((r) => r.data),
  });

  const create = useMutation({
    mutationFn: () =>
      api.post("/admin/users", {
        ...form,
        department_id: form.department_id ? Number(form.department_id) : null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      setForm({ ...EMPTY });
      setOpen(false);
      setErr(null);
    },
    onError: (e: any) => setErr(e?.response?.data?.detail || "Hata"),
  });

  const del = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/users/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });

  return (
    <div className="p-6 max-w-[1200px] mx-auto space-y-4">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Kullanıcılar</h1>
          <p className="text-sm text-slate-500">Sistem kullanıcılarını yönet (admin yetkisi).</p>
        </div>
        <Button onClick={() => setOpen((o) => !o)}>
          <UserPlus className="h-4 w-4" />Yeni Kullanıcı
        </Button>
      </header>

      {open && (
        <Card>
          <CardHeader><CardTitle>Yeni Kullanıcı</CardTitle></CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div><Label>Kullanıcı adı</Label><Input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></div>
              <div><Label>Ad Soyad</Label><Input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></div>
              <div><Label>E-posta</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
              <div><Label>Şifre</Label><Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></div>
              <div>
                <Label>Rol</Label>
                <Select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  <option value="admin">admin</option>
                  <option value="hr">hr</option>
                  <option value="manager">manager</option>
                </Select>
              </div>
              <div><Label>Departman ID (manager için)</Label><Input value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value })} /></div>
            </div>
            {err && <div className="mt-3 text-sm text-red-600">{err}</div>}
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setOpen(false)}>İptal</Button>
              <Button onClick={() => create.mutate()} disabled={create.isPending}>Oluştur</Button>
            </div>
          </CardBody>
        </Card>
      )}

      <Card>
        <CardBody className="p-0">
          {isLoading ? <div className="p-12 grid place-items-center"><Spinner /></div>
            : (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 dark:bg-slate-800/50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="text-left p-3">Kullanıcı</th>
                    <th className="text-left p-3">Ad</th>
                    <th className="text-left p-3">E-posta</th>
                    <th className="text-center p-3">Rol</th>
                    <th className="text-center p-3">Aktif</th>
                    <th className="text-right p-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {data?.map((u: any) => (
                    <tr key={u.id} className="border-t border-slate-100 dark:border-slate-800">
                      <td className="p-3 font-medium">{u.username}</td>
                      <td className="p-3">{u.full_name}</td>
                      <td className="p-3 text-slate-600 dark:text-slate-400">{u.email}</td>
                      <td className="p-3 text-center"><Badge className={ROLE_COLORS[u.role]}>{u.role}</Badge></td>
                      <td className="p-3 text-center">{u.is_active ? "Evet" : "Hayır"}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => confirm(`${u.username} silinsin mi?`) && del.mutate(u.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
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
