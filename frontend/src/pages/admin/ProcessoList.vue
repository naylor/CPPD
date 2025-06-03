<template>
  <div>
    <!-- Mensagem de autenticação -->
    <div v-if="!isAuthenticated" class="auth-message">
      <p>Por favor, faça login para acessar os processos.</p>
    </div>

    <!-- Conteúdo principal -->
    <div v-if="isAuthenticated" class="padrao-list">
      <div class="header-actions">
        <h1>Lista de Processos</h1>
        <router-link to="/processo/novo">
          <button class="btn-acoes criar-btn">Criar Novo Processo</button>
        </router-link>
      </div>
      <div v-if="processos.length > 0" class="table-wrapper">
        <table class="usuario-processos-table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Início</th>
              <th>Término</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="processo in processos" :key="processo.id">
              <td>
                <span class="processo-nome" :title="processo.nome">{{ processo.nome }}</span>
              </td>
              <td>{{ formatDate(processo.inicio) }}</td>
              <td>{{ formatDate(processo.fim) }}</td>
              <td>
                <div class="actions-container">
                  <router-link :to="{ name: 'ItemizacaoTarefaTree', params: { processoId: processo.id } }">
                    <button class="btn-acoes itemizacao-btn" title="Itemizações">
                      <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" fill="none" viewBox="0 0 24 24">
                        <path d="M7 6V4a1 1 0 011-1h8a1 1 0 011 1v2" stroke="#fff" stroke-width="2" />
                        <rect x="2" y="6" width="20" height="14" rx="2" fill="#fff" stroke="#ffa600" stroke-width="2" />
                        <path d="M7 10h10M7 14h6" stroke="#ffa600" stroke-width="2" stroke-linecap="round" />
                      </svg>
                    </button>
                  </router-link>
                  <router-link :to="{ name: 'EditarProcesso', params: { id: processo.id } }">
                    <button class="btn-acoes icon-btn edit-btn" title="Editar">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                        <path d="M16.862 5.487a2.07 2.07 0 0 1 2.933 2.933L9.6 18.615 5 19l.385-4.6L16.862 5.487Z" />
                      </svg>
                    </button>
                  </router-link>
                  <button class="btn-acoes icon-btn delete-btn" title="Excluir" @click="abrirModalExcluir(processo.id)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" stroke="currentColor"
                      stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m5 0V4a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v2" />
                      <line x1="10" y1="11" x2="10" y2="17" />
                      <line x1="14" y1="11" x2="14" y2="17" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="nenhum-processo">
        <p>Nenhum processo encontrado.</p>
      </div>
    </div>

    <!-- Modal de confirmação -->
    <div v-if="showConfirmModal" class="modal modal-log" @click.self="fecharModalExcluir">
      <div class="modal-content modal-content-log">
        <div class="modal-header">
          <h3>Confirmação</h3>
          <button class="modal-close" @click="fecharModalExcluir">&times;</button>
        </div>
        <hr class="section-divider" />
        <div>
          <p>Tem certeza que deseja excluir esse registro?</p>
        </div>
        <div class="modal-actions">
          <button class="btn-acoes salvar-btn" @click="confirmarExcluirProcesso">
            Excluir
          </button>
          <button class="btn-acoes cancelar-btn" @click="fecharModalExcluir">
            Cancelar
          </button>
        </div>
      </div>
    </div>

    <Toast ref="toast" />
  </div>
</template>

<script>
import api from "@/services/api";
import Toast from "@/components/Toast.vue";

export default {
  components: {
    Toast,
  },
  data() {
    return {
      processos: [],
      isAuthenticated: !!localStorage.getItem('access_token'),
      showConfirmModal: false,
      processoParaExcluir: null
    };
  },

  methods: {
    async fetchProcessos() {
      try {
        const response = await api.get("/processo/");
        let lista = Array.isArray(response.data.results)
          ? response.data.results.filter(p => p && p.id)
          : [];
        lista.sort((a, b) => {
          const dataA = a.inicio ? new Date(a.inicio) : (a.fim ? new Date(a.fim) : new Date(0));
          const dataB = b.inicio ? new Date(b.inicio) : (b.fim ? new Date(b.fim) : new Date(0));
          return dataB - dataA;
        });
        this.processos = lista;
      } catch (error) {
        this.showToast("Erro ao carregar os processos.", "error");
        console.error("Erro ao carregar os processos:", error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return "-";
      const date = new Date(dateString);
      if (date instanceof Date && !isNaN(date)) {
        return `${date.toLocaleDateString("pt-BR")} ${date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
      }
      return "-";
    },
    abrirModalExcluir(id) {
      this.processoParaExcluir = id;
      this.showConfirmModal = true;
    },
    fecharModalExcluir() {
      this.showConfirmModal = false;
      this.processoParaExcluir = null;
    },
    async confirmarExcluirProcesso() {
      try {
        await api.delete(`/processo/${this.processoParaExcluir}/`);
        this.showToast("Processo excluído com sucesso!", "success");
        this.fetchProcessos();
      } catch (error) {
        let mensagem = "Erro ao excluir o registro.";
        if (
          error.response &&
          error.response.data &&
          typeof error.response.data === "string" &&
          error.response.data.includes("because they are referenced through restricted foreign keys")
        ) {
          mensagem =
            "Não é possível excluir este processo pois ele está vinculado a itemizações, tarefas e/ou processos de usuários. Remova primeiro esses vínculos antes de tentar excluir.";
        }
        this.showToast(mensagem, "error");
        console.error("Erro ao excluir o documento:", error);
      }
      this.fecharModalExcluir();
    },
    showToast(message, type = "info") {
      // Supondo que o componente Toast tenha um método show({ message, type })
      if (this.$refs.toast && typeof this.$refs.toast.show === "function") {
        this.$refs.toast.show({ message, type });
      }
    },
  },
  mounted() {
    if (this.isAuthenticated) {
      this.fetchProcessos();
    }
  }
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 3000;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.45);
  /* Escurecimento do fundo */
  display: flex;
  align-items: center;
  /* Centraliza verticalmente */
  justify-content: center;
  /* Centraliza horizontalmente */
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px #0007;
  padding: 24px 24px 18px 24px;
  min-width: 280px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.6rem;
  color: #888;
  cursor: pointer;
  margin-left: 12px;
  padding: 0;
}

.modal-close:hover {
  color: #c00;
}

.modal-actions {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  /* ou center, se preferir */
  gap: 12px;
  /* ajusta o espaço entre os botões */
  margin-top: 12px;
}

h1 {
  margin-bottom: 16px;
  font-size: 1.4rem;
  color: #12366e;
  letter-spacing: 1px;
  text-align: left;
  font-weight: 700;
}

.padrao-list {
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 5px #0001;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  gap: 22px;
}

.nenhum-processo {
  color: #888;
  font-size: 1rem;
  padding: 20px;
  text-align: center;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 12px;
}

.usuario-processos-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 5px #0001;
  font-size: 0.92rem;
  table-layout: fixed;
}

.usuario-processos-table th,
.usuario-processos-table td {
  padding: 8px 7px;
  border-bottom: 1px solid #e6e8f0;
  text-align: left;
  vertical-align: middle;
}

.usuario-processos-table th {
  background: #f5f7fa;
  color: #1f3c74;
  font-weight: 600;
  font-size: 0.97rem;
}

.usuario-processos-table tr:last-child td {
  border-bottom: none;
}

.processo-nome {
  display: inline-block;
  max-width: 210px;
  white-space: wrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
}

.actions-container {
  display: flex;
  gap: 8px;
}

.btn-acoes {
  padding: 6px 14px;
  background: #0075ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.18s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-acoes:last-child {
  margin-right: 0;
}

.btn-acoes:hover {
  background: #0050a4;
}

.criar-btn {
  background: #14b714;
}

.criar-btn:hover {
  background: #0e860e;
}

.icon-btn {
  min-width: 36px;
  min-height: 36px;
  padding: 0;
  background: none;
}

.edit-btn {
  color: #0075ff;
  background: none;
}

.edit-btn:hover {
  color: #0050a4;
  background: #e8f1ff;
}

.delete-btn {
  color: #d92424;
  background: none;
}

.delete-btn:hover {
  color: #fff;
  background: #d92424;
}

.itemizacao-btn {
  background: #ffa600;
  color: #fff;
}

.itemizacao-btn:hover {
  background: #c77c00;
  color: #fff;
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

@media (max-width: 900px) {
  .padrao-list {
    padding: 16px 2vw 16px 2vw;
  }

  .auth-message {
    width: 98vw;
    margin: 24px auto 0 auto;
  }

  .processo-nome {
    max-width: 120px;
  }
}
</style>