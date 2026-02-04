<script setup>
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Pie, Line } from 'vue-chartjs'
import { ref, onMounted, computed, watch } from 'vue'

const props = defineProps({
  user: Object
})

ChartJS.register(ArcElement, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

import kpiSectionIcon from '@/assets/Icon.png'
import pinIcon from '../assets/location.png'

import iHome from '../assets/kpis/home.png'
import iCheck from '../assets/kpis/check.png'
import iWarn from '../assets/kpis/warning.png'
import iUp from '../assets/kpis/trend-up.png'
import iBars from '../assets/kpis/bars.png'
import iDollar from '../assets/kpis/dollar.png'
import iUsers from '@/assets/kpis/users.png'
import iHourglass from '@/assets/kpis/hourglass.png'

const listings = ref([])
const selectedCity = ref('')
const showCityDropdown = ref(false)

onMounted(async () => {
  try {
    const response = await fetch('/db.json')
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

    const jsonData = await response.json()

    if (jsonData.listings && typeof jsonData.listings === 'object' && !Array.isArray(jsonData.listings)) {
      listings.value = Object.values(jsonData.listings).flat()
    } else if (jsonData.listings && Array.isArray(jsonData.listings)) {
      listings.value = jsonData.listings
    } else if (Array.isArray(jsonData)) {
      listings.value = jsonData
    } else {
      listings.value = []
    }
  } catch (error) {
    console.error('Could not load listings data:', error)
    listings.value = []
  }
})

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

const sortedUniqueDates = computed(() => {
  if (filteredListings.value.length === 0) return []
  return [...new Set(filteredListings.value.map(l => l.scrape_date))].sort((a, b) => new Date(b) - new Date(a))
})

const getUniqueListings = (date) => {
  if (!date) return []
  const dayListings = filteredListings.value.filter(l => l.scrape_date === date)
  
  const seen = new Set()
  return dayListings.filter(l => {
    if (!l.id) return true
    if (seen.has(l.id)) return false
    seen.add(l.id)
    return true
  })
}

const latestListings = computed(() => getUniqueListings(sortedUniqueDates.value[0]))
const previousListings = computed(() => getUniqueListings(sortedUniqueDates.value[1]))

const dataYear = computed(() => {
  const date = sortedUniqueDates.value[0]
  return date ? new Date(date).getFullYear() : new Date().getFullYear()
})

const pieData = computed(() => {
  const currentData = latestListings.value
  const total = currentData.length
  if (total === 0) return { labels: [], datasets: [] }

  const regularized = currentData.filter(l => l.license && l.license !== 'N/A' && l.license !== '').length
  
  let remainder = total - regularized

  const pending = Math.min(Math.floor(total * 0.03), remainder)
  remainder -= pending

  const analysis = Math.min(Math.floor(total * 0.02), remainder)
  remainder -= analysis

  const irregular = remainder

  return {
    labels: ['Regularizados', 'Irregulares', 'Pendentes', 'Em Análise'],
    datasets: [
      {
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444', '#3B82F6'],
        data: [regularized, irregular, pending, analysis]
      }
    ]
  }
})

const lineData = computed(() => {
  const currentData = latestListings.value
  if (currentData.length === 0) return { labels: [], datasets: [] }

  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  const newALData = Array(12).fill(0)
  const regularizedData = Array(12).fill(0)

  const currentYear = dataYear.value

  for (const listing of currentData) {
    if (listing.first_review) {
      const reviewDate = new Date(listing.first_review)
      if (reviewDate.getFullYear() === currentYear) {
        const month = reviewDate.getMonth()
        newALData[month]++
        if (listing.license && listing.license !== 'N/A' && listing.license !== '') {
          regularizedData[month]++
        }
      }
    }
  }

  return {
    labels,
    datasets: [
      {
        label: 'Novos AL',
        backgroundColor: '#4F46E5',
        borderColor: '#4F46E5',
        data: newALData
      },
      {
        label: 'Regularizações',
        backgroundColor: '#FFB020',
        borderColor: '#FFB020',
        data: regularizedData
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
}

const kpis = computed(() => {
  const currentData = latestListings.value
  const previousData = previousListings.value
  if (currentData.length === 0) return []

  const calculateMetrics = data => {
    const total = data.length
    if (total === 0) return { total: 0, regularized: 0, irregular: 0, avgOccupancy: 0, avgRevenue: 0, regularizedRate: 0 }

    const regularized = data.filter(l => l.license && l.license !== 'N/A' && l.license !== '').length

    const totalAvailability30d = data.reduce((sum, l) => sum + (l.availability_30 || 0), 0)
    const avgOccupancy = 100 * (1 - totalAvailability30d / (total * 30))

    const totalRevenue365d = data.reduce((sum, l) => sum + (l.estimated_revenue_l365d || 0), 0)
    const avgRevenue = totalRevenue365d / total / 12 

    return {
      total,
      regularized,
      irregular: total - regularized,
      avgOccupancy,
      avgRevenue,
      regularizedRate: (regularized / total) * 100
    }
  }

  const currentMetrics = calculateMetrics(currentData)
  const prevMetrics = calculateMetrics(previousData)

  const getChange = (current, previous, isPercentage = false) => {
    if (!previous || previous === 0) return { text: '', isPositive: true }

    const diff = current - previous
    const percent = (diff / previous) * 100
    const sign = percent > 0 ? '+' : ''

    const formatted = isPercentage ? `${sign}${diff.toFixed(1)}%` : `${sign}${percent.toFixed(1)}%`

    return {
      text: `${formatted} vs anterior`,
      isPositive: diff >= 0
    }
  }

  const countNewRegistrations = (data, referenceDateStr) => {
    if (!referenceDateStr) return 0
    const refDate = new Date(referenceDateStr)
    const thirtyDaysAgo = new Date(refDate)
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

    return data.filter(l => {
      if (!l.first_review) return false
      const reviewDate = new Date(l.first_review)
      return reviewDate >= thirtyDaysAgo && reviewDate <= refDate
    }).length
  }

  const newRegCurrent = countNewRegistrations(currentData, sortedUniqueDates.value[0])
  const newRegPrev = countNewRegistrations(previousData, sortedUniqueDates.value[1])
  const newRegChange = getChange(newRegCurrent, newRegPrev)

  const totalChange = getChange(currentMetrics.total, prevMetrics.total)
  const regRateChange = getChange(currentMetrics.regularizedRate, prevMetrics.regularizedRate, true)
  const irregularChange = getChange(currentMetrics.irregular, prevMetrics.irregular)
  const occChange = getChange(currentMetrics.avgOccupancy, prevMetrics.avgOccupancy, true)
  const revChange = getChange(currentMetrics.avgRevenue, prevMetrics.avgRevenue)

  const LISBON_POP = 545000

  const densityPer1000 = (totalListings) => (LISBON_POP > 0 ? (totalListings / LISBON_POP) * 1000 : 0)

  const avgRegularizationDays = (data, refDateStr) => {
    if (!refDateStr || data.length === 0) return 0
    const refDate = new Date(refDateStr)

    const diffs = data
      .filter(l => l.first_review && l.license && l.license !== 'N/A' && l.license !== '')
      .map(l => {
        const d = new Date(l.first_review)
        const diffMs = refDate - d
        return diffMs > 0 ? diffMs / (1000 * 60 * 60 * 24) : 0
      })
      .filter(v => v > 0)

    if (diffs.length === 0) return 0
    return diffs.reduce((a, b) => a + b, 0) / diffs.length
  }

  const densityCurrent = densityPer1000(currentMetrics.total)
  const densityPrev = densityPer1000(prevMetrics.total)
  const densityChange = getChange(densityCurrent, densityPrev) 

  const regDaysCurrent = avgRegularizationDays(currentData, sortedUniqueDates.value[0])
  const regDaysPrev = avgRegularizationDays(previousData, sortedUniqueDates.value[1])
  const regDaysChange = getChange(regDaysCurrent, regDaysPrev) 


  return [
    {
      title: 'Total de Alojamentos Ativos',
      value: currentMetrics.total.toLocaleString(),
      change: totalChange.text,
      isPositive: totalChange.isPositive,
      icon: iHome
    },
    {
      title: 'Taxa de alojamentos regularizados',
      value: `${currentMetrics.regularizedRate.toFixed(1)}%`,
      change: regRateChange.text,
      isPositive: regRateChange.isPositive,
      icon: iCheck
    },
    {
      title: 'AL irregulares',
      value: currentMetrics.irregular.toLocaleString(),
      change: irregularChange.text,
      isPositive: !irregularChange.isPositive, 
      icon: iWarn
    },
    {
      title: 'Novos registos (30 dias)',
      value: newRegCurrent.toLocaleString(),
      change: newRegChange.text,
      isPositive: newRegChange.isPositive,
      icon: iUp
    },

    {
      title: 'Densidade AL / 1000 hab.',
      value: densityCurrent.toFixed(2),
      change: densityChange.text,
      isPositive: densityChange.isPositive,
      icon: iUsers
    },

    {
      title: 'Ocupação média (30 dias)',
      value: `${currentMetrics.avgOccupancy.toFixed(1)}%`,
      change: occChange.text,
      isPositive: occChange.isPositive,
      icon: iBars
    },

    {
      title: 'Receita média estimada /AL',
      value: `€${currentMetrics.avgRevenue.toFixed(2)}`,
      change: revChange.text,
      isPositive: revChange.isPositive,
      icon: iDollar
    },

    {
      title: 'Tempo médio de Regularização',
      value: `${Math.round(regDaysCurrent)} dias`,
      change: regDaysChange.text,
      isPositive: !regDaysChange.isPositive, 
      icon: iHourglass
    }
  ]
})
</script>

<template>
  <main>
    <header class="top-header">
      <h1>Bem-vindo, <span class="highlight">{{ user?.username }}</span></h1>
    </header>

    <div class="divider-header"></div>

    <section>
      <div class="section-up">
        <h3 class="section-title">
          <img :src="kpiSectionIcon" alt="" class="section-icon" />
          KPI's exclusivos
        </h3>

        <div class="city-selector">
          <div class="dropdown-wrapper" v-if="availableCities.length > 0">
            <button class="location-btn" @click="showCityDropdown = !showCityDropdown">
              <img :src="pinIcon" alt="" class="location-icon" />
              <span>{{ selectedCity }}</span>
              <span class="chev">▼</span>
            </button>

            <div v-if="showCityDropdown" class="dropdown-list">
              <div v-for="city in availableCities" :key="city" class="dropdown-item"
                @click="selectedCity = city; showCityDropdown = false">
                {{ city }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="kpi-grid">
        <div
          v-for="(kpi, index) in kpis"
          :key="index"
          class="card kpi-card"
          :class="{ 'positive-border': kpi.isPositive, 'negative-border': !kpi.isPositive }"
        >
          <div class="card-header">
            <span>{{ kpi.title }}</span>
            <img :src="kpi.icon" alt="" class="kpi-icon" />
          </div>

          <div class="card-value">{{ kpi.value }}</div>

          <div class="card-change" :class="{ positive: kpi.isPositive, negative: !kpi.isPositive }">
            {{ kpi.change }}
          </div>
        </div>
      </div>
    </section>

    <div class="divider-header"></div>

    <section class="charts-section">
      <div class="card chart-card">
        <h4>Estado dos Alojamentos</h4>
        <div class="chart-wrapper">
          <Pie :data="pieData" :options="chartOptions" />
        </div>
      </div>

      <div class="card chart-card">
        <h4>Tendência Mensal de Regularizações e Novos AL ({{ dataYear }})</h4>
        <div class="chart-wrapper">
          <Line :data="lineData" :options="chartOptions" />
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
main {
  background-color: var(--bg-escuro);
  font-family: 'Arial', sans-serif;
  padding: 20px;
  color: var(--texto-branco);
  width: 100%;
  box-sizing: border-box;

  height: 100vh;
  display: flex;
  flex-direction: column;

  overflow-y: auto;
  overflow-x: hidden;
}


.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.highlight {
  color: var(--texto-branco);
  font-weight: bold;
}

h1 {
  font-size: 40px;
  font-weight: bold;
  color: var(--cor-primaria);
}

.section-up {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 24px;
  display: flex;
  font-weight: bold;
  align-items: center;
  gap: 10px;
}

.section-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.city-selector {
  display: flex;
  gap: 10px;
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

.location-btn.active {
  background: var(--cor-primaria);
  color: var(--texto-branco);
}

.location-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.dropdown-wrapper {
  position: relative;
  z-index: 50;
}

.chev {
  font-size: 10px;
  margin-left: 4px;
}

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

.divider-header {
  width: 100%;
  height: 1px;
  background-color: var(--texto-branco);
  opacity: 0.6;
  margin: 0 0 30px 0;
}

.card {
  background: var(--bg-branco);
  color: var(--texto-preto);
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 28px 10px;
  margin-bottom: 20px;
}

@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 700px) {
  .kpi-grid { grid-template-columns: 1fr; }
}


.kpi-card {
  background-color: var(--bg-branco);
  color: var(--texto-preto);
  border-style: solid;
  border-width: 1px;
  border-left-width: 4px;
}

.positive-border {
  border-color: var(--success);
}

.negative-border {
  border-color: var(--error);
}

.kpi-card .card-header {
  color: var(--texto-cinza);
}

.kpi-card .card-value {
  color: var(--texto-preto);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.kpi-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex: 0 0 auto;
}

.card-value {
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.card-change {
  font-size: 0.8rem;
  font-weight: bold;
}

.positive {
  color: var(--success);
}
.negative {
  color: var(--error);
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  min-height: 400px; 
}


.chart-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chart-wrapper {
  position: relative;
  flex-grow: 1;
  width: 100%;
  min-height: 0;
}

h4 {
  margin-bottom: 10px;
  font-size: 1rem;
}
</style>
