<script setup>
import { ref, onMounted, inject, watch } from 'vue';
import pinIcon from '../assets/location.png';

const props = defineProps({
  userLogado: Object
});

const emit = defineEmits(['save']);
const triggerToast = inject('triggerToast');

const selectedCity = ref('');
const availableCities = ref([]);
const showDropdown = ref(false);
const saving = ref(false);

onMounted(async () => {
  try {
    const res = await fetch('/db.json');
    const data = await res.json();
    let listings = [];
    if (data.listings && !Array.isArray(data.listings)) {
      listings = Object.values(data.listings).flat();
    } else {
      listings = data.listings || [];
    }
    const cities = new Set(listings.map(l => l.city || l.neighbourhood_group_cleansed).filter(Boolean));
    availableCities.value = Array.from(cities).sort();
  } catch (e) {
    console.error("Erro ao carregar cidades:", e);
  }
});

watch(() => props.userLogado, (newVal) => {
  if (newVal && newVal.defaultCity) {
    selectedCity.value = newVal.defaultCity;
  }
}, { immediate: true });

const savePreferences = async () => {
  if (!props.userLogado || !props.userLogado.id) return;

  saving.value = true;
  try {
    const response = await fetch(`http://localhost:3000/users/${props.userLogado.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ defaultCity: selectedCity.value })
    });

    if (response.ok) {
      const updatedUser = await response.json();
      triggerToast('Cidade padrão atualizada com sucesso!', 'success');
      emit('save', updatedUser);
    } else {
      triggerToast('Erro ao guardar preferências.', 'error');
    }
  } catch (e) {
    triggerToast('Erro de conexão ao servidor.', 'error');
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <div class="prefs-page">
    <h1 class="page-title">Preferências</h1>
    
    <div class="prefs-card">
      <div class="form-group">
        <label>Cidade Padrão</label>
        <p class="desc">Esta cidade será selecionada automaticamente ao entrar na aplicação.</p>
        
        <div class="dropdown-wrapper">
          <button class="location-btn" @click="showDropdown = !showDropdown">
            <img :src="pinIcon" alt="" class="location-icon" />
            <span>{{ selectedCity || 'Selecionar Cidade' }}</span>
            <span class="chev">▼</span>
          </button>

          <div v-if="showDropdown" class="dropdown-list">
            <div v-for="city in availableCities" :key="city" class="dropdown-item" 
                 @click="selectedCity = city; showDropdown = false">
              {{ city }}
            </div>
          </div>
        </div>
      </div>

      <button class="save-btn" @click="savePreferences" :disabled="saving">
        {{ saving ? 'A guardar...' : 'Guardar Alterações' }}
      </button>
    </div>
  </div>
</template>

<style scoped>

.prefs-page {
  background-color: var(--bg-escuro);
  min-height: 100vh;
  padding: 2rem;
  color: var(--texto-branco);
  font-family: 'Inter', sans-serif;
}
.page-title { 
  font-size: 2.5rem; 
  font-weight: 700; 
  margin-bottom: 2rem; 
  color: var(--cor-primaria);
}

.prefs-card { 
  background-color: var(--bg-cartao); 
  padding: 2rem; 
  border-radius: 12px; 
  border: 1px solid var(--borda-sutil); 
  max-width: 600px;
 }
.form-group { 
  margin-bottom: 2rem; 
}

.form-group label { 
  display: block; 
  font-size: 1.1rem; 
  font-weight: 600; 
  margin-bottom: 0.5rem; 
  }

.desc { color: var(--texto-cinza); font-size: 0.9rem; margin-bottom: 1rem; }

.dropdown-wrapper { position: relative; width: 100%; max-width: 300px; }
.location-btn {
  width: 100%; background: var(--texto-branco); color: var(--bg-escuro); border: none;
  padding: 12px 16px; border-radius: 8px; font-weight: bold; cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
}
.location-icon { width: 16px; height: 16px; }
.dropdown-list {
  position: absolute; top: 110%; left: 0; right: 0; background: var(--texto-branco);
  border-radius: 8px; padding: 8px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10;
  max-height: 200px; overflow-y: auto;
}
.dropdown-item { padding: 10px 16px; color: var(--bg-escuro); cursor: pointer; }
.dropdown-item:hover { background: rgba(0,0,0,0.1); }

.save-btn {
  background-color: var(--cor-primaria); color: white; border: none; padding: 12px 24px;
  border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.save-btn:hover { background-color: var(--cor-primaria-hover); }
.save-btn:disabled { opacity: 0.7; cursor: not-allowed; }
</style>