
<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';

const props = defineProps({
  user: Object
});

const alertFilters = reactive({
  type: '',
  severity: '',
  searchQuery: props.user?.defaultCity || ''
});

const alertsData = ref([]);

onMounted(async () => {
  try {
    const response = await fetch('/db.json');
    const data = await response.json();
    let listings = [];
    if (data.listings && typeof data.listings === 'object' && !Array.isArray(data.listings)) {
      listings = Object.values(data.listings).flat();
    } else {
      listings = data.listings || [];
    }
    
    const generatedAlerts = [];
    let idCounter = 1;

    const validPrices = listings.filter(l => l.price !== null && l.price !== undefined);
    const avgPrice = validPrices.reduce((acc, l) => acc + l.price, 0) / (validPrices.length || 1);

    const licenseCounts = {};
    listings.forEach(l => {
        if (l.license && l.license !== 'Exempt' && l.license !== 'null') {
             licenseCounts[l.license] = (licenseCounts[l.license] || 0) + 1;
        }
    });

    Object.entries(licenseCounts).forEach(([license, count]) => {
        if (count > 1) {
             generatedAlerts.push({
                id: idCounter++,
                title: 'Propriedades duplicadas',
                description: `A licença ${license} está associada a ${count} alojamentos diferentes.`,
                meta: `Licença partilhada`,
                severity: 'medium',
                action: 'Ver lista'
            });
        }
    });

    listings.forEach(l => {
        if (l.availability_365 !== null && l.availability_365 < 30) {
            generatedAlerts.push({
                id: idCounter++,
                title: 'Ocupação Excessiva',
                description: `Alojamento (ID: ${l.id}) apresenta apenas ${l.availability_365} dias disponíveis no ano.`,
                meta: `${l.neighbourhood_cleansed}, ${l.neighbourhood_group_cleansed} — Licença: ${l.license || 'N/A'}`,
                severity: 'high',
                action: 'Ver no mapa'
            });
        }

        if (l.price && l.price > avgPrice * 3) {
            generatedAlerts.push({
                id: idCounter++,
                title: 'Preço fora da média',
                description: `Preço de ${l.price}€ é significativamente superior à média (${Math.round(avgPrice)}€).`,
                meta: `${l.neighbourhood_cleansed} — ID: ${l.id}`,
                severity: 'medium',
                action: 'Ver no mapa'
            });
        }

        if (l.last_review && l.scrape_date) {
            const lastRev = new Date(l.last_review);
            const scrape = new Date(l.scrape_date);
            const diffTime = Math.abs(scrape - lastRev);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
            
            if (diffDays > 365) {
                generatedAlerts.push({
                    id: idCounter++,
                    title: 'Anúncio desatualizado',
                    description: `Última atividade registada em ${l.last_review}. Sem reviews há mais de 1 ano.`,
                    meta: `${l.neighbourhood_cleansed} — ID: ${l.id}`,
                    severity: 'low',
                    action: 'Contactar host'
                });
            }
        }

        if (l.review_scores_rating && l.review_scores_rating < 4.0) {
             generatedAlerts.push({
                id: idCounter++,
                title: 'Avaliações Baixas',
                description: `Alojamento com rating de ${l.review_scores_rating}/5. Possível problema de qualidade.`,
                meta: `${l.neighbourhood_cleansed} — Reviews: ${l.number_of_reviews}`,
                severity: 'medium',
                action: 'Ver Histórico'
            });
        }
    });

    const severityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
    generatedAlerts.sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity]);

    alertsData.value = generatedAlerts;

  } catch (error) {
    console.error("Erro ao carregar alertas:", error);
  }
});

const filteredAlerts = computed(() => {
  return alertsData.value.filter(alert => {
    const matchType = alertFilters.type ? alert.title.includes(alertFilters.type) : true;
    const matchSev = alertFilters.severity ? alert.severity === alertFilters.severity : true;
    
    const query = alertFilters.searchQuery.toLowerCase();
    const matchSearch = !query || 
      alert.description.toLowerCase().includes(query) || 
      alert.meta.toLowerCase().includes(query);

    return matchType && matchSev && matchSearch;
  });
});

const currentPage = ref(1);
const itemsPerPage = 50;

const paginatedAlerts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredAlerts.value.slice(start, end);
});

const totalPages = computed(() => Math.ceil(filteredAlerts.value.length / itemsPerPage));

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

watch([() => alertFilters.type, () => alertFilters.severity, () => alertFilters.searchQuery], () => {
  currentPage.value = 1;
});

const getBorderClass = (severity) => {
    switch(severity) {
        case 'high': return 'border-red';
        case 'medium': return 'border-yellow';
        case 'low': return 'border-green';
        default: return '';
    }
};
</script>

<template>
  <div class="alerts-container">
    
    <div class="header-section">
        <h1 class="page-title"><span>Alertas</span> de Anomalias</h1>
    </div>

    <div class="filters-bar">
        <div class="search-wrapper">
            <input 
                type="text" 
                v-model="alertFilters.searchQuery" 
                placeholder="Pesquisar rua, zona ou ID..." 
                class="search-input"
            >
        </div>

        <div class="select-group">
            <select v-model="alertFilters.type" class="custom-select">
                <option value="" selected>Tipo de Anomalia</option>
                <option value="Ocupação">Ocupação</option>
                <option value="Preço">Preço</option>
                <option value="Avaliações">Avaliações</option>
                <option value="Propriedades">Propriedades</option>
                <option value="Anúncio">Anúncio</option>
            </select>
            
            <select v-model="alertFilters.severity" class="custom-select">
                <option value="" selected>Gravidade</option>
                <option value="high">Alta</option>
                <option value="medium">Média</option>
                <option value="low">Baixa</option>
            </select>
        </div>

        <button class="apply-btn">Aplicar Filtros</button>
    </div>

    <div class="alerts-list">
        
        <div 
            v-for="alert in paginatedAlerts" 
            :key="alert.id" 
            class="alert-card"
            :class="getBorderClass(alert.severity)"
        >
            <div class="icon-container">
                <img src="@/assets/danger.png" alt="Alert Icon" width="28" height="28" />
            </div>

            <div class="text-content">
                <h3>{{ alert.title }}</h3>
                <p class="desc">{{ alert.description }}</p>
                <p class="meta">{{ alert.meta }}</p>
            </div>

            <div class="action-container">
                <button class="action-btn">{{ alert.action }}</button>
            </div>
        </div>

    </div>

    <div class="pagination-controls" v-if="totalPages > 1">
        <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">Anterior</button>
        <span class="page-info">Página {{ currentPage }} de {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">Próxima</button>
    </div>

  </div>
</template>

<style scoped>

.alerts-container {
    background-color: var(--bg-escuro); 
    min-height: 100vh;
    padding: 3rem 2rem;
    font-family: 'Inter', sans-serif;
    color: var(--texto-branco);
    display: flex;
    flex-direction: column;
    align-items: center;
}

.header-section {
    margin-bottom: 2.5rem;
    text-align: center;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}

.page-title span {
    color: var(--cor-primaria); 
}

.filters-bar {
    display: flex;
    gap: 1rem;
    margin-bottom: 2.5rem;
    align-items: center;
}

.search-wrapper {
    flex-grow: 1;
}

.search-input {
    width: 100%;
    background-color: var(--bg-cartao);
    color: var(--texto-cinza);
    border: 1px solid var(--borda);
    padding: 0.6rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    outline: none;
}

.select-group {
    display: flex;
    gap: 1rem;
}

.custom-select {
    background-color: var(--bg-cartao);
    color: var(--texto-cinza);
    border: 1px solid var(--borda);
    padding: 0.6rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    min-width: 160px;
    cursor: pointer;
    outline: none;
}

.apply-btn {
    background-color: var(--texto-cinza); 
    color: var(--bg-escuro);
    border: none;
    padding: 0.6rem 1.5rem;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}

.apply-btn:hover {
    background-color: var(--texto-branco);
}

.alerts-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    width: 100%;
    max-width: 1100px;
}

.alert-card {
    display: flex;
    align-items: center;
    background-color: var(--bg-cartao); 
    padding: 1.5rem;
    border-radius: 8px;
    gap: 1.5rem;
    border: 3px solid transparent; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}

.border-red { border-color: var(--error); }
.border-yellow { border-color: #f59e0b; }
.border-green { border-color: var(--success); }

.icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border: 2px solid var(--texto-branco);
    border-radius: 50%;
    color: var(--texto-branco);
    flex-shrink: 0;
}

.text-content {
    flex-grow: 1;
}

.text-content h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--texto-branco);
}

.desc {
    margin: 0 0 0.5rem 0;
    font-size: 0.95rem;
    color: var(--texto-branco);
    line-height: 1.4;
}

.meta {
    margin: 0;
    font-size: 0.75rem;
    color: var(--texto-cinza);
    opacity: 0.8;
}

.action-container {
    flex-shrink: 0;
}

.action-btn {
    background-color: var(--cor-primaria);
    color: var(--texto-branco);
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
    white-space: nowrap;
}

.action-btn:hover {
    background-color: var(--cor-primaria-hover);
}

@media (max-width: 768px) {
    .filters-bar {
        flex-direction: column;
    }
    .alert-card {
        flex-direction: column;
        text-align: center;
        align-items: center;
    }
    .text-content {
        width: 100%;
    }
    .action-btn {
        width: 100%;
    }
}

.pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
    margin-top: 2rem;
    width: 100%;
    max-width: 1100px;
}

.page-btn {
    background-color: var(--bg-cartao);
    color: var(--texto-branco);
    border: 1px solid var(--borda);
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
    background-color: var(--cor-primaria);
    border-color: var(--cor-primaria);
}

.page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.page-info {
    color: var(--texto-cinza);
    font-size: 0.9rem;
}
</style>
