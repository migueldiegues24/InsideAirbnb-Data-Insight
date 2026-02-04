<script setup>
import { computed } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'info', 
  },
  label: {
    type: String, 
    default: ''
  },
  message: {
    type: String, 
    required: true
  }
});

const toastClass = computed(() => `toast toast-${props.type}`);
</script>

<template>
  <div class="toast-wrapper">
    <label v-if="label" class="toast-label">{{ label }}</label>
    
    <div :class="toastClass">
      <div class="toast-icon">
        <img v-if="type === 'success'" src="@/assets/check.png" alt="Success" />
        
        <img v-else-if="type === 'error'" src="@/assets/close.png" alt="Error" />
        
        <img v-else-if="type === 'warning'" src="@/assets/warning.png" alt="Warning" />


      </div>
      <span>{{ message }}</span>
    </div>
  </div>
</template>

<style scoped>
.toast-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-family: 'Inter', sans-serif;
  animation: slideIn 0.3s ease-out;
}

.toast-label {
  font-size: 0.8rem;
  color: #a1a1aa;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1rem 1.2rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  width: 320px;
  height: 64px;
  box-sizing: border-box;
}

.toast-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; 
  font-weight: 900;
  font-family: sans-serif;
}

.toast-icon img { width: 28px; height: 28px; }

/* VARIANTES */
.toast-success { background-color: #e9fdf0; color: var(--sucess); }
.toast-error   { background-color: #fef2f2; color: var(--error); }
.toast-warning { background-color: #fffbeb; color: var(--warning); }
.toast-info    { background-color: var(--info); color: var(--cor-primaria); }

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
</style>