<script setup>
import { ref } from 'vue';

const props = defineProps({
  userName: String,
  currentPage: String
});

const emit = defineEmits(['logout', 'navigate']);

const handleLogout = () => {
  console.log("A iniciar logout...");
  emit('logout');
};
</script>

<template>
  <aside class="sidebar">
    <div class="logo-container">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" class="logo-circle"/>
      </svg>
      <h2>InsideAirbnb</h2>
    </div>

    <div class="section-title">
      <h3>Principal</h3>
      <hr />
    </div>

    <nav class="menu">
      <a href="#" class="menu-item" :class="{ active: currentPage === 'home' }" @click.prevent="emit('navigate', 'home')">
        <img src="@/assets/sidebar/home.png" alt="Home" class="icon" />
        Home
      </a>
      <a href="#" class="menu-item" :class=" { active: currentPage === 'mapa' }" @click.prevent="emit('navigate', 'mapa')">
        <img src="@/assets/sidebar/map.png" alt="Mapa" class="icon" />
        Mapa & Zonas
      </a>
      <a href="#" class="menu-item" :class="{ active: currentPage === 'explorar' } " @click.prevent="emit('navigate', 'explorar')">
        <img src="@/assets/sidebar/compass.png" alt="Explorar" class="icon" />
        Explorar
      </a>
      <a href="#" class="menu-item" :class="{ active: currentPage === 'analise' }" @click.prevent="emit('navigate', 'analise')">
        <img src="@/assets/sidebar/trend.png" alt="Análise" class="icon" />
        Análise
      </a>
      <a href="#" class="menu-item" :class="{ active: currentPage === 'alertas' }" @click.prevent="emit('navigate', 'alertas')">
        <img src="@/assets/sidebar/alert.png" alt="Alertas" class="icon" />
        Alertas
      </a>
      <a href="#" class="menu-item" :class="{ active: currentPage === 'exportar' }" @click.prevent="emit('navigate', 'exportar')">
        <img src="@/assets/sidebar/export.png" alt="Exportar" class="icon" />
        Exportar & Partilhar
      </a>
      <a href="#" class="menu-item" :class="{ active: currentPage === 'help' }" @click.prevent="emit('navigate', 'help')">
        <img src="@/assets/sidebar/question.png" alt="Ajuda" class="icon" />
        Ajuda
      </a>
    </nav>

    <div class="section-title mt-large">
      <h3>Opções</h3>
      <hr />
    </div>

    <div class="menu">
      <a href="#" class="menu-item" :class="{ active: currentPage === 'preferencias' }" @click.prevent="emit('navigate', 'preferencias')">
        <img src="@/assets/sidebar/setting.png" alt="Preferências" class="icon" />
        Preferências
      </a>
      <a href="#" @click.prevent="handleLogout" class="menu-item">
        <img src="@/assets/sidebar/exit.png" alt="Terminar Sessão" class="icon" />
        Terminar Sessão
      </a>
    </div>

    <div class="user-profile">
      <button class="btn-profile" @click="emit('navigate', 'perfil')">
        <img src="@/assets/sidebar/user.png" alt="Perfil" class="user-icon" />
        {{ userName }}
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 15%;
  min-width: 220px;
  height: 100vh;
  background-color: var(--bg-escuro);
  color: var(--texto-branco);
  display: flex;
  flex-direction: column;
  padding: 24px 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  border-right: 1px solid var(--borda);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.logo-circle {
  fill: var(--cor-primaria);
}

.logo-container h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--texto-branco);
}

.section-title {
  margin-bottom: 15px;
}

.section-title.mt-large {
  margin-top: 20px;
}

.section-title h3 {
  font-size: 14px;
  font-weight: 400;
  color: var(--texto-cinza); 
  margin: 0 0 8px 0;
}

.section-title hr {
  border: 0;
  height: 1px;
  background-color: var(--borda); 
  margin: 0;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--texto-muted);
  text-decoration: none;
  font-size: 14px;
  padding: 8px 0;
  transition: color 0.2s;
}

.menu-item:hover {
  color: var(--texto-branco);
}

.menu-item.active {
  color: var(--texto-branco);
  font-weight: 600;
}

.icon {
  width: 18px;
  height: 18px;
  color: var(--texto-cinza); 
}

.menu-item:hover .icon,
.menu-item.active .icon {
  color: var(--texto-branco); 
}

.user-profile {
  margin-top: auto; 
  padding-top: 20px;
}

.btn-profile {
  width: 100%;
  background-color: var(--cor-primaria); 
  color: var(--texto-branco);
  border: none;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-profile:hover {
  background-color: var(--cor-primaria-hover);
}

.user-icon {
  width: 20px;
  height: 20px;
}
</style>
