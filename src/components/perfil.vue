<script setup>
import { reactive, watch, ref, onMounted } from 'vue';

const props = defineProps({
  userLogado: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['navigate']);


const user = reactive({
  name: props.userLogado?.name || props.userLogado?.username || '',
  age: props.userLogado?.age || '',
  education: props.userLogado?.education || '',
  location: props.userLogado?.location || '',
  status: props.userLogado?.status || '',
  role: props.userLogado?.role || '',
  context: props.userLogado?.context || '',
  skills: props.userLogado?.skills || [],
  photo: props.userLogado?.photo || '',
  defaultCity: props.userLogado?.defaultCity || 'Gaia'
});

watch(() => props.userLogado, (newUser) => {
  if (newUser) {
    user.name = newUser.name || newUser.username || '';
    user.age = newUser.age || '';
    user.education = newUser.education || '';
    user.location = newUser.location || '';
    user.status = newUser.status || '';
    user.role = newUser.role || '';
    user.context = newUser.context || '';
    user.skills = newUser.skills || [];
    user.photo = newUser.photo || '';
    user.defaultCity = newUser.defaultCity || 'Gaia';
  } else {

    user.name = '';
    user.age = '';
    user.education = '';
    user.location = '';
    user.status = '';
    user.role = '';
    user.context = '';
    user.skills = [];
    user.photo = '';
    user.defaultCity = 'Gaia';
  }
});

const fileInput = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64Image = e.target.result;
    user.photo = base64Image;

    if (props.userLogado?.id) {
      try {
        await fetch(`http://localhost:3000/users/${props.userLogado.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ photo: base64Image })
        });
      } catch (err) {
        console.error("Erro ao guardar foto:", err);
      }
    }
  };
  reader.readAsDataURL(file);
};

const allListings = ref([]);
const alertCount = ref(0);
const exportCardTitle = ref('A carregar dados...');
const analysisCardTitle = ref('A carregar dados...');

onMounted(async () => {
  try {
    const response = await fetch('/db.json');
    const data = await response.json();
    if (data.listings && typeof data.listings === 'object' && !Array.isArray(data.listings)) {
      allListings.value = Object.values(data.listings).flat();
    } else {
      allListings.value = data.listings || [];
    }
    calculateAlerts();
  } catch (error) {
    console.error("Erro ao carregar alertas para perfil:", error);
  }
});

const calculateAlerts = () => {
    if (!allListings.value.length) return;

    const city = user.defaultCity;
    const cityListings = city ? allListings.value.filter(l => 
        (l.city === city || l.neighbourhood_group_cleansed === city)
    ) : allListings.value;

    if (cityListings.length === 0) {
        alertCount.value = 0;
        exportCardTitle.value = 'Sem dados para exportar nesta zona';
        analysisCardTitle.value = 'Sem dados para análise nesta zona';
        return;
    }

    const validPrices = cityListings.filter(l => l.price !== null && l.price !== undefined);
    const avgPrice = validPrices.reduce((acc, l) => acc + l.price, 0) / (validPrices.length || 1);

    let count = 0;
    cityListings.forEach(l => {
        let isAnomaly = false;
        if (l.availability_365 !== null && l.availability_365 < 30) isAnomaly = true;
        if (l.price && l.price > avgPrice * 3) isAnomaly = true;
        if (l.review_scores_rating && l.review_scores_rating < 4.0) isAnomaly = true;
        
        if (isAnomaly) count++;
    });
    alertCount.value = count;

    exportCardTitle.value = `${cityListings.length} registos em ${city} disponíveis para exportação`;
    analysisCardTitle.value = `Preço médio de ${Math.round(avgPrice)}€ em ${city}. Veja a análise completa.`;
};

watch(() => user.defaultCity, calculateAlerts);

const handleEdit = () => emit('navigate', 'edit_perfil');
const handleUpload = () => emit('navigate', 'exportar');
const handleShare = () => emit('navigate', 'analise');
const handleAlerts = () => emit('navigate', 'alertas');
</script>

<template>
  <div class="profile-page">
    
    <section class="profile-header-card">
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <img v-if="user.photo" :src="user.photo" class="avatar-img" />
          <svg v-else class="avatar-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="12" cy="8" r="5" />
            <path d="M20 21a8 8 0 1 0-16 0" />
          </svg>
          
          <button class="camera-btn" @click="triggerFileInput">
            <img src="@/assets/wireless.png" alt="Camera" />
          </button>
          <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleFileUpload">
        </div>
      </div>

      <div class="info-section">
        <div class="info-row">
          <span class="label">Nome:</span>
          <span class="value">{{ user.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Idade:</span>
          <span class="value">{{ user.age }}</span>
        </div>
        <div class="info-row">
          <span class="label">Educação:</span>
          <span class="value">{{ user.education }}</span>
        </div>
        <div class="info-row">
          <span class="label">Localidade:</span>
          <span class="value">{{ user.location }}</span>
        </div>
        <div class="info-row">
          <span class="label">Situação Familiar:</span>
          <span class="value">{{ user.status }}</span>
        </div>
      </div>

      <button class="edit-btn" @click="handleEdit">
        <span class="icon">✎</span> EDIT
      </button>
    </section>

    <div class="middle-grid">
      
      <div class="info-card">
        <div class="card-content-wrapper">
          <h2 class="card-title">Situação profissional</h2>
          <div class="divider"></div>
          
          <div class="text-block">
            <p><span class="text-label">Profissão:</span> {{ user.role }}</p>
          </div>
          
          <div class="text-block mt-4">
            <p><span class="text-label">Contexto profissional:</span> {{ user.context }}</p>
          </div>
        </div>
      </div>

      <div class="info-card">
        <div class="card-content-wrapper">
          <h2 class="card-title">Competências</h2>
          <div class="divider"></div>
          
          <ul class="skills-list">
            <li v-for="skill in user.skills" :key="skill">{{ skill }}</li>
          </ul>
        </div>
      </div>

    </div>

    <div class="alert-bar" @click="handleAlerts">
      <div class="alert-icon">
        <img src="@/assets/danger.png" alt="Alert" />
      </div>
      <div class="alert-content">
        <h3 v-if="alertCount > 0">Foram detetadas {{ alertCount }} anomalias na zona de {{ user.defaultCity }}</h3>
        <h3 v-else>Não foram detetadas anomalias na zona de {{ user.defaultCity }}</h3>
        <p>Consulte o separador “Alertas”</p>
      </div>
    </div>

    <div class="actions-grid">
      
      <div class="action-card" @click="handleUpload">
        <div class="action-icon">
          <img src="@/assets/sidebar/export.png" alt="Export" />
        </div>
        <h3>{{ exportCardTitle }}</h3>
        <p>Consulte o separador “Exportar”</p>
      </div>

      <div class="action-card" @click="handleShare">
        <div class="action-icon">
          <img src="@/assets/sidebar/trend.png" alt="Trend" />
        </div>
        <h3>{{ analysisCardTitle }}</h3>
        <p>Consulte o separador “Análise”</p>
      </div>

    </div>

  </div>
</template>

<style scoped>
.profile-page {
  background-color: var(--bg-escuro);
  color: var(--texto-branco);
  min-height: 100vh;
  padding: 2rem;
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-header-card {
  background-color: var(--bg-cartao);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  gap: 3rem;
  position: relative;
  align-items: center;
}

.avatar-section {
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}

.avatar-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.camera-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: var(--cor-primaria);
  border: 2px solid var(--bg-cartao);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: transform 0.2s;
}
.camera-btn:hover { transform: scale(1.1); }
.camera-btn img { width: 24px; height: 24px; }

.avatar-svg {
  width: 100%;
  height: 100%;
  color: var(--texto-cinza);
  stroke-width: 1.5px;
}

.info-section {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  border-left: 2px solid var(--cor-primaria);
  padding-left: 1.5rem;
}

.info-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.info-row .label {
  color: var(--texto-branco);
  font-size: 1.1rem;
  white-space: nowrap;
}

.info-row .value {
  color: var(--texto-branco);
  font-size: 1.1rem;
}

.edit-btn {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  background-color: transparent;
  border: 1px solid var(--cor-primaria);
  color: var(--texto-branco);
  padding: 0.4rem 1.2rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn .icon {
  color: var(--cor-primaria);
  font-size: 1rem;
}

.edit-btn:hover {
  background-color: var(--bg-escuro);
}

.middle-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr; 
  gap: 1.5rem;
}

.info-card {
  background-color: var(--bg-cartao);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
}

.card-content-wrapper {
  border-left: 2px solid var(--cor-primaria);
  padding-left: 1.5rem;
  height: 100%;
}

.card-title {
  color: var(--cor-primaria);
  font-size: 1.6rem;
  font-weight: 500;
  margin: 0;
  margin-bottom: 0.5rem;
}

.divider {
  height: 1px;
  background-color: var(--borda-sutil);
  margin-bottom: 1.5rem;
  width: 100%;
}

.text-block p {
  margin: 0;
  color: var(--texto-cinza);
  font-size: 0.9rem;
  line-height: 1.5;
}

.text-label {
  color: var(--texto-branco);
  font-weight: 500;
}

.mt-4 { margin-top: 1.5rem; }

.skills-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.skills-list li {
  color: var(--texto-cinza);
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
}

.alert-bar {
  background-color: var(--bg-cartao);
  border: 1px solid var(--borda-sutil);
  border-radius: 12px;
  padding: 1.2rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.alert-bar:hover {
  background-color: var(--bg-escuro);
}

.alert-icon {
  width: 40px;
  height: 40px;
  border: 1px solid var(--texto-branco);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-icon img { width: 24px; height: 24px; }

.alert-content h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--texto-branco);
}

.alert-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-cinza);
  margin-top: 4px;
}

.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.action-card {
  background-color: var(--bg-cartao);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.action-card:hover {
  background-color: var(--bg-escuro);
  transform: translateY(-2px);
}

.action-icon {
  margin-bottom: 1rem;
  color: var(--texto-branco);
}

.action-icon svg, .action-icon img {
  width: 40px;
  height: 40px;
}

.action-card h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--texto-branco);
  margin-bottom: 0.5rem;
}

.action-card p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-cinza);
}

@media (max-width: 900px) {
  .profile-header-card { flex-direction: column; text-align: center; gap: 1.5rem; }
  .info-section { border-left: none; padding-left: 0; align-items: center; }
  .middle-grid { grid-template-columns: 1fr; }
  .actions-grid { grid-template-columns: 1fr; }
  .card-content-wrapper { border-left: none; padding-left: 0; }
  .alert-bar { flex-direction: column; text-align: center; }
}
</style>