<script setup>
import { ref, provide } from 'vue';
import Login from './components/Login.vue';
import Register from './components/Register.vue';
import Home from './components/Home.vue'
import Analise from './components/analise.vue';
import Sidebar from './components/sidebar.vue';
import AjudaSuporte from './components/ajuda_suporte.vue';
import Alertas from './components/alertas.vue'
import Exportar from './components/exportar.vue'
import MapaZonas from './components/mapa_zonas.vue';
import Explorar from './components/explorar.vue'
import Perfil from './components/perfil.vue';
import EditPerfil from './components/edit_perfil.vue';
import Preferencias from './components/preferencias.vue';
import Toast from './components/Toast.vue';
import Cards from './components/Cards.vue';

const estaLogado = ref(false);
const loggedInUser = ref(null);
const currentPage = ref('home'); 
const mostrarRegisto = ref(false);

const toast = ref({ visible: false, message: '', type: 'info', label: '' });

const modal = ref({
  visible: false,
  type: 'success',
  title: '',
  description: '',
  primaryBtnText: 'OK',
  secondaryBtnText: '',
  onPrimary: () => {},
  onSecondary: () => {}
});

const triggerToast = (message, type = 'info', label = '') => {
  toast.value = { visible: true, message, type, label };
  setTimeout(() => { toast.value.visible = false; }, 3000);
};

const triggerModal = (options) => {
  modal.value = {
    visible: true,
    type: options.type || 'success',
    title: options.title || '',
    description: options.description || '',
    primaryBtnText: options.primaryBtnText || 'OK',
    secondaryBtnText: options.secondaryBtnText || '',
    onPrimary: () => {
      if (options.onPrimary) options.onPrimary();
      modal.value.visible = false;
    },
    onSecondary: () => {
      if (options.onSecondary) options.onSecondary();
      modal.value.visible = false;
    }
  };
};

provide('triggerToast', triggerToast);
provide('triggerModal', triggerModal);

const realizarLogin = (user) => {
  loggedInUser.value = user;
  estaLogado.value = true;
}

const realizarLogout = () => {
  estaLogado.value = false;
  loggedInUser.value = null;
  currentPage.value = 'home';
};

const navigateTo = (page) => {
  currentPage.value = page;
};

const handleSaveProfile = (updatedUser) => {
  loggedInUser.value = updatedUser;
  currentPage.value = 'perfil';
};

const handleSavePreferences = (updatedUser) => {
  loggedInUser.value = updatedUser;
};

</script>

<template>
  <div v-if="toast.visible" class="toast-container">
    <Toast :message="toast.message" :type="toast.type" :label="toast.label" />
  </div>

  <div v-if="modal.visible" class="modal-overlay">
    <Cards 
      :type="modal.type"
      :title="modal.title"
      :description="modal.description"
      :primaryBtnText="modal.primaryBtnText"
      :secondaryBtnText="modal.secondaryBtnText"
      @primary="modal.onPrimary()"
      @secondary="modal.onSecondary()"
    />
  </div>

  <div v-if="!estaLogado" class="full-screen">
    <Register v-if="mostrarRegisto" @voltar="mostrarRegisto = false" />
    <Login v-else @entrar="realizarLogin" @registar="mostrarRegisto = true" />
  </div>

  <div v-else class="app-layout">
    
    <Sidebar @logout="realizarLogout" :userName="loggedInUser.username" @navigate="navigateTo" :currentPage="currentPage" />

    <div class="content-area">
      <Home v-if="currentPage === 'home'" :user="loggedInUser" />
      <Analise v-else-if="currentPage === 'analise'" :user="loggedInUser" />
      <AjudaSuporte v-else-if="currentPage === 'help'" />
      <Alertas v-else-if="currentPage ==='alertas'" :user="loggedInUser" />
      <Exportar v-else-if="currentPage ==='exportar'" :user="loggedInUser" />
      <MapaZonas v-else-if="currentPage === 'mapa'" :user="loggedInUser" />
      <Explorar v-else-if="currentPage === 'explorar'" @goExport="currentPage = 'exportar'" />
      <Perfil v-else-if="currentPage === 'perfil'" :userLogado="loggedInUser" @navigate="navigateTo" />
      <Preferencias v-else-if="currentPage === 'preferencias'" :userLogado="loggedInUser" @save="handleSavePreferences" />
      <EditPerfil 
        v-else-if="currentPage === 'edit_perfil'" 
        :userLogado="loggedInUser" 
        @cancel="currentPage = 'perfil'" 
        @save="handleSaveProfile" 
      />
    </div>

  </div>
</template>

<style>

body { 
  margin: 0;
  padding: 0;
  background-color:
  #1E1E1E;
    }

.app-layout{
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}
/* Remove margens padrão do navegador para o site ocupar a tela toda */
.content-area {
  flex: 1;
  overflow-y: auto;
  position:relative;
  min-width: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}
</style>
