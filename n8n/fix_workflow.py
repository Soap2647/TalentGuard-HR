"""
Workflow'u lineer yap:
Login → BatchPredict → HighRisk → KPIs → Code → NoOp

Böylece Code node $input.first() ile tüm önceki node data'ya erişir.
"""
import json

with open('D:/Mevcut Projeler/Çalışan Churn Tahmin/n8n/wf1_live.json', 'r', encoding='utf-8') as f:
    wrapper = json.load(f)
wf = wrapper['data']

names = {n['id']: n['name'] for n in wf['nodes']}
n_login    = names['node-login']
n_batch    = names['node-batch']
n_highrisk = names['node-highrisk']
n_kpis     = names['node-kpis']
n_summary  = names['node-summary']
n_note     = names['node-note']

print("Node isimleri:")
for k,v in names.items():
    print(f"  {k}: {v}")

# Code node JS - lineer chain'de $input.first().json = KPIs node çıktısı
# Ama high-risk items $('node-highrisk').all() ile alınır
new_code = (
    '// Lineer chain: Login->Batch->HighRisk->KPIs->Code\n'
    '// $input = KPIs node output (1 item)\n'
    '// $("HIGH_RISK_NAME").all() = 20 high-risk employee items\n\n'
    'const kpis = $input.first().json;\n'
    'const hrItems = $("HIGH_RISK_NAME").all();\n'
    'const batchResult = $("BATCH_NAME").first().json;\n\n'
    'const topRisky = hrItems.slice(0, 5).map(function(item) { return item.json; });\n\n'
    'const lines = topRisky.map(function(e, i) {\n'
    '  var prob = (Number(e.churn_prob) * 100).toFixed(1);\n'
    '  return (i + 1) + ". " + (e.full_name || "?") + " (" + (e.department || "?") + ") - %" + prob;\n'
    '});\n\n'
    'var report = [\n'
    '  "GUNLUK CHURN RISK RAPORU - " + new Date().toLocaleDateString("tr-TR"),\n'
    '  "",\n'
    '  "Toplam Calisanlar : " + kpis.total_employees,\n'
    '  "Yuksek Risk       : " + kpis.high_risk_count + " kisi",\n'
    '  "Ort. Kidem        : " + kpis.avg_tenure + " yil",\n'
    '  "Genel Attrition   : %" + kpis.overall_attrition,\n'
    '  "",\n'
    '  "=== En Riskli 5 Calisanlar ==="\n'
    '].concat(lines.length > 0 ? lines : ["(bos)"]).concat([\n'
    '  "",\n'
    '  "Batch Tahmin: " + batchResult.processed + " basarili / " + batchResult.failed + " basarisiz",\n'
    '  "",\n'
    '  "Detaylar icin: http://127.0.0.1:5173"\n'
    ']).join("\\n");\n\n'
    'return [{ json: { report: report, topRisky: topRisky, kpis: kpis, batchResult: batchResult } }];\n'
)

new_code = new_code.replace("HIGH_RISK_NAME", n_highrisk)
new_code = new_code.replace("BATCH_NAME", n_batch)

# Node konumlarını düzenle (lineer yerleşim)
positions = {
    'node-schedule': [240, 300],
    'node-login':    [460, 300],
    'node-batch':    [680, 300],
    'node-highrisk': [900, 300],
    'node-kpis':     [1120, 300],
    'node-summary':  [1340, 300],
    'node-note':     [1560, 300],
}
for node in wf['nodes']:
    if node['id'] in positions:
        node['position'] = positions[node['id']]
    if node['id'] == 'node-summary':
        node['parameters']['jsCode'] = new_code
        print(f"Code node güncellendi")

# Connections: lineer zincir
wf['connections'] = {
    n_login:    {"main": [[{"node": n_batch,    "type": "main", "index": 0}]]},
    n_batch:    {"main": [[{"node": n_highrisk, "type": "main", "index": 0}]]},
    n_highrisk: {"main": [[{"node": n_kpis,     "type": "main", "index": 0}]]},
    n_kpis:     {"main": [[{"node": n_summary,  "type": "main", "index": 0}]]},
    n_summary:  {"main": [[{"node": n_note,     "type": "main", "index": 0}]]},
}

# Schedule trigger'ı da Login'e bağla
n_sched = names.get('node-schedule', '')
if n_sched:
    wf['connections'][n_sched] = {"main": [[{"node": n_login, "type": "main", "index": 0}]]}

patch = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {}),
    'staticData': None
}

with open('D:/Mevcut Projeler/Çalışan Churn Tahmin/n8n/wf1_linear.json', 'w', encoding='utf-8') as f:
    json.dump(patch, f, ensure_ascii=False)
print("wf1_linear.json hazır")
