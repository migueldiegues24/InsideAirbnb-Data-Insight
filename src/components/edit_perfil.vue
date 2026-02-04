<script setup>
import { reactive, ref, watch, inject } from 'vue';

const props = defineProps({
  userLogado: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['cancel', 'save']);
const triggerToast = inject('triggerToast');

const formData = reactive({
  name: '',
  age: '',
  education: '',
  location: '',
  status: '',
  role: '',
  context: '',
  skills: [],
  photo: ''
});

watch(() => props.userLogado, (user) => {
  if (user) {
    formData.name = user.name || user.username || '';
    formData.age = user.age || '';
    formData.education = user.education || '';
    formData.location = user.location || '';
    formData.status = user.status || '';
    formData.role = user.role || '';
    formData.context = user.context || '';
    formData.skills = user.skills ? [...user.skills] : [];
    formData.photo = user.photo || '';
  }
}, { immediate: true });

const newSkill = ref('');

const addSkill = () => {
  if (newSkill.value.trim()) {
    formData.skills.push(newSkill.value.trim());
    newSkill.value = ''; 
  }
};

const removeSkill = (index) => {
  formData.skills.splice(index, 1);
};

const fileInput = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    formData.photo = e.target.result;
  };
  reader.readAsDataURL(file);
};

const cancelChanges = () => {
  emit('cancel');
};

const saveChanges = async () => {
  if (!props.userLogado || !props.userLogado.id) {
    triggerToast('Erro: Utilizador não identificado.', 'error');
    return;
  }

  try {

    const response = await fetch(`http://localhost:3000/users/${props.userLogado.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      const updatedUser = await response.json();
      triggerToast('Perfil atualizado com sucesso!', 'success');
      emit('save', updatedUser);
    } else {
      triggerToast('Erro ao atualizar perfil.', 'error');
    }
  } catch (error) {
    console.error(error);
    triggerToast('Erro de conexão ao servidor.', 'error');
  }
};
</script>

<template>
  <div class="edit-profile-page">
    
    <section class="edit-card header-section">
      
      <div class="avatar-wrapper">
        <img v-if="formData.photo" :src="formData.photo" class="avatar-img" />

        <button class="camera-btn" @click="triggerFileInput">
          <img src="@/assets/wireless.png" alt="Camera" />
        </button>
        <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleFileUpload">
      </div>

      <div class="personal-inputs">
        <div class="input-row">
          <label>Nome:</label>
          <input type="text" v-model="formData.name" class="gray-input">
        </div>
        <div class="input-row">
          <label>Idade:</label>
          <input type="text" v-model="formData.age" class="gray-input">
        </div>
        <div class="input-row">
          <label>Educação :</label>
          <input type="text" v-model="formData.education" class="gray-input">
        </div>
        <div class="input-row">
          <label>Localidade:</label>
          <input type="text" v-model="formData.location" class="gray-input">
        </div>
        <div class="input-row">
          <label>Situação Familiar:</label>
          <input type="text" v-model="formData.status" class="gray-input">
        </div>
      </div>
    </section>

    <div class="split-grid">
      
      <section class="edit-card">
        <h2 class="section-title">Situação profissional</h2>
        <div class="divider"></div>

        <div class="form-group">
          <label class="field-label">Profissão</label>
          <textarea v-model="formData.role" class="gray-input area-small" rows="2"></textarea>
        </div>

        <div class="form-group">
          <label class="field-label">Contexto profissional</label>
          <textarea v-model="formData.context" class="gray-input area-large" rows="5"></textarea>
        </div>
      </section>

      <section class="edit-card flex-col">
        <h2 class="section-title">Competências</h2>
        <div class="divider"></div>

        <div class="form-group">
          <label class="field-label">Adicionar competência:</label>
          <div class="add-skill-row">
            <input 
              type="text" 
              v-model="newSkill" 
              placeholder="Digite a sua competência" 
              class="gray-input"
              @keyup.enter="addSkill"
            >
            <button class="add-btn" @click="addSkill">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
        </div>

        <div class="skills-list">
          <div v-for="(skill, index) in formData.skills" :key="index" class="skill-item">
            <input type="text" v-model="formData.skills[index]" class="gray-input">
            <button class="remove-btn" @click="removeSkill(index)">×</button>
          </div>
        </div>

        <div class="action-buttons">
          <button class="btn-cancel" @click="cancelChanges">Cancelar alterações</button>
          <button class="btn-confirm" @click="saveChanges">Confirmar Alterações</button>
        </div>
      </section>

    </div>

  </div>
</template>

<style scoped>
.edit-profile-page {
  background-color: var(--bg-escuro);
  min-height: 100vh;
  padding: 2rem;
  color: var(--texto-branco);
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.edit-card {
  background-color: var(--bg-cartao);
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid var(--borda-sutil);
}

.flex-col {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header-section {
  display: flex;
  gap: 3rem;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid var(--texto-cinza);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--texto-cinza);
}
.avatar-circle svg { width: 80%; height: 80%; }

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

.personal-inputs {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-left: 2rem;
  border-left: 1px solid var(--borda-sutil);
}

.input-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.input-row label {
  width: 140px; 
  color: var(--texto-branco);
  font-size: 0.95rem;
}

.gray-input {
  width: 100%;
  background-color: #52525b; 
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  color: white;
  font-size: 0.9rem;
  outline: none;
}
.gray-input:focus {
  box-shadow: 0 0 0 2px var(--cor-primaria);
}

/* 2. GRELHA DIVIDIDA */
.split-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.5rem;
  align-items: start;
}

.section-title {
  color: var(--cor-primaria);
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
}

.divider {
  height: 1px;
  background-color: var(--borda-sutil);
  width: 100%;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.field-label {
  display: block;
  color: var(--texto-cinza);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.area-small { resize: none; }
.area-large { resize: none; }

.add-skill-row {
  display: flex;
  gap: 0.5rem;
}

.add-btn {
  background-color: var(--cor-primaria);
  border: none;
  border-radius: 6px;
  width: 42px; 
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  flex-shrink: 0;
}
.add-btn svg { width: 24px; height: 24px; }

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 2rem;
  flex-grow: 1; 
}

.skill-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--texto-cinza);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0 0.5rem;
}
.remove-btn:hover { color: var(--error); }

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: auto;
}

.btn-cancel {
  background-color: transparent;
  border: 1px solid var(--texto-cinza);
  color: var(--texto-cinza);
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}
.btn-cancel:hover { border-color: var(--texto-branco); color: var(--texto-branco); }

.btn-confirm {
  background-color: var(--cor-primaria);
  border: none;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-confirm:hover { background-color: var(--cor-primaria-hover); }

/* Responsividade */
@media (max-width: 900px) {
  .header-section { flex-direction: column; text-align: center; }
  .personal-inputs { border-left: none; padding-left: 0; width: 100%; }
  .input-row { flex-direction: column; align-items: flex-start; gap: 0.2rem; }
  .input-row label { width: 100%; }
  .split-grid { grid-template-columns: 1fr; }
}
</style>