<template>
  <div v-if="!isAuthenticated" class="auth-message">
    <p>Por favor, faça login para acessar os documentos enviados pelos usuários.</p>
  </div>
  <div v-if="isAuthenticated" class="usuario-processos">
    <div class="header-actions">
      <h2>Processos dos Usuários</h2>
    </div>

    <div v-if="usuarioProcessos.length" class="table-wrapper">
      <table class="usuario-processos-table">
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Processo</th>
            <th>Data</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="usuarioProcesso in usuarioProcessos" :key="usuarioProcesso.id">
            <td>
              <span class="processo-nome" :title="usuarioProcesso.usuario_nome || usuarioProcesso.usuario">
                {{ usuarioProcesso.usuario_nome || usuarioProcesso.usuario }}
              </span>
            </td>
            <td>
              <span class="processo-nome" :title="usuarioProcesso.processo_nome || usuarioProcesso.processo">
                {{ usuarioProcesso.processo_nome || usuarioProcesso.processo }}
              </span>
            </td>
            <td>
              <span class="processo-data">
                {{ formatarDataUTC(usuarioProcesso.data) }}
              </span>
            </td>
            <td class="status-col">
              <a href="#" class="status-link" @click.prevent="abrirLog(usuarioProcesso)">
                {{ usuarioProcesso.status }}
              </a>
            </td>
            <td>
              <button class="btn-acoes visualizar-btn" @click="listarDocumentos(usuarioProcesso.id)">
                Documentos
              </button>
              <button class="btn-acoes alterar-btn" @click="abrirAlterarStatus(usuarioProcesso)"
                :disabled="usuarioProcesso.status === 'Iniciado' || usuarioProcesso.status === 'Devolvido'">
                Alterar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!usuarioProcessos.length && !loading" class="nenhum-processo">
      <p>Nenhum usuário encontrado.</p>
    </div>

    <!-- Paginação Numérica -->
    <div v-if="totalPages > 1" class="pagination-numeric">
      <button class="btn-acoes pag-btn" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
        &laquo;
      </button>
      <button v-for="page in visiblePages" :key="page" class="btn-acoes pag-btn page-number"
        :class="{ active: currentPage === page }" @click="changePage(page)" :disabled="currentPage === page">
        {{ page }}
      </button>
      <button class="btn-acoes pag-btn" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
        &raquo;
      </button>
    </div>
  </div>

  <!-- Modal de Alteração de Status -->
  <div v-if="isModalAlterarStatusOpen" class="modal modal-alterar-status" @click.self="fecharAlterarStatus">
    <div class="modal-content modal-content-alterar">
      <div class="modal-header">
        <h3>Alterar Status do Processo</h3>
        <button class="modal-close" @click="fecharAlterarStatus">&times;</button>
      </div>
      <hr class="section-divider" />
      <div>
        <label>Status:</label>
        <select v-model="statusSelecionado" required>
          <option disabled value="">Selecione...</option>
          <option value="Devolvido">Devolvido</option>
          <option value="Finalizado">Finalizado</option>
        </select>
      </div>
      <div>
        <label>Observação:</label>
        <textarea v-model="observacao" rows="3" placeholder="Observação (obrigatório)" required></textarea>
      </div>
      <div class="modal-actions">
        <button class="btn-acoes salvar-btn" @click="salvarAlteracaoStatus">Salvar</button>
        <button class="btn-acoes cancelar-btn" @click="fecharAlterarStatus">Cancelar</button>
      </div>
    </div>
  </div>

  <!-- Modal de Log -->
  <div v-if="isModalLogOpen" class="modal modal-log" @click.self="fecharLog">
    <div class="modal-content modal-content-log">
      <div class="modal-header">
        <h3>Histórico de Logs</h3>
        <button class="modal-close" @click="fecharLog">&times;</button>
      </div>
      <hr class="section-divider" />
      <div class="log-content">
        <pre v-if="logSelecionado && logSelecionado.trim() !== ''">{{ logSelecionado }}</pre>
        <p v-else>Nenhum log registrado.</p>
      </div>
      <div class="modal-actions">
        <button class="btn-acoes cancelar-btn" @click="fecharLog">Fechar</button>
      </div>
    </div>
  </div>

  <!-- Snackbar/Toast -->
  <div v-if="toast.show" :class="['custom-toast', toast.type]">
    {{ toast.message }}
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  data() {
    return {
      usuarioProcessos: [],
      currentPage: 1,
      totalPages: 1,
      pageSize: 10,
      loading: false,
      isAuthenticated: !!localStorage.getItem("access_token"),

      isModalAlterarStatusOpen: false,
      usuarioProcessoSelecionado: null,
      statusSelecionado: "",
      observacao: "",

      isModalLogOpen: false,
      logSelecionado: "",

      toast: {
        show: false,
        message: "",
        type: "info",
      },
      toastTimeout: null
    };
  },
  computed: {
    visiblePages() {
      const pages = [];
      let start = Math.max(1, this.currentPage - 2);
      let end = Math.min(this.totalPages, this.currentPage + 2);

      if (this.currentPage <= 3) {
        end = Math.min(this.totalPages, 5);
        start = 1;
      }
      if (this.currentPage >= this.totalPages - 2) {
        start = Math.max(1, this.totalPages - 4);
        end = this.totalPages;
      }
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    showToast(msg, type = "info", timeout = 3500) {
      this.toast.message = msg;
      this.toast.type = type;
      this.toast.show = true;
      if (this.toastTimeout) clearTimeout(this.toastTimeout);
      this.toastTimeout = setTimeout(() => {
        this.toast.show = false;
      }, timeout);
    },
    async fetchUsuarioProcessos() {
      this.loading = true;
      try {
        const response = await api.get(`/usuario-processo`, {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
            ordering: "-data", // Ordena por data decrescente
          },
        });
        let data = Array.isArray(response.data.results)
          ? response.data.results
          : response.data;
        // Garantir ordenação por data UTC decrescente no front também:
        data.sort((a, b) => {
          if (!a.data) return 1;
          if (!b.data) return -1;
          return b.data.localeCompare(a.data); // ISO string, desc
        });
        this.usuarioProcessos = data;
        this.totalPages = response.data.count
          ? Math.ceil(response.data.count / this.pageSize)
          : 1;
      } catch (error) {
        this.showToast("Erro ao carregar os usuários e processos.", "error");
        console.error("Erro ao carregar os usuários e processos:", error);
      } finally {
        this.loading = false;
      }
    },
    changePage(page) {
      if (page > 0 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        this.fetchUsuarioProcessos();
      }
    },
    // Exibir data UTC do JSON (sem conversão local)
    formatarDataUTC(dataISO) {
      if (!dataISO || dataISO.length < 10) return "";
      return dataISO.substring(8, 10) + "/" + dataISO.substring(5, 7) + "/" + dataISO.substring(0, 4);
    },
    async listarDocumentos(id) {
      localStorage.setItem("usuarioProcessoId", id);
      this.$router.push({ name: "DocsUsuarioProcesso" });
    },
    abrirAlterarStatus(usuarioProcesso) {
      this.usuarioProcessoSelecionado = usuarioProcesso;
      this.statusSelecionado = usuarioProcesso.status || "";
      this.observacao = "";
      this.isModalAlterarStatusOpen = true;
    },
    fecharAlterarStatus() {
      this.usuarioProcessoSelecionado = null;
      this.statusSelecionado = "";
      this.observacao = "";
      this.isModalAlterarStatusOpen = false;
    },
    async salvarAlteracaoStatus() {
      if (!this.statusSelecionado || !this.observacao.trim()) {
        this.showToast("Selecione o status e insira a observação.", "error");
        return;
      }
      try {
        const now = new Date();
        const timestamp =
          now.getFullYear() +
          "-" +
          String(now.getMonth() + 1).padStart(2, "0") +
          "-" +
          String(now.getDate()).padStart(2, "0") +
          " " +
          String(now.getHours()).padStart(2, "0") +
          ":" +
          String(now.getMinutes()).padStart(2, "0") +
          ":" +
          String(now.getSeconds()).padStart(2, "0");

        const logEntry = `[${timestamp}] ${this.observacao}`;

        await api.patch(
          `/usuario-processo/${this.usuarioProcessoSelecionado.id}/`,
          {
            status: this.statusSelecionado,
            log: logEntry,
          }
        );
        this.fecharAlterarStatus();
        this.fetchUsuarioProcessos();
        this.showToast("Status alterado com sucesso!", "success");
      } catch (error) {
        this.showToast("Erro ao alterar status do processo.", "error");
        console.error("Erro ao alterar status:", error);
      }
    },
    abrirLog(usuarioProcesso) {
      this.logSelecionado = usuarioProcesso.log || "";
      this.isModalLogOpen = true;
    },
    fecharLog() {
      this.isModalLogOpen = false;
      this.logSelecionado = "";
    },
  },
  mounted() {
    if (this.isAuthenticated) {
      this.fetchUsuarioProcessos();
    }
  },
};
</script>

<style scoped>
h2 {
  margin-bottom: 16px;
  font-size: 1.25rem;
  color: #12366e;
  letter-spacing: 1px;
  text-align: left;
  font-weight: 700;
}

.usuario-processos {
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
  font-size: 0.90rem;
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
  font-size: 0.94rem;
}

.usuario-processos-table tr:last-child td {
  border-bottom: none;
}

.processo-nome {
  display: inline-block;
  max-width: 200px;
  white-space: wrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
}

.processo-data {
  font-family: monospace;
  color: #1a355c;
  font-size: 0.96em;
  white-space: nowrap;
}

.status-col {
  width: 72px;
  min-width: 50px;
  max-width: 90px;
  text-align: left;
  padding-left: 0;
}

.status-link {
  color: #0075ff;
  text-decoration: underline;
  cursor: pointer;
  font-weight: 600;
  font-size: 1em;
}

.status-link:hover {
  color: #003a74;
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
  margin-right: 8px;
  transition: background 0.18s;
}

.btn-acoes:last-child {
  margin-right: 0;
}

.btn-acoes:hover {
  background: #0050a4;
}

.btn-acoes:disabled,
.btn-acoes[disabled] {
  background: #e0e0e0 !important;
  color: #aaa !important;
  cursor: not-allowed;
}

.visualizar-btn {
  background: #14b714;
}

.visualizar-btn:hover {
  background: #0e860e;
}

.alterar-btn {
  background: #ffb300;
  color: #222;
}

.alterar-btn:hover {
  background: #c28700;
  color: #fff;
}

.salvar-btn {
  background: #14b714;
}

.salvar-btn:hover {
  background: #0e860e;
}

.cancelar-btn {
  background: #e0e0e0;
  color: #444;
}

.cancelar-btn:hover {
  background: #bdbdbd;
  color: #222;
}

.pag-btn {
  background: #555dad;
  font-size: 0.96rem;
}

.pag-btn:disabled {
  background: #e0e0e0;
  color: #aaa;
  cursor: not-allowed;
}

.pag-btn:hover:enabled {
  background: #373989;
}

/* Paginação numérica */
.pagination-numeric {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-end;
  margin: 18px 0 10px 0;
  font-size: 1.03rem;
}

.page-number.active,
.page-number:disabled {
  background: #1976d2;
  color: #fff !important;
  font-weight: bold;
  cursor: default;
}

.nenhum-processo {
  color: #888;
  font-size: 1rem;
  padding: 20px;
  text-align: center;
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

/* Modal de alteração de status */
.modal.modal-alterar-status,
.modal.modal-log {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 30000;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.38);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content.modal-content-alterar,
.modal-content.modal-content-log {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px #0004;
  padding: 24px 28px 18px 28px;
  min-width: 340px;
  max-width: 98vw;
  min-height: 0;
  max-height: 92vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.modal-content-alterar label,
.modal-content-log label {
  font-weight: 500;
  margin-bottom: 5px;
  display: block;
}

.modal-content-alterar select,
.modal-content-alterar textarea {
  width: 100%;
  padding: 7px 10px;
  border-radius: 5px;
  border: 1px solid #e6e8f0;
  background: #f7f9fc;
  margin-bottom: 7px;
  font-size: 1rem;
  color: #222;
  resize: none;
}

.modal-content-alterar textarea {
  min-height: 60px;
  max-height: 120px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.modal-header h3 {
  font-size: 1.18rem;
  margin: 0;
  font-weight: bold;
  color: #222;
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
  gap: 16px;
  justify-content: flex-end;
  margin-top: 10px;
}

.section-divider {
  border: none;
  border-top: 1px solid #eee;
}

.log-content pre {
  background: #f4f4f4;
  padding: 10px;
  border-radius: 4px;
  color: #222;
  font-size: 0.97em;
  white-space: pre-wrap;
  max-height: 240px;
  overflow-y: auto;
}

/* Toast/Snackbar styles */
.custom-toast {
  position: fixed;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 220px;
  max-width: 380px;
  background: #323232;
  color: #fff;
  border-radius: 6px;
  padding: 14px 24px;
  font-size: 1.04em;
  box-shadow: 0 2px 8px #0002;
  z-index: 99999;
  text-align: center;
  opacity: 0.93;
  transition: opacity 0.2s;
  pointer-events: none;
}

.custom-toast.success {
  background: #16a34a;
  color: #fff;
}

.custom-toast.error {
  background: #d32f2f;
  color: #fff;
}

.custom-toast.info {
  background: #1976d2;
  color: #fff;
}
</style>