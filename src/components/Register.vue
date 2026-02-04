<script setup>
import { ref, inject } from 'vue';

const emit = defineEmits(['voltar']);
const triggerToast = inject('triggerToast');
const triggerModal = inject('triggerModal');

const username = ref('');
const password = ref('');
const confirmPassword = ref('');

const handleRegister = async () => {
  if (!username.value || !password.value || !confirmPassword.value) {
    triggerToast("Por favor, preencha todos os campos.", "warning", "Campos em falta");
    return;
  }

  if (password.value !== confirmPassword.value) {
    triggerToast("As palavras-passe não coincidem.", "error", "Erro de Validação");
    return;
  }

  try {

    const checkUrl = `http://localhost:3000/users?username=${username.value}`;
    const checkResponse = await fetch(checkUrl);
    const existingUsers = await checkResponse.json();

    if (existingUsers.length > 0) {
      triggerToast("Este nome de utilizador já está em uso.", "warning", "Registo");
      return;
    }


    const response = await fetch('http://localhost:3000/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });

    if (response.ok) {
      triggerModal({
        type: 'success',
        title: 'Conta Criada!',
        description: `Bem-vindo, ${username.value}. A sua conta foi criada com sucesso.`,
        primaryBtnText: 'Ir para Login',
        onPrimary: () => { emit('voltar'); }
      });
    } else {
      triggerToast("Erro ao criar conta.", "error", "Erro");
    }
  } catch (error) {
    console.error("Erro ao registar:", error);
    triggerToast("Erro no servidor.", "error", "Erro de Sistema");
  }
};

const goBack = () => {
  emit('voltar');
};
</script>

<template>
  <div class="login-wrapper">
    <h1 class="page-title">
      Junte-se ao <span class="brand-highlight">InsideAirbnb</span>
    </h1>

    <div class="login-card">
      <h2 class="card-title">Criar Conta</h2>
      <div class="form-container">
        
        <div class="input-group">
          <img 
            src="@/assets/login/user.png" 
            alt="user" 
            class="input-icon" 
          />
          <input type="text" v-model="username" placeholder="Nome de Utilizador" class="form-input" />
        </div>

        <div class="input-group">
          <img 
            src="@/assets/login/lock.png" 
            alt="Ícone Senha" 
            class="input-icon" 
          />
          <input type="password" v-model="password" placeholder="Palavra-Passe" class="form-input" />
        </div>

        <div class="input-group">
          <img 
            src="@/assets/login/lock.png" 
            alt="Ícone Senha" 
            class="input-icon" 
          />
          <input type="password" v-model="confirmPassword" placeholder="Confirmar Palavra-Passe" class="form-input" />
        </div>

      </div>
    </div>

    <button class="btn-login" @click="handleRegister">Registar</button>
    <button class="btn-back" @click="goBack">Voltar ao Login</button>
  </div>
</template>

<style scoped>
.login-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-escuro);
  color: var(--texto-branco);
  padding: 20px;
}

.page-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 50px;
  text-align: center;
}

.brand-highlight {
  color: var(--cor-primaria);
}
.login-card {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 48px;
  width: 100%;
  max-width: 596px;
  background-color: var(--bg-cartao); 
  border-radius: 16px;
  border: 1px solid var(--borda-sutil); 
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  text-align: center;
  margin-bottom: 30px;
}

.card-title {
  font-size: 40px;
  font-weight: bold;
  margin-bottom: 0;
  color: var(--texto-branco);
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
}

.form-input {
  width: 100%;
  padding: 14px 24px 14px 80px;
  border-radius: 8px;
  border: 1px solid transparent;
  background-color: var(--bg-branco); 
  color: var(--texto-preto);           
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: var(--cor-primaria);
}

.form-input::placeholder {
  color: var(--texto-cinza); 
}

.btn-login {
  width: 100%;
  max-width: 400px;
  padding: 14px;
  border-radius: 8px;
  border: none;
  background-color: var(--cor-primaria);
  color: var(--texto-branco);
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login:hover {
  background-color: var(--cor-primaria-hover);
}

.btn-back {
  width: 100%;
  max-width: 400px;
  padding: 14px;
  border: none;
  background-color: transparent;
  color: var(--texto-branco);
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s;
  margin-top: 10px;
}

.btn-back:hover {
  color: var(--texto-branco);
}
</style>