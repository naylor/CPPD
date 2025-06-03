<template>
  <div v-if="!isAuthenticated" class="auth-message">
    <p>Por favor, faça login para acessar as itemizações.</p>
  </div>
  <div v-if="isAuthenticated" class="padrao-form">
    <div class="header-actions">
      <h1>{{ isEditing ? "Editar Processo" : "Criar Novo Processo" }}</h1>
      <router-link to="/processo">
        <button class="btn-acoes back-btn">Voltar para a Lista</button>
      </router-link>
    </div>

    <form @submit.prevent="salvarProcesso" class="processo-form">
      <div class="form-group">
        <label for="nome">Nome do Processo:</label>
        <input v-model="processo.nome" type="text" id="nome" placeholder="Digite o nome do processo" required />
      </div>

      <div class="form-group">
        <label for="inicio">Início:</label>
        <input v-model="processo.inicio" type="datetime-local" id="inicio"
          placeholder="Selecione a data e hora de início" required />
      </div>

      <div class="form-group">
        <label for="fim">Término:</label>
        <input v-model="processo.fim" type="datetime-local" id="fim" placeholder="Selecione a data e hora de término"
          required />
      </div>

      <div class="form-group">
        <label for="pontos">Pontos:</label>
        <input v-model="processo.pontos" type="number" id="pontos" placeholder="Quantidade de pontos mínimos"
          required />
      </div>

      <div class="form-group">
        <label for="descricao">Descrição:</label>
        <textarea v-model="processo.descricao" id="descricao" placeholder="Descreva o processo" rows="4"></textarea>
      </div>

      <div class="form-group">
        <label for="observacao">Observações:</label>
        <textarea v-model="processo.observacao" id="observacao" placeholder="Adicione observações sobre o processo"
          rows="4"></textarea>
      </div>

      <button type="submit" class="btn-acoes submit-btn" :disabled="loading">
        {{ loading ? "Salvando..." : (isEditing ? "Atualizar" : "Criar") }}
      </button>
    </form>

    <Toast ref="toast" />

  </div>
</template>

<script>
import api from "@/services/api";
import Toast from "@/components/Toast.vue";

export default {
  inheritAttrs: false,
  components: {
    Toast,
  },
  data() {
    return {
      processo: {
        nome: '',
        inicio: '',
        fim: '',
        pontos: '',
        descricao: '',
        observacao: ''
      },
      isEditing: false,
      loading: false,
      showModal: false,
      isAuthenticated: !!localStorage.getItem('access_token')
    };
  },
  methods: {
    showToast(message, type = "info") {
      // Supondo que o componente Toast tenha um método show({ message, type })
      if (this.$refs.toast && typeof this.$refs.toast.show === "function") {
        this.$refs.toast.show({ message, type });
      }
    },
    async salvarProcesso() {
      this.loading = true;
      try {
        if (this.isEditing) {
          await api.put(`/processo/${this.$route.params.id}/`, this.processo);
        } else {
          await api.post("/processo/", this.processo);
        }
        this.showToast("Processo criado com sucesso!", "success");
        setTimeout(() => {
          this.$router.back();
        }, 3000);
      } catch (error) {
        console.error("Erro ao salvar o processo:", error);
      } finally {
        this.loading = false;
      }
    },
    async fetchProcesso() {
      if (this.isAuthenticated && this.$route.params.id) {
        this.isEditing = true;
        try {
          const response = await api.get(`/processo/${this.$route.params.id}/`);
          this.processo = response.data;
          ['inicio', 'fim'].forEach(campo => {
            this.processo[campo] = ajustarDataParaLocal(this.processo[campo]);
          });
        } catch (error) {
          console.error("Erro ao carregar os dados do processo:", error);
        }
      }
    }
  },
  mounted() {
    this.fetchProcesso();
  }
};

function ajustarDataParaLocal(dateString) {
  const utcDate = new Date(dateString);
  const localDate = new Date(utcDate.getTime() - utcDate.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 16);
}
</script>

<style scoped>
h1 {
  margin-bottom: 16px;
  font-size: 1.4rem;
  color: #12366e;
  letter-spacing: 1px;
  text-align: left;
  font-weight: 700;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 18px;
}

.padrao-form {
  max-width: 520px;
  margin: 42px auto 0 auto;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 5px #0001;
  padding: 32px 28px 26px 28px;
}

.processo-form .form-group {
  margin-bottom: 18px;
}

.form-group label {
  font-weight: 600;
  color: #1f3c74;
  display: block;
  margin-bottom: 6px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e6e8f0;
  border-radius: 4px;
  font-size: 1rem;
  background: #fafbfc;
  color: #26334d;
  transition: border-color 0.18s;
  box-sizing: border-box;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #0075ff;
  outline: none;
}

.loading-message {
  color: #888;
  font-size: 1rem;
  margin-bottom: 18px;
  text-align: center;
}

.btn-acoes {
  padding: 8px 22px;
  background: #0075ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  margin-right: 12px;
  margin-top: 8px;
  margin-bottom: 2px;
  transition: background 0.18s;
}

.btn-acoes:disabled {
  background: #8ec4fb;
  color: #f5f5f5;
  cursor: not-allowed;
}

.btn-acoes:last-child {
  margin-right: 0;
}

.btn-acoes:hover:not(:disabled) {
  background: #0050a4;
}

.submit-btn {
  background: #14b714;
}

.submit-btn:hover:not(:disabled) {
  background: #0e860e;
}

.back-btn {
  background: #d92424;
}

.back-btn:hover {
  background: #a50d0d;
}

.auth-message {
  color: #c00;
  background: #fff4f4;
  border: 1px solid #fbcaca;
  border-radius: 5px;
  padding: 32px 18px;
  text-align: center;
  width: 60vw;
  margin: 48px auto 0 auto;
  font-size: 1.07rem;
  font-weight: 500;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}


@media (max-width: 700px) {
  .padrao-form {
    padding: 18px 5vw 12px 5vw;
    max-width: 98vw;
  }

}
</style>