<script setup>
import { computed, onMounted, ref, watch, nextTick, shallowRef, inject } from "vue";
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const emit = defineEmits(['goExport']);

const listingsAll = ref([]);
const loading = ref(true);
const loadError = ref("");

const triggerToast = inject('triggerToast');

onMounted(async () => {
  try {
    const res = await fetch("/db.json");
    const data = await res.json();
    if (data.listings && typeof data.listings === 'object' && !Array.isArray(data.listings)) {
      listingsAll.value = Object.values(data.listings).flat();
    } else {
      listingsAll.value = data.listings || [];
    }
  } catch (e) {
    loadError.value = "Não foi possível carregar /db.json";
    listingsAll.value = [];
  } finally {
    loading.value = false;
  }
});

const latestScrapeDate = computed(() => {
  if (!listingsAll.value.length) return null;
  const dates = [...new Set(listingsAll.value.map(l => l.scrape_date).filter(Boolean))];
  dates.sort((a,b) => new Date(b) - new Date(a));
  return dates[0] || null;
});

const listingsLatest = computed(() => {
  if (!latestScrapeDate.value) return [];
  return listingsAll.value.filter(l => l.scrape_date === latestScrapeDate.value);
});

const cityOptions = computed(() => {
  const s = new Set();
  for (const l of listingsLatest.value) {
    if (l.neighbourhood_group_cleansed) s.add(l.neighbourhood_group_cleansed);
  }
  return [...s].sort();
});

const roomTypeMap = {
  "Entire home/apt": "Apartamento",
  "Private room": "Quarto Privado",
  "Shared room": "Quarto Partilhado",
  "Hotel room": "Quarto Hotel",
};

const typeOptions = computed(() => {
  const s = new Set();
  for (const l of listingsLatest.value) {
    if (l.room_type) s.add(l.room_type);
  }
  return [...s].sort().map(rt => ({
    raw: rt,
    label: roomTypeMap[rt] || rt
  }));
});

const propertyType = ref(""); 
const city = ref("");         
const priceMax = ref(200);    
const availabilityMax = ref(365); 

const applied = ref(false);
const appliedSnapshot = ref(null);

const aplicar = () => {
  applied.value = true;
  appliedSnapshot.value = {
    propertyType: propertyType.value,
    city: city.value,
    priceMax: Number(priceMax.value),
    availabilityMax: Number(availabilityMax.value)
  };
  page.value = 1;
};

const limpar = () => {
  propertyType.value = "";
  city.value = "";
  priceMax.value = 200;
  availabilityMax.value = 365;

  applied.value = false;
  appliedSnapshot.value = null;
  page.value = 1;
};

const filtered = computed(() => {
  if (!applied.value || !appliedSnapshot.value) return [];

  const f = appliedSnapshot.value;
  let arr = listingsLatest.value;

  arr = arr.filter(l => {
    if (f.propertyType && l.room_type !== f.propertyType) return false;
    if (f.city && l.neighbourhood_group_cleansed !== f.city) return false;
    if (l.price == null || Number(l.price) > f.priceMax) return false;
    if (l.availability_365 == null || Number(l.availability_365) > f.availabilityMax) return false;
    return true;
  });

  return arr;
});

const perPage = 4;
const page = ref(1);

const totalResults = computed(() => filtered.value.length);

const rowsPage = computed(() => {
  const start = (page.value - 1) * perPage;
  return filtered.value.slice(start, start + perPage);
});

const showingText = computed(() => {
  if (!totalResults.value) return "";
  const start = (page.value - 1) * perPage + 1;
  const end = Math.min(page.value * perPage, totalResults.value);
  return `A mostrar ${start}-${end} de ${totalResults.value}`;
});

const totalPages = computed(() => Math.max(1, Math.ceil(totalResults.value / perPage)));

const goPage = (p) => {
  page.value = Math.max(1, Math.min(p, totalPages.value));
};

const activeTab = ref("distrib"); 
const priceChartCanvas = ref(null);
const chartInstance = shallowRef(null);

const kpis = computed(() => {
  if (!applied.value) return { listings: 0, priceAvg: 0, occAvg: 0 };

  const arr = filtered.value;
  const n = arr.length || 0;
  const priceAvg = n ? Math.round(arr.reduce((s,l)=>s+(Number(l.price)||0),0) / n) : 0;
  const occAvg = n ? Math.round(arr.reduce((s,l)=>s+(100*(1-(Number(l.availability_365)||365)/365)),0) / n) : 0;

  return { listings: n, priceAvg, occAvg };
});

const top5Bairros = computed(() => {
  if (!applied.value) return [];
  const counts = new Map();
  for (const l of filtered.value) {
    const b = l.neighbourhood_cleansed || "—";
    counts.set(b, (counts.get(b) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a,b)=>b[1]-a[1])
    .slice(0,5)
    .map(([bairro, n]) => ({ bairro, n }));
});

const priceHistogramData = computed(() => {
  const data = filtered.value;
  if (!data.length) return { labels: [], data: [] };

  const bins = [0, 0, 0, 0, 0];
  const labels = ["0-50€", "50-100€", "100-150€", "150-200€", "200€+"];

  data.forEach(l => {
    const p = Number(l.price) || 0;
    if (p <= 50) bins[0]++;
    else if (p <= 100) bins[1]++;
    else if (p <= 150) bins[2]++;
    else if (p <= 200) bins[3]++;
    else bins[4]++;
  });

  return { labels, data: bins };
});

const renderChart = () => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }

  if (!priceChartCanvas.value) return;

  const ctx = priceChartCanvas.value.getContext('2d');
  const chartData = priceHistogramData.value;

  chartInstance.value = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Nº Alojamentos',
        data: chartData.data,
        backgroundColor: '#6366f1',
        borderRadius: 4,
        barPercentage: 0.6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: '#27272a', titleColor: '#fff', bodyColor: '#fff' }
      },
      scales: {
        y: { beginAtZero: true, grid: { display: false }, ticks: { display: false } },
        x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#6b7280' } }
      }
    }
  });
};

watch([filtered, activeTab], () => {
  if (activeTab.value === 'distrib' && applied.value) {
    nextTick(() => renderChart());
  }
});

const exportar = () => {
  if (!applied.value || !appliedSnapshot.value) return;

  triggerToast("A preparar dados para exportação...", "info", "Exportação");

  const payload = {
    source: 'explorar',
    createdAt: new Date().toISOString(),
    filters: { ...appliedSnapshot.value },
    rows: filtered.value
  };

  localStorage.setItem('insideairbnb_export_payload', JSON.stringify(payload));
  emit('goExport');
};
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>
        <span class="accent">Filtrar</span>
        <span class="rest">&amp; Explorar</span>
      </h1>
    </header>

    <section class="filters card">
      <div class="row">
        <div class="lbl">Tipo de Propriedade</div>
        <div class="ctrl">
          <div class="select-wrap">
            <select v-model="propertyType" :disabled="loading || !!loadError">
              <option value="">Selecionar Tipo...</option>
              <option v-for="t in typeOptions" :key="t.raw" :value="t.raw">
                {{ t.label }}
              </option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="lbl">Localização</div>
        <div class="ctrl">
          <div class="select-wrap">
            <select v-model="city" :disabled="loading || !!loadError">
              <option value="">Selecionar Cidade...</option>
              <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="lbl">Preço p/noite</div>
        <div class="ctrl range-row">
          <span class="range-min">20€</span>
          <input type="range" min="20" max="400" v-model="priceMax" />
          <span class="range-val">{{ Number(priceMax) }}€</span>
          <span class="range-max">400€</span>
        </div>
      </div>

      <div class="row">
        <div class="lbl">Disponibilidade dias/ano</div>
        <div class="ctrl range-row">
          <span class="range-min">0</span>
          <input type="range" min="0" max="365" v-model="availabilityMax" />
          <span class="range-val">{{ Number(availabilityMax) }}</span>
          <span class="range-max">365</span>
        </div>
      </div>

      <div class="actions">
        <button class="btn primary" @click="aplicar" :disabled="loading || !!loadError">Aplicar</button>
        <button class="btn ghost" @click="limpar">Limpar</button>
      </div>

      <div v-if="loadError" class="note error">{{ loadError }}</div>
    </section>

    <section v-if="!applied" class="bottom-empty">
      <div class="empty-left card"></div>
      <div class="empty-right card"></div>
    </section>

    <section v-else class="bottom">
      <div class="results card">
        <div class="results-header">
          <h2>Resultados ({{ totalResults }})</h2>
          <button class="btn small ghost" @click="exportar">Exportar</button>
        </div>

        <table class="tbl">
          <thead>
            <tr>
              <th>Propriedade</th>
              <th>Tipo</th>
              <th>Bairro</th>
              <th class="num">€</th>
              <th class="num">%</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rowsPage" :key="r.id">
              <td>#{{ r.id }}</td>
              <td>{{ roomTypeMap[r.room_type] || r.room_type }}</td>
              <td>{{ r.neighbourhood_cleansed || "—" }}</td>
              <td class="num">€{{ Math.round(Number(r.price || 0)) }}</td>
              <td class="num">
                {{ Math.round(100 * (1 - (Number(r.availability_365 ?? 365) / 365))) }}%
              </td>
            </tr>
            <tr v-if="rowsPage.length === 0">
              <td colspan="5" class="nores">Sem resultados para os filtros atuais.</td>
            </tr>
          </tbody>
        </table>

        <div class="pager" v-if="totalResults > 0">
          <div class="showing">{{ showingText }}</div>
          <div class="pages">
            <button class="pg" @click="goPage(page - 1)">‹</button>
            <button
              v-for="p in Math.min(totalPages, 4)"
              :key="p"
              class="pg"
              :class="{ active: page === p }"
              @click="goPage(p)"
            >{{ p }}</button>
            <button class="pg" @click="goPage(page + 1)">›</button>
          </div>
        </div>
      </div>

      <div class="right card">
        <div class="tabs">
          <button class="tab" :class="{ active: activeTab === 'distrib' }" @click="activeTab = 'distrib'">Distribuições</button>
          <button class="tab" :class="{ active: activeTab === 'comp' }" @click="activeTab = 'comp'">Comparações</button>
          <button class="tab" :class="{ active: activeTab === 'emblem' }" @click="activeTab = 'emblem'">Emblemáticos</button>
        </div>

        <div v-if="activeTab === 'distrib'" class="tab-body">
          <div class="kpis">
            <div class="kpi">
              <div class="kpi-label">Listagens</div>
              <div class="kpi-value">{{ kpis.listings }}</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Preço médio</div>
              <div class="kpi-value">{{ kpis.priceAvg }}€</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Ocupação Média</div>
              <div class="kpi-value">{{ kpis.occAvg }}%</div>
            </div>
          </div>

          <div class="panel-grid">
            <div class="panel">
              <div class="panel-title">Distribuição - Preço</div>
              <div class="chart-container">
                <canvas ref="priceChartCanvas"></canvas>
              </div>
            </div>

            <div class="panel">
              <div class="panel-title">Top 5 Bairros</div>
              <ol class="top5">
                <li v-for="b in top5Bairros" :key="b.bairro">
                  <span>{{ b.bairro }}</span>
                  <b>{{ b.n }}</b>
                </li>
              </ol>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'comp'" class="tab-body">
          <div class="compare-note">Comparação com mês anterior (Mock)</div>
          <div class="diff-card">
            <div class="diff-title">Variação Mensal</div>
            <div class="diff-row"><span>Listagens</span><span class="diff pos">↑ 2.4%</span></div>
            <div class="diff-row"><span>Preço Médio</span><span class="diff neg">↓ 1.2%</span></div>
            <div class="diff-row"><span>Ocupação</span><span class="diff pos">↑ 5.0%</span></div>
          </div>
        </div>

        <div v-else class="tab-body">
          <div class="emblem-header">
            <div class="emblem-title">Destaques da Seleção</div>
          </div>

          <div class="share-grid">
            <div class="share-card">
              <div class="share-head">Bairro mais caro</div>
              <div class="share-main">{{ top5Bairros[0]?.bairro || 'N/A' }}</div>
            </div>
            <div class="share-card">
              <div class="share-head">Maior disponibilidade</div>
              <div class="share-main">320 dias/ano</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
:root {
  --bg-dark: #18181b;
  --bg-cartao: #27272a;
  --cor-primaria: #6366f1;
  --cor-primaria-hover: #4f46e5;
  --texto-branco: #f4f4f5;
  --texto-cinza: #a1a1aa;
  --success: #10b981;
  --error: #ef4444;
  --borda: #3F3F46;
}

.page { padding: 28px; color: var(--texto-branco); }
.page-header { margin-bottom: 16px; }
h1 { margin: 0; font-size: 46px; font-weight: 800; }
.accent { color: var(--cor-primaria); }
.rest { margin-left: 10px; color: var(--texto-branco); }

.card { background: var(--bg-cartao); border: 1px solid var(--borda); border-radius: 18px; }

.filters { padding: 22px; }
.row { display:flex; align-items:center; gap: 22px; padding: 10px 0; }
.lbl { width: 220px; font-size: 18px; font-weight: 700; color:var(--texto-muted); }
.ctrl { flex: 1; }

.select-wrap { position: relative; max-width: 420px; }
select {
  width: 100%;
  appearance: none;
  background: #1f1f1f;
  border: 1px solid var(--texto-cinza);
  color: var(--texto-branco);
  border-radius: 12px;
  padding: 12px 42px 12px 12px;
  font-size: 15px;
}
.chev { position:absolute; right:14px; top:50%; transform:translateY(-50%); color:var(--texto-cinza); pointer-events:none; }

.range-row { display:flex; align-items:center; gap: 12px; max-width: 520px; }
.range-row input[type="range"] { width: 100%; accent-color: var(--cor-primaria); }
.range-min, .range-max { width: 48px; text-align:center; color:var(--texto-muted); }
.range-val{
  width: 70px;
  text-align: center;
  font-weight: 800;
  color: var(--texto-branco);
}

.actions { display:flex; justify-content:flex-end; gap: 16px; margin-top: 10px; }

.btn { border-radius: 14px; padding: 12px 18px; font-size: 20px; font-weight: 800; cursor:pointer; border: 1px solid transparent; }
.btn.primary { background: var(--cor-primaria); border-color: var(--cor-primaria); color:var(--texto-branco); }
.btn.primary:hover { background: var(--cor-primaria-hover); }
.btn.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn.ghost { background: transparent; border-color:var(--texto-cinza); color:var(--texto-muted); }
.btn.ghost:hover { border-color:var(--texto-cinza); color:var(--texto-branco); }
.btn.small { font-size: 14px; padding: 10px 14px; border-radius: 12px; }

.note { margin-top: 10px; font-size: 13px; color: var(--texto-cinza); }
.note.error { color: var(--error); }
.note.subtle { opacity: 0.85; }

.bottom-empty { margin-top: 18px; display:grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; }
.empty-left { height: 520px; }
.empty-right { height: 520px; }
.bottom { margin-top: 18px; display:grid; grid-template-columns: 1.2fr 0.8fr; gap: 18px; }

.results { padding: 18px 18px 12px; }
.results-header { display:flex; align-items:center; justify-content:space-between; padding: 6px 4px 10px; }
.results-header h2 { margin: 0; font-size: 28px; font-weight: 800; }

.tbl { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 0.9rem; }
.tbl th, .tbl td { padding: 14px 10px; }
.tbl thead th { color:var(--texto-muted); font-weight: 800; border-bottom: 1px solid var(--borda); text-align: left; }
.tbl tbody td { color:var(--texto-muted); border-bottom: 1px solid rgba(63,63,70,0.35); }
.tbl .num { text-align: right; width: 70px; }
.nores { text-align:center; padding: 20px 10px; color: var(--texto-cinza); }

.pager { display:flex; align-items:center; justify-content:space-between; padding: 12px 6px 6px; }
.showing { color:var(--texto-cinza); font-size: 13px; }
.pages { display:flex; align-items:center; gap: 8px; }
.pg { background: transparent; border: 1px solid transparent; color:var(--texto-muted); padding: 6px 10px; border-radius: 10px; cursor:pointer; }
.pg.active, .pg:hover { border-color: var(--borda); color:var(--texto-branco); }

.right { padding: 14px; background: var(--bg-branco); color:var(--texto-preto); border-color: var(--borda); }
.tabs { display:flex; border-bottom: 1px solid var(--texto-cinza); margin-bottom: 12px; gap: 8px; }
.tab {
  flex: 1; padding: 10px 12px;
  border: 1px solid var(--texto-cinza); border-bottom: none;
  background: var(--bg-cartao); color: var(--texto-muted);
  cursor: pointer; font-weight: 800;
  border-top-left-radius: 10px; border-top-right-radius: 10px;
}
.tab.active { background: var(--cor-primaria); border-color: var(--cor-primaria); color:var(--texto-branco); }

.tab-body { padding: 8px 4px 4px; }
.kpis { display:grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }
.kpi { background:var(--bg-branco); border: 1px solid var(--texto-cinza); border-radius: 12px; padding: 10px; text-align:center; }
.kpi-label { font-size: 11px; color:var(--texto-preto); font-weight: 700; opacity:0.7; text-transform: uppercase; }
.kpi-value { font-size: 20px; font-weight: 900; color: var(--texto-preto); }

.panel-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.panel { background:var(--bg-branco); border: 1px solid var(--texto-cinza); border-radius: 14px; padding: 12px; height: 180px; display: flex; flex-direction: column; }
.panel-title { font-weight: 900; margin-bottom: 10px; font-size: 0.9rem; }

.chart-container { flex: 1; position: relative; width: 100%; min-height: 0; }

.top5 { margin: 0; padding-left: 0; list-style: none; overflow-y: auto; }
.top5 li { padding: 6px 0; border-bottom: 1px solid var(--texto-cinza); display: flex; justify-content: space-between; font-size: 0.85rem; }
.top5 li b { color: var(--cor-primaria); }

.compare-note { font-size: 13px; color:var(--texto-cinza); margin-bottom: 10px; }
.diff-card { background:var(--bg-branco); border: 1px solid var(--texto-cinza); border-radius: 14px; padding: 12px; }
.diff-title { font-weight: 900; text-align:center; margin-bottom: 10px; }
.diff-row { display:flex; justify-content:space-between; padding: 10px 4px; border-bottom: 1px solid var(--texto-cinza); }
.diff.pos { color: var(--success); font-weight: 900; }
.diff.neg { color: var(--error); font-weight: 900; }

.emblem-header { text-align:center; padding: 6px 6px 10px; }
.emblem-title { font-size: 18px; font-weight: 900; }

.share-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
.share-card { background:var(--texto-branco); border-radius: 14px; padding: 12px; position: relative; min-height: 120px; border: 1px solid var(--texto-cinza); }
.share-head { font-size: 11px; font-weight: 900; margin-bottom: 8px; color: var(--texto-cinza); text-transform: uppercase; }
.share-main { font-size: 15px; font-weight: 900; margin-bottom: 6px; }

@media (max-width: 1180px) {
  .bottom-empty, .bottom { grid-template-columns: 1fr; }
  .lbl { width: 180px; }
}
</style>