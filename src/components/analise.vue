<script setup>
import { 
  ref, 
  onMounted, 
  onUnmounted,
  computed, 
  reactive, 
  watch, 
  shallowRef,
  nextTick,
  inject
} from 'vue';
import { Chart, registerables } from 'chart.js';
import iBars from '../assets/kpis/bars.png'
import iUp from '../assets/kpis/trend-up.png'
import iCalendar from '../assets/kpis/calendar.png'
import pinIcon from '../assets/location.png'


Chart.register(...registerables);

const props = defineProps({
  user: Object
});

const triggerToast = inject('triggerToast');

const listings = ref([]);

const activeTab = ref('timeseries')
const activeChartTab = ref('comparacoes');

const chartInstance = shallowRef(null);

const distChartInstances = shallowRef({ price: null, type: null, city: null });
const priceChartCanvas = ref(null);
const typeChartCanvas = ref(null);
const cityChartCanvas = ref(null);

const relChartInstances = shallowRef({ scatter: null, radar: null, combined: null });
const scatterCanvas = ref(null);
const radarCanvas = ref(null);
const combinedCanvas = ref(null);

const myChartCanvas = ref(null);
const showFilters = ref(true);

const filters = reactive({
  metric: 'avgPrice',
  timeScale: 'monthly',
  geoScale: 'city',
  period: 'last12months',
  compareWith: 'none',
  chartType: 'line',
  startDate: '',
  endDate: '',
});

const filterOptions = {
  metrics: [
    { value: 'avgPrice', text: 'Preço Médio por Noite' },
    { value: 'occupancy', text: 'Taxa de Ocupação' },
    { value: 'totalListings', text: 'Número de Alojamentos' },
  ],
  timeScales: [
    { value: 'monthly', text: 'Mensal' },
    { value: 'yearly', text: 'Anual' },
  ],
  chartTypes: [
    { value: 'line', text: 'Linhas' },
    { value: 'bar', text: 'Barras' },
  ],
};

onMounted(async () => {
  try {
    const response = await fetch('/db.json');
    const data = await response.json();
    if (data.listings && !Array.isArray(data.listings)) {
      listings.value = Object.values(data.listings).flat();
    } else {
      listings.value = data.listings || [];
    }
  } catch (error) {
    console.error('Erro ao carregar os dados:', error);
    triggerToast("Erro ao carregar dados.", "error", "Sistema");
  }
});

const processedData = ref({
  currentData: [],
  previousData: [],
  latestDate: null,
  previousDate: null,
});

const selectedCity = ref('');
const showCityDropdown = ref(false);

const availableCities = computed(() => {
  const cities = new Set(listings.value.map(l => l.city).filter(Boolean))
  return cities.size > 0 ? Array.from(cities).sort() : []
})

watch(availableCities, (cities) => {
  if (cities.length > 0 && !cities.includes(selectedCity.value)) {
    if (props.user?.defaultCity && cities.includes(props.user.defaultCity)) {
      selectedCity.value = props.user.defaultCity;
    } else {
      selectedCity.value = cities[0];
    }
  }
})

const filteredListings = computed(() => {
  if (!selectedCity.value) return listings.value
  return listings.value.filter(l => l.city === selectedCity.value)
})

watch(filteredListings, (newListings) => {
  if (!newListings || newListings.length === 0) return;

  const groupedByDate = newListings.reduce((acc, l) => {
    const date = l.scrape_date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(l);
    return acc;
  }, {});

  const uniqueDates = Object.keys(groupedByDate).sort((a, b) => new Date(b) - new Date(a));
  
  const latestDate = uniqueDates[0] || null;
  const previousDate = uniqueDates[1] || null;

  processedData.value = {
    currentData: latestDate ? groupedByDate[latestDate] : [],
    previousData: previousDate ? groupedByDate[previousDate] : [],
    latestDate,
    previousDate,
  };
});

const kpis = computed(() => {
  if (!chartData.value.datasets || chartData.value.datasets.length === 0) {
    return [];
  }

  const chartValues = chartData.value.datasets[0].data || [];
  const chartLabels = chartData.value.labels || [];
  
  const nonZeroValues = chartValues.filter(v => v > 0);

  if (chartValues.length === 0 || nonZeroValues.length === 0) {
    return [
        { title: 'Sem dados para apresentar', value: 'N/A', change: 'Selecione outros filtros', isPositive: true, icon: '🤷' },
        { title: 'Média do Período', value: 'N/A', change: 'Selecione outros filtros', isPositive: true, icon: '📈' },
        { title: 'Período Analisado', value: 'N/A', change: 'Selecione outros filtros', isPositive: true, icon: '📅' }
    ];
  }

  let lastValue = 0;
  let lastValueLabel = 'N/A';
  for (let i = chartValues.length - 1; i >= 0; i--) {
    if (chartValues[i] > 0) {
        lastValue = chartValues[i];
        lastValueLabel = chartLabels[i];
        break;
    }
  }

 const average = nonZeroValues.length > 0 
      ? nonZeroValues.reduce((a, b) => a + b, 0) / nonZeroValues.length 
      : 0;

  const formatValue = (value, metric) => {
    switch (metric) {
      case 'avgPrice':
        return `€${value.toFixed(2)}`;
      case 'occupancy':
        return `${value.toFixed(1)}%`;
      case 'totalListings':
         return Math.round(value).toLocaleString();
      default:
        return value.toFixed(2);
    }
  };
  
  const metricText = filterOptions.metrics.find(m => m.value === filters.metric)?.text || 'Métrica';

  const timeScaleText = filterOptions.timeScales.find(t => t.value === filters.timeScale)?.text || '';
  const periodText = 'Últimos 12 meses'; 
  return [
    { 
      title: `Valor Recente (${lastValueLabel})`,
      value: formatValue(lastValue, filters.metric),
      change: metricText,
      isPositive: true,
      icon: iBars
    },
    { 
      title: 'Média do Período',
      value: formatValue(average, filters.metric),
      change: 'Média dos valores mensais',
      isPositive: true,
      icon: iUp
    },
    { 
      title: 'Período Analisado',
      value: timeScaleText,
      change: periodText,
      isPositive: true,
      icon: iCalendar
    }
  ];
});

const chartData = computed(() => {
  const { currentData } = processedData.value;
  if (currentData.length === 0) {
    return { labels: [], datasets: [] };
  }

  let labels = [];
  let values = [];

  if (filters.timeScale === 'monthly') {
    labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    const monthlyData = Array(12).fill(0).map(() => ({ sum: 0, count: 0, totalAvailability: 0, listingsCount: 0 }));
    
    currentData.forEach(l => {
      if (l.last_review) {
        const reviewDate = new Date(l.last_review);
        if (!isNaN(reviewDate.getTime())) {
          const month = reviewDate.getMonth();
          if (l.price) {
            monthlyData[month].sum += l.price;
            monthlyData[month].count++;
          }
          monthlyData[month].totalAvailability += l.availability_30 || 0;
          monthlyData[month].listingsCount++;
        }
      }
    });

    if (filters.metric === 'avgPrice') {
      values = monthlyData.map(m => m.count > 0 ? m.sum / m.count : 0);
    } else if (filters.metric === 'occupancy') {
      values = monthlyData.map(m => m.listingsCount > 0 ? 100 * (1 - m.totalAvailability / (m.listingsCount * 30)) : 0);
    } else if (filters.metric === 'totalListings') {
      values = monthlyData.map(m => m.listingsCount);
    }
  }

  const selectedMetric = filterOptions.metrics.find(m => m.value === filters.metric) || {};
  
  return {
    labels: labels,
    datasets: [{
      label: selectedMetric.text || 'Valor',
      data: values,
      borderColor: '#818cf8',
      backgroundColor: filters.chartType === 'bar' ? '#818cf8' : 'transparent',
      borderWidth: 2,
      pointBackgroundColor: 'white',
      pointBorderColor: '#818cf8',
      pointRadius: 4,
      tension: 0.2
    }]
  };
});

const chartTitle = computed(() => {
    const metricText = filterOptions.metrics.find(m => m.value === filters.metric)?.text || '';
    return `Evolução Temporal - ${metricText}`;
});

const chartSubtitle = computed(() => {
    const timeScaleText = filterOptions.timeScales.find(t => t.value === filters.timeScale)?.text || '';
    return `Análise da tendência ao longo do tempo com escala ${timeScaleText.toLowerCase()}`;
});

const distributionChartData = computed(() => {
    const data = processedData.value.currentData;
    if (!data || data.length === 0) return { labels: [], datasets: [] };

    const stats = {};
    data.forEach(l => {
        const group = l.neighbourhood_group_cleansed || 'Desconhecido';
        stats[group] = (stats[group] || 0) + 1;
    });

    const sorted = Object.entries(stats).sort((a, b) => b[1] - a[1]);

    return {
        labels: sorted.map(s => s[0]),
        datasets: [{
            label: 'Alojamentos',
            data: sorted.map(s => s[1]),
            backgroundColor: '#818cf8',
            borderRadius: 4,
            barPercentage: 0.9,      
            categoryPercentage: 0.8, 
            maxBarThickness: 100      
        }]
    };
});

const priceDistributionData = computed(() => {
    const data = processedData.value.currentData;
    if (!data || data.length === 0) return { labels: [], datasets: [] };

    const bins = ['0-50€', '50-100€', '100-150€', '150-200€', '200-300€', '300€+'];
    const counts = [0, 0, 0, 0, 0, 0];

    data.forEach(l => {
        const p = l.price || 0;
        if (p <= 50) counts[0]++;
        else if (p <= 100) counts[1]++;
        else if (p <= 150) counts[2]++;
        else if (p <= 200) counts[3]++;
        else if (p <= 300) counts[4]++;
        else counts[5]++;
    });

    return {
        labels: bins,
        datasets: [{
            label: 'Alojamentos',
            data: counts,
            backgroundColor: '#818cf8',
            borderRadius: 4,
            barPercentage: 0.9,
            categoryPercentage: 0.9
        }]
    };
});

const typeDistributionData = computed(() => {
    const data = processedData.value.currentData;
    if (!data || data.length === 0) return { labels: [], datasets: [] };

    const stats = {};
    data.forEach(l => {
        const type = l.room_type || 'Outro';
        stats[type] = (stats[type] || 0) + 1;
    });

    return {
        labels: Object.keys(stats),
        datasets: [{
            data: Object.values(stats),
            backgroundColor: ['#818cf8', '#34d399', '#fbbf24', '#f87171'],
            borderWidth: 0
        }]
    };
});

const cityTypeDistributionData = computed(() => {
    const data = processedData.value.currentData;
    if (!data || data.length === 0) return { labels: [], datasets: [] };

    const cityStats = {};
    const typesSet = new Set();

    data.forEach(l => {
        const city = l.neighbourhood_group_cleansed || 'Desconhecido';
        const type = l.room_type || 'Outro';
        typesSet.add(type);

        if (!cityStats[city]) cityStats[city] = { total: 0, types: {} };
        cityStats[city].total++;
        cityStats[city].types[type] = (cityStats[city].types[type] || 0) + 1;
    });

    const sortedCities = Object.keys(cityStats).sort((a, b) => cityStats[b].total - cityStats[a].total);
    const sortedTypes = Array.from(typesSet).sort();
    const colors = ['#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'];

    return {
        labels: sortedCities,
        datasets: sortedTypes.map((type, index) => ({
            label: type,
            data: sortedCities.map(city => cityStats[city].types[type] || 0),
            backgroundColor: colors[index % colors.length],
            stack: 'stack0'
        }))
    };
});

const top3Locations = computed(() => {
    const data = processedData.value.currentData;
    if (!data || data.length === 0) return [];

    const stats = {};

    data.forEach(l => {
        const group = l.neighbourhood_group_cleansed || 'Desconhecido';
        if (!stats[group]) {
            stats[group] = { name: group, total: 0, licensed: 0, unlicensed: 0 };
        }
        stats[group].total++;
        
        if (l.license && l.license.toString().trim().length > 0) {
            stats[group].licensed++;
        } else {
            stats[group].unlicensed++;
        }
    });

    return Object.values(stats)
        .sort((a, b) => b.total - a.total)
        .slice(0, 3);
});

const scatterData = computed(() => {
    const data = processedData.value.currentData;
    if (!data) return { datasets: [] };
    
    const stats = {};
    data.forEach(l => {
        const hood = l.neighbourhood_cleansed || l.neighbourhood_group_cleansed || 'Outro';
        if (!stats[hood]) stats[hood] = { priceSum: 0, availSum: 0, count: 0 };
        stats[hood].priceSum += l.price || 0;
        stats[hood].availSum += l.availability_30 || 0; 
        stats[hood].count++;
    });

    const points = Object.keys(stats).map(hood => {
        const count = stats[hood].count;
        const avgPrice = count > 0 ? stats[hood].priceSum / count : 0;
        const avgOcc = count > 0 ? 100 * (1 - (stats[hood].availSum / (count * 30))) : 0;
        return { x: avgPrice, y: avgOcc, hood: hood, count: count };
    }).filter(p => p.x < 600 && p.count >= 2); 

    return {
        datasets: [{
            label: 'Bairros',
            data: points,
            backgroundColor: 'rgba(255, 90, 95, 0.6)', 
            borderColor: '#FF5A5F',
            borderWidth: 1,
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    };
});

const radarData = computed(() => {
    return {
        labels: ['Ocupação', 'Preço', 'Reviews', 'Disponibilidade', 'Comodidades'],
        datasets: [{
            label: 'Média da Cidade',
            data: [75, 60, 85, 40, 70], 
            fill: true,
            backgroundColor: 'rgba(255, 90, 95, 0.2)',
            borderColor: '#FF5A5F',
            pointBackgroundColor: '#FF5A5F',
            pointBorderColor: '#fff'
        }]
    };
});

const combinedData = computed(() => {
    const rawData = scatterData.value.datasets[0]?.data || [];

    const top6 = [...rawData].sort((a, b) => b.y - a.y).slice(0, 6);
    
    return {
        labels: top6.map(d => d.hood),
        datasets: [
            {
                label: 'Ocupação (%)',
                data: top6.map(d => d.y),
                backgroundColor: '#00A699', 
                borderRadius: 4,
                yAxisID: 'y'
            },
            {
                label: 'Preço Médio (€)',
                data: top6.map(d => d.x),
                backgroundColor: '#FF5A5F', 
                borderRadius: 4,
                yAxisID: 'y1'
            }
        ]
    };
});

const renderChart = () => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }
  Object.values(distChartInstances.value).forEach(inst => {
      if (inst) inst.destroy();
  });
  distChartInstances.value = { price: null, type: null, city: null };
  Object.values(relChartInstances.value).forEach(inst => {
      if (inst) inst.destroy();
  });
  relChartInstances.value = { scatter: null, radar: null, combined: null };

  if (activeTab.value === 'timeseries' && myChartCanvas.value) {
      const ctx = myChartCanvas.value.getContext('2d');
      if (!ctx) return;
    
      chartInstance.value = new Chart(ctx, {
      type: filters.chartType,
      data: chartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        resizeDelay: 200, 
        animation: false, 
        scales: {
          y: { beginAtZero: true, ticks: { color: '#a1a1aa' }, grid: { color: '#3f3f46' } },
          x: { ticks: { color: '#a1a1aa' }, grid: { color: '#3f3f46' } }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: '#000000' } }
        }
      }
    });
  } 
  else if (activeTab.value === 'charts' && activeChartTab.value === 'comparacoes' && myChartCanvas.value) {
      const ctx = myChartCanvas.value.getContext('2d');
      if (!ctx) return;
      chartInstance.value = new Chart(ctx, {
          type: 'bar',
          data: distributionChartData.value,
          options: {
              indexAxis: 'y',
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                  x: { beginAtZero: true, grid: { color: '#3f3f46' }, ticks: { color: '#a1a1aa' } },
                  y: { grid: { display: false }, ticks: { color: '#000000', autoSkip: false } }
              },
              plugins: { legend: { display: false } }
          }
      });
  }
  else if (activeTab.value === 'charts' && activeChartTab.value === 'distribuicoes') {
      if (priceChartCanvas.value) {
          distChartInstances.value.price = new Chart(priceChartCanvas.value.getContext('2d'), {
              type: 'bar',
              data: priceDistributionData.value,
              options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                      y: { beginAtZero: true, grid: { color: '#3f3f46' }, ticks: { color: '#a1a1aa' } },
                      x: { grid: { display: false }, ticks: { color: '#a1a1aa' } }
                  },
                  plugins: { legend: { display: false } }
              }
          });
      }

      if (typeChartCanvas.value) {
          distChartInstances.value.type = new Chart(typeChartCanvas.value.getContext('2d'), {
              type: 'pie',
              data: typeDistributionData.value,
              options: {
                  responsive: true,
                  resizeDelay: 200,
                  maintainAspectRatio: false,
                  plugins: { 
                      legend: { position: 'right', labels: { color: '#a1a1aa' } } 
                  }
              }
          });
      }

      if (cityChartCanvas.value) {
          distChartInstances.value.city = new Chart(cityChartCanvas.value.getContext('2d'), {
              type: 'bar',
              data: cityTypeDistributionData.value,
              options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: { 
                      x: { stacked: true, ticks: { color: '#a1a1aa' }, grid: { display: false } }, 
                      y: { stacked: true, ticks: { color: '#a1a1aa' }, grid: { color: '#3f3f46' } } 
                  },
                  plugins: { 
                      legend: { display: true, position: 'top', labels: { color: '#000000' } } 
                  }
              }
          });
      }
  }
  else if (activeChartTab.value === 'relacoes') {
    if (scatterCanvas.value) {
        relChartInstances.value.scatter = new Chart(scatterCanvas.value.getContext('2d'), {
            type: 'scatter',
            data: scatterData.value,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Preço Médio (€)' }, grid: { color: '#e5e7eb' } },
                    y: { title: { display: true, text: 'Ocupação (%)' }, beginAtZero: true, grid: { color: '#e5e7eb' } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.raw.hood}: €${ctx.raw.x.toFixed(0)} / ${ctx.raw.y.toFixed(0)}%`
                        }
                    }
                }
            }
        });
    }

    if (radarCanvas.value) {
        relChartInstances.value.radar = new Chart(radarCanvas.value.getContext('2d'), {
            type: 'radar',
            data: radarData.value,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: { 
                        grid: { color: '#e5e7eb' },
                        pointLabels: { font: { size: 11 }, color: '#374151' },
                        suggestedMin: 0, suggestedMax: 100
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    if (combinedCanvas.value) {
        relChartInstances.value.combined = new Chart(combinedCanvas.value.getContext('2d'), {
            type: 'bar',
            data: combinedData.value,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { type: 'linear', display: true, position: 'left', grid: { display: false } },
                    y1: { type: 'linear', display: true, position: 'right', grid: { display: false } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { position: 'bottom', labels: { usePointStyle: true } } }
            }
        });
    }
  }
};

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }
  Object.values(distChartInstances.value).forEach(inst => {
      if (inst) inst.destroy();
  });
  distChartInstances.value = { price: null, type: null, city: null };
  Object.values(relChartInstances.value).forEach(inst => {
      if (inst) inst.destroy();
  });
  relChartInstances.value = { scatter: null, radar: null, combined: null };
});

watch([chartData, distributionChartData, cityTypeDistributionData, scatterData, radarData, combinedData, activeTab, activeChartTab, () => filters.chartType], () => {
  nextTick(() => {
      requestAnimationFrame(() => renderChart());
  });
}, { deep: true });

</script>

<template>
  <main class="main-content">
    
    <div class="top-header">
        <div class="page-title">
            <h1 class="title-text"><span>Análise</span> de Alojamentos Locais</h1>
        </div>
    </div>

    <div class="navigation-container">
        <div class="nav-row">
            <div class="tabs-wrapper">
                <button 
                    @click="activeTab = 'timeseries'" 
                    :class="['tab-btn', { active: activeTab === 'timeseries' }]">
                    Séries temporais
                </button>
                <button 
                    @click="activeTab = 'charts'" 
                    :class="['tab-btn', { active: activeTab === 'charts' }]">
                    Gráficos
                </button>
            </div>

            <div class="city-selector">
              <div class="dropdown-wrapper" v-if="availableCities.length > 0">
                <button class="location-btn" @click="showCityDropdown = !showCityDropdown">
                  <img :src="pinIcon" alt="" class="location-icon" />
                  <span>{{ selectedCity }}</span>
                  <span class="chev">▼</span>
                </button>
                <div v-if="showCityDropdown" class="dropdown-list">
                  <div v-for="city in availableCities" :key="city" class="dropdown-item" @click="selectedCity = city; showCityDropdown = false">{{ city }}</div>
                </div>
              </div>
            </div>
        </div>

        <div v-if="activeTab === 'charts'" class="sub-tabs-wrapper">
            <button @click="activeChartTab = 'comparacoes'" :class="['sub-tab-btn', { active: activeChartTab === 'comparacoes' }]">
                Comparações
            </button>
            <button @click="activeChartTab = 'distribuicoes'" :class="['sub-tab-btn', { active: activeChartTab === 'distribuicoes' }]">
                Distribuições
            </button>
            <button @click="activeChartTab = 'relacoes'" :class="['sub-tab-btn', { active: activeChartTab === 'relacoes' }]">
                Relações
            </button>
        </div>
    </div>

    <div v-if="activeTab === 'timeseries'">
    <section v-if="showFilters" class="filters-panel">
        <div class="filters-grid">
            <div class="filter-item">
                <label for="metric">Métrica</label>
                <select id="metric" class="custom-select" v-model="filters.metric">
                    <option v-for="opt in filterOptions.metrics" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
                </select>
            </div>
            <div class="filter-item">
                <label for="timeScale">Escala Temporal</label>
                <select id="timeScale" class="custom-select" v-model="filters.timeScale">
                    <option v-for="opt in filterOptions.timeScales" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
                </select>
            </div>
            <div class="filter-item">
                <label>Escala Geográfica</label>
                <select class="custom-select" v-model="filters.geoScale" disabled>
                    <option value="city">Cidade</option>
                </select>
            </div>
            <div class="filter-item">
                <label>Período Temporal</label>
                <select class="custom-select" v-model="filters.period" disabled>
                    <option value="last12months">Últimos 12 meses</option>
                </select>
            </div>
            <div class="filter-item">
                <label>Comparar com</label>
                <select class="custom-select" v-model="filters.compareWith" disabled>
                    <option value="none">Nenhum</option>
                </select>
            </div>
            <div class="filter-item">
                <label for="chartType">Tipo de Gráfico</label>
                <select id="chartType" class="custom-select" v-model="filters.chartType">
                    <option v-for="opt in filterOptions.chartTypes" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
                </select>
            </div>
        </div>
    </section>

    <section class="kpi-grid">
      <div 
        v-for="kpi in kpis" 
        :key="kpi.title" 
        class="kpi-card"
        :class="[kpi.change === 'N/A' ? 'border-neutral' : kpi.isPositive ? 'border-positive' : 'border-negative']"
      >
        <div class="kpi-header">
            <img :src="kpi.icon" alt="" class="kpi-icon-img" />
          <p class="kpi-title">{{ kpi.title }}</p>
        </div>
        <p class="kpi-value">{{ kpi.value }}</p>
        <p class="kpi-change" :class="[kpi.change === 'N/A' ? 'text-neutral' : kpi.isPositive ? 'text-positive' : 'text-negative']">
          {{ kpi.change }}
        </p>
      </div>
    </section>

<section class="chart-section-wrapper">
      <div class="chart-container">
          <div class="chart-header">
              <h3>{{ chartTitle }}</h3>
              <p>{{ chartSubtitle }}</p>
          </div>
          
          <div class="canvas-wrapper">
              <canvas ref="myChartCanvas"></canvas>
          </div>

      </div>
    </section>
    </div>

    <div v-else-if="activeTab === 'charts'">
        <div v-if="activeChartTab === 'comparacoes'">
        <section class="chart-section-wrapper" style="height: 450px; margin-bottom: 2rem;">
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Distribuição por Zona</h3>
                    <p>Número de alojamentos por grupo de vizinhança</p>
                </div>
                <div class="canvas-wrapper">
                    <canvas ref="myChartCanvas"></canvas>
                </div>
            </div>
        </section>

        <section class="kpi-grid">
             <div v-for="loc in top3Locations" :key="loc.name" class="kpi-card">
                <div class="kpi-content">
                    <h3>{{ loc.name }}</h3>
                    <div class="kpi-value">{{ loc.total }}</div>
                    <div class="kpi-subtext" style="display: flex; gap: 10px; font-size: 0.85rem;">
                        <span style="color: #10b981;">{{ loc.licensed }} Lic.</span>
                        <span style="color: #ef4444;">{{ loc.unlicensed }} Não Lic.</span>
                    </div>
                </div>
            </div>
        </section>
        </div>

        <div v-else-if="activeChartTab === 'distribuicoes'" class="distribuicoes-container">
            <div class="charts-row">
                <div class="chart-card-half">
                    <h4>Distribuição por Preço Diário</h4>
                    <div class="canvas-wrapper"><canvas ref="priceChartCanvas"></canvas></div>
                </div>
                <div class="chart-card-half">
                    <h4>Tipo de Alojamento</h4>
                    <div class="canvas-wrapper"><canvas ref="typeChartCanvas"></canvas></div>
                </div>
            </div>
            
            <div class="chart-card-full">
                <h4>Distribuição por Cidade</h4>
                <div class="canvas-wrapper"><canvas ref="cityChartCanvas"></canvas></div>
            </div>
        </div>

        <div v-else-if="activeChartTab === 'relacoes'" class="relations-grid">
            <div class="card-white full-width">
                <div class="chart-header-inline">
                    <h3>Relação Preço vs Ocupação</h3>
                    <p>Análise da correlação entre preço médio e taxa de ocupação por bairro</p>
                </div>
                <div class="canvas-container-large">
                    <canvas ref="scatterCanvas"></canvas>
                </div>
            </div>
            <div class="card-white">
                <div class="chart-header-left">
                    <h3>Métricas de Performance</h3>
                    <p>Avaliação comparativa de indicadores-chave</p>
                </div>
                <div class="canvas-container-medium">
                    <canvas ref="radarCanvas"></canvas>
                </div>
            </div>
            <div class="card-white">
                <div class="chart-header-right">
                    <h3>Top Bairros - Análise Combinada</h3>
                    <p>Relação entre ocupação e preço médio</p>
                </div>
                <div class="canvas-container-medium">
                    <canvas ref="combinedCanvas"></canvas>
                </div>
            </div>
        </div>
    </div>

  </main>
</template>


<style scoped>
.main-content {
    flex-grow: 1;
    padding: 2rem 2.5rem;
    background-color: var(--bg-escuro);
    color: var(--texto-branco);
    height: 100vh;
    overflow-y: auto;
}

.top-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.title-text {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--texto-branco);
    margin-top: -10px;
}

.title-text span {
    color: var(--cor-primaria);
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
  min-width: 120px;
  font-weight: bold;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.location-icon { width: 16px; height: 16px; object-fit: contain; }
.dropdown-wrapper { position: relative; z-index: 50; }
.chev { font-size: 10px; margin-left: 4px; }

.dropdown-list {
  position: absolute;
  top: 110%;
  right: 0;
  background: var(--bg-branco);
  border-radius: 12px;
  padding: 8px 0;
  min-width: 160px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 20px;
  color: var(--texto-preto);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: rgba(0,0,0,0.05);
  color: var(--cor-primaria);
}

.navigation-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
    align-items: flex-start;
}

.nav-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    justify-content: space-between;
}

.tabs-wrapper {
    display: inline-flex;
    background-color: var(--bg-cartao); 
    padding: 4px;              
    border-radius: 9999px;     
    margin-bottom: 0;          
    border: 1px solid var(--borda-sutil); 
}

.tab-btn {
    background: transparent;   
    border: none;
    color: var(--texto-cinza);
    padding: 0.5rem 1.5rem;    
    border-radius: 9999px;     
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease; 
    min-width: 140px;          
    text-align: center;
}

.tab-btn:hover:not(.active) {
    color: var(--texto-branco); 
    background-color: rgba(255, 255, 255, 0.05); 
}

.tab-btn.active {
    background-color: var(--cor-primaria); 
    color: var(--texto-branco);
    box-shadow: 0 1px 3px rgba(0,0,0,0.3); 
}

.sub-tabs-wrapper {
    display: inline-flex;
    background-color: var(--bg-cartao);
    padding: 4px;
    border-radius: 9999px;
    margin-bottom: 0;          
    border: 1px solid var(--borda-sutil);
}

.sub-tab-btn {
    background: transparent;
    border: none;
    color: var(--texto-cinza);
    padding: 0.5rem 1.5rem;
    border-radius: 9999px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
    min-width: 140px;
    text-align: center;
}

.sub-tab-btn:hover:not(.active) {
    color: var(--texto-branco);
    background-color: rgba(255, 255, 255, 0.05);
}

.sub-tab-btn.active {
    background-color: var(--cor-primaria);
    color: var(--texto-branco);
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.filters-header {
    margin-bottom: 1rem;
}
.toggle-filters-btn {
    background-color: var(--bg-cartao);
    border: 1px solid var(--borda-sutil);
    color: var(--texto-branco);
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.toggle-filters-btn:hover {
    background-color: var(--cor-primaria-hover);
}

.filters-panel {
    background-color: var(--bg-cartao);
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin-bottom: 2rem;
    border: 1px solid var(--borda-sutil);
}

.filters-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.filter-item label {
    display: block;
    font-size: 0.875rem;
    color: var(--texto-cinza);
    margin-bottom: 0.5rem;
}

.custom-select {
    width: 100%;
    background-color: var(--bg-escuro);
    border: 1px solid var(--borda-sutil);
    color: var(--texto-branco);
    padding: 0.6rem 1rem;
    border-radius: 0.375rem;
    appearance: none;
    background-image: url("@/assets/down-arrow.png");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1em;
    cursor: pointer;
}
.custom-select:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}


.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 28px;
    row-gap: 10px;
    margin-bottom: 2rem;
}

.kpi-card {
    background-color: var(--bg-cartao);
    border-radius: 0.75rem;
    padding: 1.5rem;
    border-left-width: 1px;
    border-top-width: 1px;
    border-right-width: 1px;
    border-bottom-width: 1px;
    border-style: solid;
    transition: all 0.2s ease-in-out;
}



.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.kpi-icon-img {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex: 0 0 auto;
}


.kpi-title {
    font-size: 0.9rem;
    color: var(--texto-cinza);
    font-weight: 500;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--texto-branco);
    margin-bottom: 0.25rem;
}

.kpi-change {
    font-size: 0.875rem;
}

.text-positive { color: var(--success); }
.text-negative { color: var(--error); }
.text-neutral { color: var(--texto-cinza); }

.chart-section-wrapper {
  background-color: var(--bg-branco);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--borda-sutil);
  height: 400px; 
  display: flex;
  flex-direction: column;
}

.chart-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    min-height: 0; 
}

.chart-header {
    text-align: center;
    margin-bottom: 1rem;
    flex-shrink: 0; 
}

.chart-header h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--texto-preto);
}
.chart-header p {
    font-size: 0.875rem;
    color: var(--texto-preto);
}

.distribuicoes-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    height: 300px;
}

.chart-card-half, .chart-card-full {
    background-color: var(--bg-branco);
    border-radius: 0.75rem;
    padding: 1.5rem;
    border: 1px solid var(--borda-sutil);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chart-card-full {
    height: 350px;
}

.chart-card-half h4, .chart-card-full h4 {
    margin-bottom: 1rem;
    color: var(--texto-preto);
    font-size: 1rem;
    font-weight: 600;
}

.canvas-wrapper {
    flex-grow: 1;
    position: relative; 
    width: 100%;
    height: 100%;
    overflow: hidden; 
}

::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: var(--bg-escuro);
}
::-webkit-scrollbar-thumb {
    background: var(--borda-sutil);
    border-radius: 4px;
}

.relations-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.card-white {
    background-color: var(--bg-branco);
    border-radius: 1rem;
    padding: 1.5rem;
    color: #1f2937;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.full-width {
    grid-column: 1 / -1; 
    min-height: 420px;
}

.chart-header-inline { text-align: center; margin-bottom: 1rem; }
.chart-header-left { text-align: left; margin-bottom: 1rem; }
.chart-header-right { text-align: right; margin-bottom: 1rem; }

.card-white h3 { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem 0; color: var(--texto-preto); }
.card-white p { font-size: 0.85rem; color: var(--texto-cinza); margin: 0; }

.canvas-container-large { flex-grow: 1; position: relative; width: 100%; min-height: 320px; }
.canvas-container-medium { flex-grow: 1; position: relative; width: 100%; min-height: 280px; }
</style>
