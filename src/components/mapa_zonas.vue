<script setup>
import { computed, onMounted, ref, watch, onUnmounted, inject } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import pinIconSrc from '../assets/location.png'; 

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const props = defineProps({
  user: Object
});

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const listingsAll = ref([]);
const loading = ref(true);
const loadError = ref("");

const triggerToast = inject('triggerToast');

onMounted(async () => {
  try {
    const res = await fetch("/db.json");
    const data = await res.json();
    if (data.listings && !Array.isArray(data.listings)) {
      listingsAll.value = Object.values(data.listings).flat();
    } else {
      listingsAll.value = data.listings || [];
    }
  } catch (e) {
    loadError.value = "Não foi possível carregar /db.json";
    listingsAll.value = [];
  } finally {
    loading.value = false;
    initMap(); 
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

const indicador = ref("");
const periodo = ref("12m");
const nivel = ref("freguesia");
const normalizacao = ref("1000hab");
const zona = ref(props.user?.defaultCity || "");

const applied = ref(false);
const appliedSnapshot = ref(null);

const filteredMapData = computed(() => {
  return base.value;
});

const aplicar = () => {
  applied.value = true;
  appliedSnapshot.value = {
    indicador: indicador.value,
    periodo: periodo.value,
    nivel: nivel.value,
    normalizacao: normalizacao.value,
    zona: zona.value,
  };
  selectedZone.value = null;
  updateMapMarkers(); 
};

const limpar = () => {
  indicador.value = "";
  periodo.value = "12m";
  nivel.value = "freguesia";
  normalizacao.value = "1000hab";
  zona.value = "";

  applied.value = false;
  appliedSnapshot.value = null;
  selectedZone.value = null;
  updateMapMarkers();
};

const indicatorOptions = [
  { id: "listings", label: "Nº de alojamentos" },
  { id: "price_avg", label: "Preço médio/noite" },
  { id: "availability_avg", label: "Disponibilidade média (dias/ano)" },
  { id: "occupancy_avg", label: "Ocupação média (estim.)" }, 
];

const indicadorLabel = computed(() => {
  const found = indicatorOptions.find(o => o.id === indicador.value);
  return found ? found.label : "Indicador";
});

const base = computed(() => {
  const z = (appliedSnapshot.value?.zona || zona.value || "").trim().toLowerCase();
  let arr = listingsLatest.value;

  if (z) {
    arr = arr.filter(l =>
      String(l.neighbourhood_group_cleansed || "").toLowerCase().includes(z)
      || String(l.city || "").toLowerCase().includes(z)
      || String(l.neighbourhood_cleansed || "").toLowerCase().includes(z)
    );
  }
  return arr;
});

const groupKeyLabel = computed(() => (nivel.value === "freguesia" ? "Freguesia" : "Área (aprox.)"));

function safeNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

const grouped = computed(() => {
  const m = new Map(); 
  for (const l of base.value) {
    const key = (l.neighbourhood_cleansed || l.neighbourhood || "—").trim() || "—";
    const price = safeNum(l.price);
    const avail = safeNum(l.availability_365);
    const occ = avail == null ? null : (100 * (1 - (avail / 365)));

    if (!m.has(key)) {
      m.set(key, { key, count: 0, priceSum: 0, priceN: 0, availSum: 0, availN: 0, occSum: 0, occN: 0 });
    }
    const o = m.get(key);
    o.count += 1;

    if (price != null) { o.priceSum += price; o.priceN += 1; }
    if (avail != null) { o.availSum += avail; o.availN += 1; }
    if (occ != null) { o.occSum += occ; o.occN += 1; }
  }

  const arr = [...m.values()].map(o => ({
    key: o.key,
    listings: o.count,
    price_avg: o.priceN ? (o.priceSum / o.priceN) : null,
    availability_avg: o.availN ? (o.availSum / o.availN) : null,
    occupancy_avg: o.occN ? (o.occSum / o.occN) : null,
  }));

  return arr;
});

const selectedZone = ref(null);

const scored = computed(() => {
  if (!applied.value || !appliedSnapshot.value?.indicador) return [];
  const id = appliedSnapshot.value.indicador;

  const arr = grouped.value
    .map(z => ({ ...z, value: z[id] }))
    .filter(z => z.value != null);

  const desc = (id === "availability_avg") ? false : true;
  arr.sort((a,b) => (desc ? (b.value - a.value) : (a.value - b.value)));
  return arr;
});

const topZones = computed(() => scored.value.slice(0, 5));

const legendMin = computed(() => (scored.value.length ? scored.value[scored.value.length - 1].value : null));
const legendMax = computed(() => (scored.value.length ? scored.value[0].value : null));

function fmtValue(ind, v) {
  if (v == null) return "—";
  if (ind === "price_avg") return `${Math.round(v)}€`;
  if (ind === "availability_avg") return `${Math.round(v)} dias`;
  if (ind === "occupancy_avg") return `${Math.round(v)}%`;
  if (ind === "listings") return `${Math.round(v)}`;
  return `${Math.round(v)}`;
}

const explorarZona = () => {
  if (!selectedZone.value) return;
  localStorage.setItem("insideairbnb_selected_neighbourhood", selectedZone.value.key);
  triggerToast(`Zona '${selectedZone.value.key}' guardada para Explorar!`, 'success', 'Zona Selecionada');
};

const mapContainer = ref(null);
let map = null;
let markersLayer = null; 

const initMap = () => {
  if (!mapContainer.value) return;

  map = L.map(mapContainer.value, { preferCanvas: true }).setView([38.722, -9.139], 12);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
  
  if (listingsLatest.value.length > 0) {
    updateMapMarkers();
  }
};

const updateMapMarkers = () => {
  if (!map || !markersLayer) return;
  markersLayer.clearLayers();

  const data = filteredMapData.value;
  if (!data.length) return;

  const getColor = (val) => {
    return applied.value ? "#4F46E5" : "#A1A1AA"; 
  };

  const markers = [];

  data.forEach(l => {
    if (l.latitude && l.longitude) {
      const marker = L.circleMarker([l.latitude, l.longitude], {
        radius: 4,
        fillColor: getColor(),
        color: "#fff",
        weight: 0.5,
        opacity: 1,
        fillOpacity: 0.7
      });

      const price = l.price ? `${l.price}€` : "N/A";
      marker.bindPopup(`
        <div style="color: #333;">
          <b>${l.name || 'Alojamento'}</b><br/>
          ${l.neighbourhood_cleansed || ''}<br/>
          Preço: ${price}
        </div>
      `);
      
      markersLayer.addLayer(marker);
      markers.push([l.latitude, l.longitude]);
    }
  });

  if (markers.length > 0) {
    const bounds = L.latLngBounds(markers);
    map.fitBounds(bounds, { padding: [50, 50] });
  }
};

watch(filteredMapData, () => {
  updateMapMarkers();
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});

</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>
        <span class="accent">Mapa</span>
        <span class="rest">& Zonas</span>
      </h1>
    </header>

    <div class="layout">
      <section class="filters">
        <div class="card">
          <div class="field">
            <label>Indicador</label>
            <div class="select-wrap">
              <select v-model="indicador" :disabled="loading || !!loadError">
                <option value="">Seleciona ...</option>
                <option v-for="o in indicatorOptions" :key="o.id" :value="o.id">{{ o.label }}</option>
              </select>
              <span class="chev">▾</span>
            </div>
          </div>

          <div class="field">
            <label>Período</label>
            <div class="segmented" role="group">
              <button :class="{ active: periodo === '3m' }" @click="periodo = '3m'">Últ. 3m</button>
              <button :class="{ active: periodo === '6m' }" @click="periodo = '6m'">Últ. 6m</button>
              <button :class="{ active: periodo === '12m' }" @click="periodo = '12m'">Últ. 12m</button>
            </div>
          </div>

          <div class="field">
            <label>Nível Geográfico</label>
            <div class="segmented two" role="group">
              <button :class="{ active: nivel === 'freguesia' }" @click="nivel = 'freguesia'">Freguesia</button>
              <button :class="{ active: nivel === 'area500' }" @click="nivel = 'area500'">Área 500 m</button>
            </div>
          </div>

          <div class="field">
            <label>Normalização</label>
            <div class="select-wrap">
              <select v-model="normalizacao">
                <option value="1000hab">por 1.000 hab.</option>
                <option value="absolute">absoluto</option>
                <option value="km2">por km²</option>
              </select>
              <span class="chev">▾</span>
            </div>
          </div>

          <div class="field">
            <label>Zona</label>
            <div class="zone-chip">
              <img :src="pinIconSrc" alt="" class="pin-icon" />
              <input v-model="zona" aria-label="Zona" placeholder="Ex: Lisboa" />
            </div>
          </div>

          <div class="actions">
            <button class="btn primary" @click="aplicar" :disabled="loading || !!loadError">Aplicar</button>
            <button class="btn ghost" @click="limpar">Limpar</button>
          </div>

          <div v-if="loadError" class="note error">{{ loadError }}</div>
          <div v-else-if="loading" class="note">A carregar dados…</div>
          <div v-else class="note subtle">
            Registos: <b>{{ listingsLatest.length }}</b> (Visíveis: {{ filteredMapData.length }})
          </div>
        </div>
      </section>

      <section class="map">
        <div class="map-card">
          <div ref="mapContainer" class="map-container">
            <div class="map-overlay-top">
              <div class="pill">
                <span class="dot" :style="{ background: applied ? '#4F46E5' : '#A1A1AA' }"></span>
                {{ applied ? indicadorLabel : "Mostrando todos os alojamentos (Filtros desligados)" }}
              </div>

              <div v-if="applied" class="applied-pill">
                {{ groupKeyLabel }} · {{ appliedSnapshot?.zona || zona }}
              </div>
            </div>

            <div v-if="applied && appliedSnapshot?.indicador" class="overlay-ranking">
              <div class="overlay-title">Top 5 Zonas</div>
              <div class="overlay-sub">
                Ordenado por <b>{{ indicadorLabel }}</b>
              </div>

              <button
                v-for="z in topZones"
                :key="z.key"
                class="zone-row"
                :class="{ active: selectedZone?.key === z.key }"
                @click="selectedZone = z"
              >
                <span class="zname">{{ z.key }}</span>
                <span class="zval">{{ fmtValue(appliedSnapshot.indicador, z.value) }}</span>
              </button>

              <div v-if="selectedZone" class="zone-detail">
                <div class="zd-title">Selecionada: {{ selectedZone.key }}</div>
                <div class="zd-grid">
                  <div class="zd-item"><span>Listagens</span><b>{{ fmtValue("listings", selectedZone.listings) }}</b></div>
                  <div class="zd-item"><span>Preço méd.</span><b>{{ fmtValue("price_avg", selectedZone.price_avg) }}</b></div>
                  <div class="zd-item"><span>Disp. méd.</span><b>{{ fmtValue("availability_avg", selectedZone.availability_avg) }}</b></div>
                  <div class="zd-item"><span>Ocup. méd.</span><b>{{ fmtValue("occupancy_avg", selectedZone.occupancy_avg) }}</b></div>
                </div>

                <button class="btn tiny primary full-width" @click="explorarZona">Explorar esta zona</button>
              </div>
            </div>

            <div v-if="applied && appliedSnapshot?.indicador" class="legend-box">
              <div class="legend-title">Intensidade</div>
              <div class="bar" />
              <div class="legend-scale">
                <span>{{ fmtValue(appliedSnapshot.indicador, legendMin) }}</span>
                <span>{{ fmtValue(appliedSnapshot.indicador, legendMax) }}</span>
              </div>
            </div>

          </div>
        </div>

        <div class="map-footnote">
          * Mapa interativo (Leaflet + CartoDB Dark). Os pontos representam alojamentos reais do dataset.
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 28px; color: var(--texto-branco); font-family: 'Inter', sans-serif; }
.page-header { margin-bottom: 16px; }
h1 { margin: 0; font-size: 46px; font-weight: 800; }
.accent { color: var(--cor-primaria); }
.rest { margin-left: 10px; color: #fff; }
.layout { display: grid; grid-template-columns: 380px 1fr; gap: 22px; align-items: start; }

.card {
  background: var(--bg-cartao);
  border: 1px solid var(--borda);
  border-radius: 18px;
  padding: 18px;
}
.field { margin-bottom: 14px; }
label { display:block; color:var(--texto-muted); font-size:16px; font-weight:700; margin-bottom:8px; }
.select-wrap { position: relative; }
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
.segmented { display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; }
.segmented.two { grid-template-columns: 1fr 1fr; }
.segmented button {
  background:var(--bg-cartao); border:1px solid var(--texto-cinza); color:var(--texto-muted);
  border-radius:12px; padding:10px; cursor:pointer; font-weight:600;
}
.segmented button.active { background: var(--cor-primaria); border-color: var(--cor-primaria); color:#fff; }
.zone-chip {
  display:flex; align-items:center; gap:10px;
  background:#1f1f1f; border:1px solid #4B5563; border-radius:12px; padding:10px 12px;
}
.zone-chip input { border:0; outline:none; background:transparent; color:var(--texto-branco); font-size:15px; width:100%; }
.pin-icon { width: 18px; height: 18px; opacity: 0.7; }

.actions { display:grid; grid-template-columns: 1fr 1fr; gap:14px; margin-top:8px; }
.btn { border-radius:14px; padding:12px 14px; font-size:16px; font-weight:800; cursor:pointer; border:1px solid transparent; }
.btn.primary { background: var(--cor-primaria); border-color: var(--cor-primaria); color:#fff; }
.btn.primary:hover { background: var(--cor-primaria-hover); }
.btn.primary:disabled { opacity: .6; cursor:not-allowed; }
.btn.ghost { background:transparent; border-color:var(--texto-cinza); color:var(--texto-muted); }
.btn.ghost:hover { border-color:var(--texto-cinza); color:var(--texto-branco); }
.btn.tiny { font-size: 13px; padding: 8px 12px; border-radius: 8px; }
.btn.full-width { width: 100%; margin-top: 8px; }

.note { margin-top: 10px; font-size: 13px; color: var(--texto-cinza); }
.note.error { color: var(--error); }
.note.subtle { opacity: 0.85; }

.map-card { border-radius:18px; overflow:hidden; border:1px solid var(--borda); background:var(--bg-escuro); position: relative; }
.map-container {
  height: calc(100vh - 140px);
  min-height: 520px;
  width: 100%;
  position: relative;
  z-index: 1; 
}

.map-overlay-top {
  position:absolute; top:16px; left:16px; right:16px; 
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  z-index: 1000; 
  pointer-events: none; 
}
.pill, .applied-pill {
  pointer-events: auto;
  display:inline-flex; align-items:center; gap:10px; padding:10px 12px; border-radius:999px;
  background: rgba(17, 24, 39, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color:#E5E7EB; font-weight:700; font-size: 14px;
  backdrop-filter: blur(4px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.dot { width:10px; height:10px; border-radius:999px; background: var(--cor-primaria); }

.overlay-ranking {
  position:absolute; left:16px; bottom:16px; width: 340px;
  padding:16px; border-radius:14px;
  background: rgba(17, 24, 39, 0.90);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  z-index: 1000;
  box-shadow: 0 10px 15px rgba(0,0,0,0.3);
  display: flex; flex-direction: column;
}
.overlay-title { font-weight: 900; font-size: 16px; color:#fff; }
.overlay-sub { font-size: 13px; color:var(--texto-cinza); margin-top: 4px; margin-bottom: 12px; }

.zone-row {
  width:100%;
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 12px; border-radius:8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid transparent;
  color:var(--texto-muted);
  cursor:pointer;
  margin-bottom: 6px;
  transition: all 0.2s;
}
.zone-row:hover { background: rgba(255,255,255,0.1); }
.zone-row.active { border-color: var(--cor-primaria); background: rgba(79, 70, 229, 0.15); }
.zname { font-weight: 600; font-size: 14px; }
.zval { font-weight: 800; font-size: 14px; }

.zone-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.15);
}
.zd-title { font-weight: 800; margin-bottom: 10px; color: #fff; font-size: 15px; }
.zd-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.zd-item {
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  padding: 8px 10px;
  display:flex; flex-direction: column; gap: 4px;
  color:var(--texto-cinza); font-size: 11px;
}
.zd-item b { font-size: 14px; color: #fff; }

.legend-box {
  position:absolute; right:16px; bottom:16px; width:220px; padding:12px;
  border-radius:14px; background: rgba(17, 24, 39, 0.90);
  border: 1px solid rgba(255, 255, 255, 0.15);
  z-index: 1000;
  backdrop-filter: blur(8px);
}
.legend-title { font-weight:800; font-size:13px; color:var(--texto-muted); margin-bottom:8px; }
.bar {
  height:8px; border-radius:999px;
  background: linear-gradient(90deg, #A1A1AA, var(--cor-primaria));
}
.legend-scale { display:flex; justify-content:space-between; margin-top:6px; font-size:12px; color:#D1D5DB; }

.map-footnote { margin-top: 10px; font-size: 12px; color: var(--texto-cinza); opacity: 0.8; }

@media (max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
  .map-container { height: 500px; }
  .overlay-ranking { width: calc(100% - 32px); bottom: 16px; left: 16px; }
  .legend-box { display: none; }
}
</style>
