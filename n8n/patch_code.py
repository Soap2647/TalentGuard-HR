import json

with open('D:/Mevcut Projeler/Çalışan Churn Tahmin/n8n/wf1_live.json', 'r', encoding='utf-8') as f:
    wrapper = json.load(f)
wf = wrapper['data']

# Gerçek node isimlerini al
names = {n['id']: n['name'] for n in wf['nodes']}
hr_name  = names.get('node-highrisk', '')
kpi_name = names.get('node-kpis', '')
bat_name = names.get('node-batch', '')

print("node-highrisk:", repr(hr_name))
print("node-kpis    :", repr(kpi_name))
print("node-batch   :", repr(bat_name))

new_code = r"""// n8n: HTTP Request v4.2 dizileri birden fazla item yapar
// Her item bir calisanin verisini icerir
const hrItems = $("NODE_HR").all();
const kpis = $("NODE_KPI").first().json;
const batchResult = $("NODE_BAT").first().json;

const topRisky = hrItems.slice(0, 5).map(function(item) { return item.json; });

const lines = topRisky.map(function(e, i) {
  var prob = (Number(e.churn_prob) * 100).toFixed(1);
  return (i + 1) + ". " + (e.full_name || "?") + " (" + (e.department || "?") + ") - %" + prob;
});

var report = [
  "GUNLUK CHURN RISK RAPORU - " + new Date().toLocaleDateString("tr-TR"),
  "",
  "Toplam Calisanlar : " + kpis.total_employees,
  "Yuksek Risk       : " + kpis.high_risk_count + " kisi",
  "Ort. Kidem        : " + kpis.avg_tenure + " yil",
  "Genel Attrition   : %" + kpis.overall_attrition,
  "",
  "=== En Riskli 5 Calisanlar ==="
].concat(lines.length > 0 ? lines : ["(veri yok)"]).concat([
  "",
  "Batch Tahmin: " + batchResult.processed + " basarili / " + batchResult.failed + " basarisiz",
  "",
  "Detaylar icin: http://127.0.0.1:5173"
]).join("\n");

return [{ json: { report: report, topRisky: topRisky, kpis: kpis, batchResult: batchResult } }];
"""

# Node isimlerini yerleştir
new_code = new_code.replace("NODE_HR", hr_name)
new_code = new_code.replace("NODE_KPI", kpi_name)
new_code = new_code.replace("NODE_BAT", bat_name)

for node in wf['nodes']:
    if node.get('id') == 'node-summary':
        node['parameters']['jsCode'] = new_code
        print("Code node guncellendi")

patch = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {}),
    'staticData': None
}

with open('D:/Mevcut Projeler/Çalışan Churn Tahmin/n8n/wf1_patch3.json', 'w', encoding='utf-8') as f:
    json.dump(patch, f, ensure_ascii=False)
print("patch3.json hazir")
