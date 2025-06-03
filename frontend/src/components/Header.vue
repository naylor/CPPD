<template>
  <header class="header-login">
    <!-- Logotipo -->
    <div class="logo">
      <img src="@/assets/logo.svg" alt="Logo" />
    </div>

    <!-- Área de login -->
    <div class="auth">
      <div v-if="!isAuthenticated" class="auth-fields">
        <input v-model="loginUsername" placeholder="Usuário" type="text" class="input-login" />
        <input v-model="password" placeholder="Senha" type="password" class="input-login" @keyup.enter="handleLogin" />
        <button @click="handleLogin" class="btn-acoes login-btn" :disabled="loginLoading">
          <span v-if="loginLoading">Entrando...</span>
          <span v-else>Login</span>
        </button>
        <button @click="goToRegister" class="btn-acoes register-btn" :disabled="loginLoading">
          Cadastrar
        </button>
      </div>
      <div v-else class="user-info">
        <span class="username clickable" @click="openChangePasswordModal">{{ username }}</span>
        <button @click="handleLogout" class="btn-acoes logout-btn">Sair</button>
      </div>
    </div>

    <!-- Aviso de login em andamento -->
    <div v-if="loginLoading" class="login-loading-message">
      Aguarde, efetuando login...
    </div>

    <!-- Container para mensagens -->
    <div class="message-container" v-if="loginError || showActivationError || activationMessage || activationError">
      <div v-if="loginError" class="custom-error-message">
        {{ loginError }}
      </div>
      <div v-if="showActivationError" class="activation-error-message">
        <p>
          Falha no login. Se você acabou de se cadastrar, verifique se recebeu o link de ativação no seu email.<br>
          <b>Não esqueça de olhar na pasta SPAM.</b>
        </p>
        <button class="btn-acoes resend-btn" :disabled="activationEmailLoading" @click="resendActivation">
          <span v-if="activationEmailLoading">Reenviando...</span>
          <span v-else>Reenviar link de ativação</span>
        </button>
      </div>
      <div v-if="activationMessage" class="success-message">
        {{ activationMessage }}
      </div>
      <div v-if="activationError" class="custom-error-message">
        {{ activationError }}
      </div>
    </div>

    <!-- Modal de alteração de senha -->
    <ChangePasswordModal v-if="showChangePasswordModal" :username="username" @close="closeChangePasswordModal" />
  </header>
</template>

<script>
import { login, logout, resendActivationLink } from "@/services/authService";
import { useAuthStore } from "@/stores/authStore";
import ChangePasswordModal from "@/components/ChangePasswordModal.vue";

export default {
  components: { ChangePasswordModal },
  data() {
    return {
      loginUsername: '',
      password: '',
      loginLoading: false,
      showActivationError: false,
      activationEmailLoading: false,
      activationMessage: '',
      activationError: '',
      loginError: '',
      messageTimers: {},
      showChangePasswordModal: false,
    };
  },
  computed: {
    authStore() {
      return useAuthStore();
    },
    username: {
      get() {
        return this.authStore.username;
      },
      set(val) {
        // Não altere o store diretamente ao digitar login!
      }
    },
    isAuthenticated() {
      return this.authStore.isAuthenticated;
    }
  },
  methods: {
    clearMessage(key) {
      if (this.messageTimers[key]) {
        clearTimeout(this.messageTimers[key]);
        this.messageTimers[key] = null;
      }
      this[key] = (typeof this[key] === 'boolean') ? false : '';
    },
    showMessage(key, value, timeout = 4000) {
      this.clearMessage(key);
      this[key] = value;
      if (timeout > 0) {
        this.messageTimers[key] = setTimeout(() => {
          this.clearMessage(key);
        }, timeout);
      }
    },
    async handleLogin() {
      if (this.loginLoading) return;
      this.loginLoading = true;
      this.clearMessage('loginError');
      this.clearMessage('activationMessage');
      this.clearMessage('activationError');
      this.clearMessage('showActivationError');
      try {
        const response = await login(this.loginUsername, this.password);

        if (response && response.userId) {
          this.authStore.login(this.loginUsername);
          localStorage.setItem("userId", response.userId);
          localStorage.setItem("username", this.loginUsername);
          this.loginUsername = '';
          this.password = '';
          this.$router.push({ name: "Home" });
        } else if (response && response.error === 'not_activated') {
          this.showMessage('showActivationError', true);
        } else {
          this.showMessage('showActivationError', true);
          this.showMessage('loginError', "Erro no login. Verifique suas credenciais ou se o usuário está ativado.");
        }
      } catch (error) {
        if (error && error.response && error.response.data && error.response.data.error === 'not_activated') {
          this.showMessage('showActivationError', true);
        } else {
          this.showMessage('showActivationError', true);
          this.showMessage('loginError', "Erro no login. Verifique suas credenciais ou se o usuário está ativado.");
        }
      } finally {
        this.loginLoading = false;
      }
    },
    async resendActivation() {
      if (!this.loginUsername) {
        this.showMessage('activationError', "Informe o usuário para reenviar o link.");
        return;
      }
      this.activationEmailLoading = true;
      this.clearMessage('activationMessage');
      this.clearMessage('activationError');
      try {
        const result = await resendActivationLink(this.loginUsername);
        if (result.alreadyActivated) {
          this.showMessage('activationMessage', "Sua conta já está ativada! Você pode fazer login normalmente.");
        } else {
          this.showMessage('activationMessage', "Link de ativação reenviado! Por favor, verifique seu email (inclusive a caixa de SPAM).");
        }
      } catch (e) {
        this.showMessage('activationError', "Erro ao reenviar o link de ativação. Tente novamente mais tarde.");
      } finally {
        this.activationEmailLoading = false;
      }
    },
    handleLogout() {
      logout();
      this.authStore.logout();
      this.password = '';
      this.loginUsername = '';
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('userId');
      localStorage.removeItem("isStaff");
      localStorage.removeItem("username");
      this.$emit('logout');
      this.$router.push({ name: "Home" });
    },
    goToRegister() {
      if (!this.loginLoading) {
        this.$router.push({ name: "NovoUsuarioUser" });
      }
    },
    openChangePasswordModal() {
      this.showChangePasswordModal = true;
    },
    closeChangePasswordModal() {
      this.showChangePasswordModal = false;
    }
  },
  beforeUnmount() {
    Object.values(this.messageTimers).forEach(timer => clearTimeout(timer));
  }
};
</script>

<style scoped>
.header-login {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background: #fff;
  color: #12366e;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1000;
  box-shadow: 0 2px 5px #0001;
  border-bottom: 1px solid #e6e8f0;
}

.logo img {
  height: 80px;
  margin: 6px 0 0 0;
}

.auth {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-right: 20px;
}

.auth-fields {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  color: #26334d;
  font-weight: 600;
  font-size: 1.01rem;
  padding-right: 3px;
}

.username.clickable {
  text-decoration: underline dotted;
  cursor: pointer;
}

.input-login {
  width: 124px;
  padding: 7px 13px;
  border: 1.5px solid #e6e8f0;
  border-radius: 4px;
  background: #fafbfc;
  color: #26334d;
  font-size: 0.97rem;
  outline: none;
  transition: border-color 0.18s;
}

.input-login:focus {
  border-color: #0075ff;
}

.btn-acoes {
  padding: 7px 17px;
  background: #0075ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.96rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s;
  margin-left: 0;
}

.btn-acoes:disabled {
  background: #e0e0e0;
  color: #aaa;
  cursor: not-allowed;
}

.btn-acoes:hover:enabled {
  background: #0050a4;
}

.login-btn {
  background: #14b714;
}

.login-btn:hover:enabled {
  background: #0e860e;
}

.logout-btn {
  background: #d92424;
}

.logout-btn:hover {
  background: #a50d0d;
}

.register-btn {
  background: #555dad;
}

.register-btn:hover:enabled {
  background: #373989;
}

.login-loading-message {
  position: absolute;
  right: 40px;
  top: 90px;
  background: #fff4f4;
  color: #d92424;
  border: 1px solid #fbcaca;
  border-radius: 5px;
  padding: 12px 22px;
  font-size: 1.02rem;
  font-weight: 500;
  box-shadow: 0 2px 5px #0001;
}

.message-container {
  position: absolute;
  right: 40px;
  top: 110px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1100;
  max-width: 360px;
}

.custom-error-message {
  background: #fff6f6;
  color: #d92424;
  border: 1px solid #fbcaca;
  border-radius: 5px;
  padding: 10px 20px;
  font-size: 1.01rem;
  font-weight: 500;
  box-shadow: 0 2px 5px #0001;
}

.activation-error-message {
  background: #fffbe4;
  color: #a67c00;
  border: 1px solid #ffe194;
  border-radius: 5px;
  padding: 14px 22px;
  font-size: 1.01rem;
  font-weight: 500;
  box-shadow: 0 2px 5px #0001;
}

.resend-btn {
  margin-top: 10px;
  background: #14b714;
}

.resend-btn:disabled {
  background: #e0e0e0;
  color: #aaa;
  cursor: not-allowed;
}

.success-message {
  background: #ecffe5;
  color: #267d12;
  border: 1px solid #bffcc2;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 0.97rem;
}
</style>