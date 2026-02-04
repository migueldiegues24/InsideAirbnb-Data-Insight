<script setup>
import { ref, inject } from 'vue';

const emit = defineEmits(['entrar', 'registar']);
const triggerToast = inject('triggerToast');
const triggerModal = inject('triggerModal');

const username = ref('');
const password = ref('');
const erro = ref('');

const handleLogin = async() => {
   try {
        const url = `http://localhost:3000/users?username=${username.value}&password=${password.value}`;
        
        const response = await fetch(url);
        const users = await response.json();

        if (users.length > 0) {
            console.log("Login com sucesso:", users[0]);
            return users[0]; 
        } else {
            triggerToast("Usuário ou senha incorretos!", "error", "Erro de Login");
            return null;
        }
    } catch (error) {
        console.error("Erro ao conectar ao servidor:", error);
        triggerToast("Erro no servidor.", "error", "Erro de Sistema");
        return null;
    }
};

const handleForgotPassword = () => {
    triggerModal({
      type: 'warning',
      title: 'Recuperar Palavra-Passe',
      description: 'Entre em contacto com o administrador do sistema para redefinir as suas credenciais.',
      primaryBtnText: 'Entendido',
    });
};

const tentarEntrar = async () => {
  const user = await handleLogin(); 
  
  if (user) {
    emit('entrar', user); 
  }
}

const goToRegister = () => {
  emit('registar');
};
</script>

<template>
  <div class="login-wrapper">
    <h1 class="page-title">
      Bem-Vindo ao <span class="brand-highlight">InsideAirbnb</span>
    </h1>

    <div class="login-card">
      <h2 class="card-title">Iniciar Sessão</h2>
      <div class="form-container">
        
        <div class="input-group">
          <img 
            src="@/assets/login/user.png" 
            alt="user" 
            class="input-icon" 
          />
          <input type="text" v-model="username" placeholder="Nome" class="form-input" />
        </div>

        <div class="input-group">
          <img 
            src="@/assets/login/lock.png" 
            alt="Ícone Senha" 
            class="input-icon" 
          />
          <input type="password" v-model="password" placeholder="Palavra-Passe" class="form-input" />
        </div>

        <div class="forgot-password-link">
          <a href="#" @click.prevent="handleForgotPassword">Esqueceu-se da palavra-passe?</a>
        </div>
      </div>
    </div>

    <button class="btn-login" @click="tentarEntrar">Entrar</button>
    <button class="btn-register" @click="goToRegister">Criar Conta</button>
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

.forgot-password-link {
  text-align: center;
  margin-top: -5px;
}

.forgot-password-link a {
  color: var(--texto-branco);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-password-link a:hover {
  color: var(--texto-branco);
  text-decoration: underline;
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

.btn-register {
  width: 100%;
  max-width: 400px;
  padding: 14px;
  border-radius: 8px;
  border: none;
  
  background-color: transparent;
  color: var(--texto-cinza);
  
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s;
  margin-top: 10px;
}

.btn-register:hover {
  color: var(--texto-branco);
}
</style>