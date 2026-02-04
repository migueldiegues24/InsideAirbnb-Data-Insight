<script setup>
import { computed } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'error', 'warning'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  primaryBtnText: {
    type: String,
    default: 'Aceitar'
  },
  secondaryBtnText: {
    type: String,
    default: '' 
  }
});


const emit = defineEmits(['primary', 'secondary']);


const iconClass = computed(() => {
  return {
    'icon-circle': true,
    [props.type]: true 
  };
});
</script>

<template>
  <div class="modal-card">
    <div :class="iconClass">
      
      <img v-if="type === 'error'" src="@/assets/mark.png" alt="Mark" width="64" height="64" />

      <img v-else-if="type === 'warning'" src="@/assets/warning.png" alt="Warning" width="64" height="64" />

    </div>

    <h3>{{ title }}</h3>
    <p>{{ description }}</p>

    <div class="modal-actions">
      <button 
        v-if="secondaryBtnText" 
        class="btn-secondary" 
        @click="$emit('secondary')"
      >
        {{ secondaryBtnText }}
      </button>
      
      <button 
        class="btn-primary" 
        @click="$emit('primary')"
      >
        {{ primaryBtnText }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-card {
  background-color: var(--bg-cartao); 
  width: 320px;
  padding: 2rem 1.5rem;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  color: var(--texto-branco);
  font-family: 'Inter', sans-serif;
}

.modal-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 1rem 0 0.5rem 0;
}

.modal-card p {
  color: var(--texto-cinza);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 2rem;
}

.icon-circle.success {
  background-color: var(--success);
  border-color: var(--success);
  color: var(--texto-branco);
}

/* BOTÕES */
.modal-actions {
  display: flex;
  gap: 1rem;
  width: 100%;
  justify-content: center;
}

.btn-primary {
  background-color: var(--cor-primaria);
  color: var(--texto-branco);
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
  transition: background-color 0.2s;
}

.btn-secondary {
  background-color: var(--texto-cinza);
  color: var(--bg-escuro);
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
  transition: background-color 0.2s;
}

.btn-primary:hover { background-color: var(--cor-primaria-hover); }
.btn-secondary:hover { background-color: var(--texto-branco); }
</style>