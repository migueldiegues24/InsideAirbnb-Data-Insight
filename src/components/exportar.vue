<script setup>
import { ref, reactive, onMounted, computed, watch, inject } from 'vue';
import pinIcon from '../assets/location.png';

const props = defineProps({
  user: Object
});

const triggerToast = inject('triggerToast');

const listings = ref([]);

const filters = reactive({
  city: props.user?.defaultCity || '',
  startDate: '',
  endDate: '',
  legalStatus: 'Todos',
  roomType: 'Todos'
});

const fields = reactive({
  identificacao: [
    { id: 'id_alojamento', label: 'ID do Alojamento', checked: true }
  ],
  localizacao: [
    { id: 'bairro', label: 'Bairro', checked: false },
    { id: 'zona', label: 'Cidade', checked: true },
    { id: 'latitude', label: 'Latitude', checked: true },
    { id: 'longitude', label: 'Longitude', checked: true }
  ],
  financeiro: [
    { id: 'preco', label: 'Preço por Noite(€)', checked: true }
  ],
  avaliacao: [
    { id: 'reviews', label: 'Número de Reviews', checked: true }
  ],
  ocupacao: [
    { id: 'taxa_ocupacao', label: 'Taxa de ocupação(%)', checked: false },
    { id: 'dias_ocupados', label: 'Dias ocupados (ano)', checked: true }
  ],
  legal: [
    { id: 'estado_legal', label: 'Estado Legal', checked: true },
    { id: 'ultima_inspecao', label: 'Última Review', checked: true }
  ],
  caracteristicas: [
    { id: 'tipo', label: 'Tipo de alojamento', checked: true }
  ]
});

onMounted(async () => {
  try {
    const response = await fetch('/db.json');
    const data = await response.json();
    if (data.listings && typeof data.listings === 'object' && !Array.isArray(data.listings)) {
      listings.value = Object.values(data.listings).flat();
    } else {
      listings.value = data.listings || [];
    }

    const raw = localStorage.getItem('insideairbnb_export_payload');
    if (raw) {
      try {
        const payload = JSON.parse(raw);
        const f = payload.filters || payload.filtersSnapshot;
        if (f) {
          if (f.city) filters.city = f.city;
          if (f.propertyType) filters.roomType = f.propertyType;
        }
        localStorage.removeItem('insideairbnb_export_payload');
      } catch (_) {}
    }

    if (listings.value.length > 0) {
      if (!filters.startDate || !filters.endDate) {
        const dates = listings.value.map(l => l.scrape_date).filter(Boolean).sort();
        if (dates.length > 0) {
          filters.startDate = dates[0];
          filters.endDate = dates[dates.length - 1];
        }
      }
    }
  } catch (error) {
    console.error('Erro ao carregar os dados de exportação:', error);
  }
});

const availableCities = computed(() => {
  const cities = new Set(
    listings.value
      .map(l => l.neighbourhood_group_cleansed)
      .filter(Boolean)
  );
  return Array.from(cities).sort();
});

watch(availableCities, (cities) => {
  if (cities.length > 0 && !cities.includes(filters.city)) {
    if (props.user?.defaultCity && cities.includes(props.user.defaultCity)) {
      filters.city = props.user.defaultCity;
    } else {
      filters.city = cities[0];
    }
  }
});

const roomTypeMap = {
  "Entire home/apt": "Apartamento",
  "Private room": "Quarto Privado",
  "Shared room": "Quarto Partilhado",
  "Hotel room": "Quarto Hotel",
};

const availableRoomTypes = computed(() => {
  const types = new Set(listings.value.map(l => l.room_type).filter(Boolean));
  return Array.from(types).sort().map(t => ({
    value: t,
    label: roomTypeMap[t] || t
  }));
});

const selectAll = () => {
  Object.values(fields).forEach(category => {
    category.forEach(field => field.checked = true);
  });
};

const clearAll = () => {
  Object.values(fields).forEach(category => {
    category.forEach(field => field.checked = false);
  });
};

const keyMap = {
  id_alojamento: 'id',
  bairro: 'neighbourhood_cleansed',
  zona: 'neighbourhood_group_cleansed',
  latitude: 'latitude',
  longitude: 'longitude',
  preco: 'price',
  reviews: 'number_of_reviews',
  taxa_ocupacao: 'occupancy_rate', 
  dias_ocupados: 'occupied_days',  
  estado_legal: 'legal_status',   
  ultima_inspecao: 'last_review',    
  tipo: 'room_type'
};

const getLegalStatus = (license) => {
    if (!license || license === 'null') return 'Ilegal';
    if (license === 'Exempt') return 'Em Análise';
    return 'Legal';
};

const downloadFile = (content, fileName, contentType) => {
  const blob = new Blob([content], { type: contentType });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
};

const exportData = (format) => {
  const selectedKeys = [];
  const headers = {};
  for (const category in fields) {
    fields[category].forEach(field => {
      if (field.checked) {
        const dataKey = keyMap[field.id];
        selectedKeys.push(dataKey);
        headers[dataKey] = field.label;
      }
    });
  }

  if (selectedKeys.length === 0) {
    triggerToast('Selecione pelo menos um campo para exportar.', 'warning', 'Exportação');
    return;
  }

  const filteredListings = listings.value.filter(l => {
    const cityValue = (l.neighbourhood_group_cleansed ?? '').toString();
    const matchCity = cityValue.toLowerCase() === (filters.city || '').toLowerCase();

    const scrapeDate = new Date(l.scrape_date);
    const startDate = new Date(filters.startDate);
    const endDate = new Date(filters.endDate);
    const matchDate = scrapeDate >= startDate && scrapeDate <= endDate;

    let matchLegal = true;
    if (filters.legalStatus !== 'Todos') {
      matchLegal = getLegalStatus(l.license) === filters.legalStatus;
    }

    let matchType = true;
    if (filters.roomType !== 'Todos') {
      matchType = l.room_type === filters.roomType;
    }

    return matchCity && matchDate && matchLegal && matchType;
  });

  const dataToExport = filteredListings.map(l => {
    const item = {};
    for (const key of selectedKeys) {
      switch (key) {
        case 'occupancy_rate':
          item[key] = l.availability_30 !== null ? (100 * (1 - (l.availability_30 / 30))).toFixed(1) : 'N/A';
          break;
        case 'occupied_days':
          item[key] = l.availability_365 !== null ? 365 - l.availability_365 : 'N/A';
          break;
        case 'legal_status':
          item[key] = getLegalStatus(l.license);
          break;
        default:
          item[key] = l[key] !== null && l[key] !== undefined ? l[key] : 'N/A';
      }
    }
    return item;
  });

  if (dataToExport.length === 0) {
    triggerToast('Nenhum dado encontrado com os filtros selecionados.', 'warning', 'Sem dados');
    return;
  }

  if (format === 'JSON') {
    const jsonContent = JSON.stringify(dataToExport, null, 2);
    downloadFile(jsonContent, 'export_data.json', 'application/json;charset=utf-8;');
    triggerToast('Exportação JSON concluída!', 'success', 'Sucesso');
  } else if (format === 'CSV') {
    const csvHeaders = selectedKeys.map(key => headers[key]).join(',');
    const csvRows = dataToExport.map(item => 
      selectedKeys.map(key => {
        let value = item[key];
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = `${csvHeaders}\n${csvRows.join('\n')}`;
    const bom = new Uint8Array([0xEF, 0xBB, 0xBF]); 
    const blob = new Blob([bom, csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'export_data.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    triggerToast('Exportação CSV concluída!', 'success', 'Sucesso');
  }
};

const showCityDropdown = ref(false);
</script>

<template>
  <div class="export-page-container">
    
    <div class="page-header">
      <h1><span>Exportar</span> & Partilhar</h1>
    </div>

    <div class="content-layout">
      
      <aside class="filters-panel">
        <div class="filters-header-text">
          <h2>Filtro de Dados</h2>
          <p>Configure os critérios para exportação</p>
        </div>

        <div class="form-group">
          <label>Fonte de Dados / Cidade</label>
          <div class="city-selector">
            <div class="dropdown-wrapper">
              <button class="location-btn" @click="showCityDropdown = !showCityDropdown">
                <img :src="pinIcon" alt="" class="location-icon" />
                <span>{{ filters.city || 'Selecionar' }}</span>
                <span class="chev">▼</span>
              </button>
              <div v-if="showCityDropdown" class="dropdown-list">
                <div v-for="city in availableCities" :key="city" class="dropdown-item" @click="filters.city = city; showCityDropdown = false">{{ city }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Intervalo de tempo</label>
          <div class="date-row">
            <div class="date-col">
              <span class="sub-label">Data Início</span>
              <input type="date" v-model="filters.startDate" class="dark-input date-input">
            </div>
            <div class="date-col">
              <span class="sub-label">Data Fim</span>
              <input type="date" v-model="filters.endDate" class="dark-input date-input">
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Tipo de alojamento</label>
          <select v-model="filters.roomType" class="dark-input">
            <option value="Todos">Todos</option>
            <option v-for="t in availableRoomTypes" :key="t.value" :value="t.value">
              {{ t.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Estado legal</label>
          <select v-model="filters.legalStatus" class="dark-input">
            <option>Todos</option>
            <option>Legal</option>
            <option>Ilegal</option>
            <option>Em Análise</option>
          </select>
        </div>
      </aside>

      <main class="main-content">
        
        <div class="selection-card">
          <div class="selection-header">
            <h3>Selecionar campos</h3>
            <div class="selection-actions">
              <button @click="selectAll" class="action-btn">Selecionar Todos</button>
              <button @click="clearAll" class="action-btn">Limpar</button>
            </div>
          </div>

          <div class="checkbox-grid">
            
            <div class="check-group">
              <span class="category-badge">Identificação</span>
              <label v-for="f in fields.identificacao" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

            <div class="check-group">
              <span class="category-badge">Localização</span>
              <label v-for="f in fields.localizacao" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

             <div class="check-group">
              <span class="category-badge">Financeiro</span>
              <label v-for="f in fields.financeiro" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

            <div class="check-group">
              <span class="category-badge">Avaliação</span>
              <label v-for="f in fields.avaliacao" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

            <div class="check-group">
              <span class="category-badge">Ocupação</span>
              <label v-for="f in fields.ocupacao" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

            <div class="check-group">
              <span class="category-badge">Legal</span>
              <label v-for="f in fields.legal" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

            <div class="check-group">
              <span class="category-badge">Características</span>
              <label v-for="f in fields.caracteristicas" :key="f.id" class="custom-checkbox">
                <input type="checkbox" v-model="f.checked">
                <span class="checkmark"></span>
                {{ f.label }}
              </label>
            </div>

          </div>
        </div>

        <div class="export-section">
          <h3>Formato de Exportação</h3>
          <div class="export-cards">
            
            <button class="export-card-btn" @click="exportData('CSV')">
              <div class="icon csv-icon">
                <img src="@/assets/csv.png" alt="CSV" />
              </div>
              <span>CSV</span>
            </button>

            <button class="export-card-btn" @click="exportData('JSON')">
              <div class="icon json-icon">
                <img src="@/assets/json.png" alt="JSON" />
              </div>
              <span>JSON</span>
            </button>

          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
.export-page-container {
  background-color: var(--bg-escuro);
  min-height: 100vh;
  padding: 2rem;
  color: var(--texto-branco);
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}
.page-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; }
.page-header span { color: var(--cor-primaria); }

.content-layout {
  display: flex;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  align-items: flex-start;
}

.filters-panel {
  width: 320px;
  background-color: var(--bg-cartao);
  padding: 1.5rem;
  border-radius: 12px;
  flex-shrink: 0;
}

.filters-header-text {
  text-align: center;
  margin-bottom: 2rem;
}
.filters-header-text h2 { font-size: 1.3rem; margin-bottom: 0.25rem; }
.filters-header-text p { color: var(--texto-cinza); font-size: 0.8rem; }

.form-group { margin-bottom: 1.5rem; }
.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--texto-muted);
}

.dark-input {
  width: 100%;
  background-color: var(--texto-branco); 
  color: var(--bg-escuro);
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  outline: none;
}

.date-row { display: flex; gap: 10px; }
.date-col { flex: 1; }
.sub-label { display: block; font-size: 0.75rem; color: var(--texto-cinza); margin-bottom: 2px; }
.date-input { font-size: 0.85rem; padding: 0.4rem; }

.static-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-left: 0.5rem;
}
.static-list p { margin: 0; color: var(--texto-muted); font-size: 0.9rem; }

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.selection-card {
  background-color: var(--bg-cartao);
  padding: 1.5rem;
  border-radius: 12px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.selection-header h3 { font-size: 1rem; font-weight: 700; margin: 0; }

.selection-actions { display: flex; gap: 0.5rem; }
.action-btn {
  background-color: var(--texto-muted);
  border: none;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  font-weight: 600;
  color: var(--bg-escuro);
}
.action-btn:hover { background-color: var(--texto-branco); }

.checkbox-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.check-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-badge {
  background-color: var(--texto-cinza); 
  color: var(--texto-branco);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
  width: fit-content;
  margin-bottom: 0.25rem;
}

.custom-checkbox {
  display: flex;
  align-items: center;
  color: var(--texto-muted);
  font-size: 0.9rem;
  cursor: pointer;
  padding-left: 0.5rem;
}

.custom-checkbox input {
  margin-right: 0.5rem;
  accent-color: var(--cor-primaria); 
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.export-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  margin-top: 0;
}

.export-cards {
  display: flex;
  gap: 1.5rem;
}

.export-card-btn {
  flex: 1;
  background-color: var(--texto-branco); 
  border: none;
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 140px;
  justify-content: center;
}

.export-card-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.export-card-btn span {
  color: var(--bg-escuro);
  font-weight: 700;
  font-size: 1rem;
}

.icon {
  width: 48px;
  height: 48px;
}
.icon img { width: 100%; height: 100%; object-fit: contain; }

@media (max-width: 900px) {
  .content-layout { flex-direction: column; }
  .filters-panel { width: 100%; }
}

.city-selector {
  display: flex;
  gap: 0.5rem;
}

.location-btn {
  background: var(--texto-branco);
  color: var(--bg-escuro);
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  height: 40px;
  width: 100%;
  min-width: 120px;
  font-weight: bold;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.location-icon { width: 16px; height: 16px; object-fit: contain; }
.dropdown-wrapper { position: relative; z-index: 50; width: 100%; }
.chev { font-size: 10px; margin-left: 4px; }

.dropdown-list {
  position: absolute;
  top: 110%;
  left: 0;
  right: 0;
  background: var(--texto-branco);
  border-radius: 12px;
  padding: 8px 0;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 20px;
  color: var(--bg-escuro);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: rgba(0,0,0,0.1);
}
</style>