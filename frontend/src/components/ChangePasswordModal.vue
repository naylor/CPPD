<template>
  <div class="modal-bg" ref="modalBg" @click="closeOnBackground">
    <div class="modal-content">
      <h3>Alterar senha</h3>
      <form @submit.prevent="handleSubmit">
        <input v-model="currentPassword" type="password" autocomplete="current-password" placeholder="Senha atual"
          :disabled="loading" />
        <input v-model="newPassword" type="password" autocomplete="new-password" placeholder="Nova senha"
          :disabled="loading" />
        <input v-model="confirmPassword" type="password" autocomplete="new-password" placeholder="Confirme a nova senha"
          :disabled="loading" />
        <div v-if="error" class="modal-message error">{{ error }}</div>
        <div v-if="success" class="modal-message success">{{ success }}</div>
        <div class="modal-actions">
          <button type="submit" :disabled="loading">Alterar senha</button>
          <button type="button" class="cancel-btn" @click="$emit('close')" :disabled="loading">Cancelar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { changePassword } from "@/services/authService";
export default {
  props: ['username'],
  data() {
    return {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
      loading: false,
      error: '',
      success: ''
    };
  },
  methods: {
    async handleSubmit() {
      this.error = '';
      this.success = '';
      if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
        this.error = "Todos os campos são obrigatórios.";
        return;
      }
      if (this.newPassword.length < 6) {
        this.error = "A nova senha deve ter pelo menos 6 caracteres.";
        return;
      }
      if (this.currentPassword === this.newPassword) {
        this.error = "A nova senha deve ser diferente da senha atual.";
        return;
      }
      if (this.newPassword !== this.confirmPassword) {
        this.error = "A confirmação de senha não confere.";
        return;
      }
      this.loading = true;
      try {
        await changePassword(this.username, this.currentPassword, this.newPassword);
        this.success = "Senha alterada com sucesso!";
        this.currentPassword = this.newPassword = this.confirmPassword = '';
        setTimeout(() => {
          this.$emit('close');
        }, 1500);
      } catch (e) {
        // Corrigido para melhor mensagem de erro
        this.error = (e?.response?.data?.error || e?.response?.data?.detail) || "Erro ao alterar senha. Tente novamente.";
      } finally {
        this.loading = false;
      }
    },
    closeOnBackground(e) {
      if (e.target === this.$refs.modalBg) {
        this.$emit('close');
      }
    }
  }
};
</script>

<style scoped>
.modal-bg {
  position: fixed;
  z-index: 1200;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  padding: 32px 24px 20px 24px;
  border-radius: 10px;
  min-width: 340px;
  max-width: 95vw;
  box-shadow: 0 8px 32px #0002;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-content h3 {
  margin: 0 0 10px 0;
  font-size: 1.2rem;
  color: #12366e;
  text-align: center;
}

.modal-content form {
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.modal-content input {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1.5px solid #e6e8f0;
  background: #fafbfc;
  font-size: 1rem;
  color: #26334d;
  outline: none;
  transition: border-color 0.18s;
}

.modal-content input:focus {
  border-color: #0075ff;
}

.modal-message.error {
  color: #d92424;
  background: #fff6f6;
  border: 1px solid #fbcaca;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 0.97rem;
}

.modal-message.success {
  color: #267d12;
  background: #ecffe5;
  border: 1px solid #bffcc2;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 0.97rem;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 7px;
  justify-content: flex-end;
}

.modal-actions button {
  padding: 7px 16px;
  border-radius: 4px;
  font-size: 0.97rem;
  border: none;
  cursor: pointer;
  background: #0075ff;
  color: #fff;
}

.modal-actions .cancel-btn {
  background: #e0e0e0;
  color: #333;
}

.modal-actions button:disabled {
  background: #e0e0e0;
  color: #aaa;
  cursor: not-allowed;
}
</style>