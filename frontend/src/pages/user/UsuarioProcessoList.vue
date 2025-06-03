<template>
  <div v-if="!isAuthenticated" class="auth-message">
    <p>Por favor, faça login para acessar os documentos enviados.</p>
  </div>
  <div v-else class="usuario-processos">
    <div class="header-actions">
      <h2>Meus Processos</h2>
    </div>
    <div v-if="usuarioProcessos && usuarioProcessos.length > 0" class="table-wrapper">
      <table class="usuario-processos-table">
        <thead>
          <tr>
            <th>Processo</th>
            <th>Pontos</th>
            <th>Data</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="up in usuarioProcessos" :key="up.id">
            <td>
              <span class="processo-nome" :title="up.processo_nome">{{ up.processo_nome }}</span>
            </td>
            <td class="pontos-col">
              <div class="progress-bar-outer">
                <div class="progress-bar-inner" :style="{ width: calcularPorcentagem(up) + '%' }"
                  :title="up.total_pontos + ' de ' + getTotalPontosProcesso(up) + ' pontos'"></div>
                <span class="progress-label">
                  {{ up.total_pontos }}/{{ getTotalPontosProcesso(up) }}
                </span>
              </div>
            </td>
            <td>
              <span class="processo-data">
                {{ formatDataProcesso(up.data) }}
              </span>
            </td>
            <td class="status-col">
              <a href="#" class="status-link" @click.prevent="abrirLog(up)">
                {{ up.status }}
              </a>
            </td>
            <td>
              <button v-if="up.status != 'Submetido' && up.status != 'Finalizado'" class="btn-acoes submit-btn"
                @click="abrirConfirmacao('submeter', up)">Submeter</button>
              <button v-if="up.status == 'Submetido'" class="btn-acoes" @click="baixarPdfProcesso(up)">Download</button>
              <button v-if="up.status != 'Submetido'" class="btn-acoes visualizar-btn"
                @click="getInscricao(up)">Documentos</button>
              <button v-if="up.status == 'Iniciado'" class="btn-acoes delete-btn"
                @click="abrirConfirmacao('excluir', up)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading" class="nenhum-processo">
      <p>Nenhum processo encontrado.</p>
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

    <!-- Modal de Confirmação para Submeter/Excluir -->
    <div v-if="modalConfirmacao.visivel" class="modal modal-log" @click.self="fecharModalConfirmacao">
      <div class="modal-content modal-content-log">
        <div class="modal-header">
          <h3>{{ modalConfirmacao.titulo }}</h3>
          <button class="modal-close" @click="fecharModalConfirmacao">&times;</button>
        </div>
        <hr class="section-divider" />
        <div>
          <p>{{ modalConfirmacao.mensagem }}</p>
        </div>
        <div class="modal-actions">
          <button class="btn-acoes salvar-btn" @click="confirmarAcao">{{ modalConfirmacao.textoConfirmar }}</button>
          <button class="btn-acoes cancelar-btn" @click="fecharModalConfirmacao">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Toast/Snackbar -->
    <div v-if="toast.show" :class="['custom-toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  data() {
    return {
      usuarioProcessos: [],
      loading: false,
      isAuthenticated: !!localStorage.getItem('access_token'),
      isModalLogOpen: false,
      logSelecionado: "",
      toast: {
        show: false,
        message: "",
        type: "info"
      },
      toastTimeout: null,
      // Modal de confirmação
      modalConfirmacao: {
        visivel: false,
        acao: '',
        usuarioProcesso: null,
        titulo: '',
        mensagem: '',
        textoConfirmar: ''
      }
    };
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
        const response = await api.get(`/usuario-processo/by-user/${localStorage.getItem('userId')}`);
        let data = [];
        if (Array.isArray(response.data.results)) {
          data = response.data.results;
        } else if (Array.isArray(response.data)) {
          data = response.data;
        } else {
          data = [];
        }
        data.sort((a, b) => {
          if (!a.data) return 1;
          if (!b.data) return -1;
          return b.data.localeCompare(a.data);
        });
        this.usuarioProcessos = data;
      } catch (error) {
        this.showToast("Erro ao carregar os processos.", "error");
      } finally {
        this.loading = false;
      }
    },
    formatDataProcesso(dataISO) {
      if (!dataISO || dataISO.length < 10) return "-";
      return dataISO.substring(8, 10) + "/" + dataISO.substring(5, 7) + "/" + dataISO.substring(0, 4);
    },
    abrirConfirmacao(acao, usuarioProcesso) {
      if (acao === 'submeter') {
        this.modalConfirmacao = {
          visivel: true,
          acao: 'submeter',
          usuarioProcesso,
          titulo: 'Submeter Processo',
          mensagem: 'Deseja submeter o processo? A operação não poderá ser desfeita.',
          textoConfirmar: 'Submeter'
        };
      } else if (acao === 'excluir') {
        this.modalConfirmacao = {
          visivel: true,
          acao: 'excluir',
          usuarioProcesso,
          titulo: 'Excluir Registro',
          mensagem: 'Tem certeza que deseja excluir o registro?',
          textoConfirmar: 'Excluir'
        };
      }
    },
    fecharModalConfirmacao() {
      this.modalConfirmacao = {
        visivel: false,
        acao: '',
        usuarioProcesso: null,
        titulo: '',
        mensagem: '',
        textoConfirmar: ''
      };
    },
    async confirmarAcao() {
      if (this.modalConfirmacao.acao === 'submeter') {
        await this.submeterProcesso(this.modalConfirmacao.usuarioProcesso.id, this.modalConfirmacao.usuarioProcesso.processo);
      } else if (this.modalConfirmacao.acao === 'excluir') {
        await this.deletarProcesso(this.modalConfirmacao.usuarioProcesso.id);
      }
      this.fecharModalConfirmacao();
    },
    async submeterProcesso(usuarioProcessoId, processoId) {
      const form = new FormData();
      form.append("usuario", localStorage.getItem("userId"));
      form.append("status", 'Submetido');
      form.append("processo", processoId);
      try {
        await api.put(`/usuario-processo/${usuarioProcessoId}/`, form);
        this.fetchUsuarioProcessos();
        this.showToast('Processo submetido com sucesso!', "success");
      } catch (error) {
        let erro = "Erro ao submeter o processo.";
        if (error.response && error.response.data && error.response.data.non_field_errors) {
          erro = error.response.data.non_field_errors[0];
        }
        this.showToast(erro, "error");
      }
    },
    baixarPdfProcesso(up) {
      if (up.link_processo_pdf) {
        window.open(up.link_processo_pdf, '_blank');
      } else {
        this.showToast('Link do PDF não disponível.', "error");
      }
    },
    async getInscricao(up) {
      localStorage.setItem("usuarioProcessoId", up.id);
      localStorage.setItem("processoId", up.processo);
      this.$router.push({ name: "DocsUsuarioProcessoUser" });
    },
    async deletarProcesso(usuarioProcessoId) {
      try {
        await api.delete(`/usuario-processo/${usuarioProcessoId}/`);
        this.fetchUsuarioProcessos();
        this.showToast("Registro excluído com sucesso.", "success");
      } catch (error) {
        this.showToast('Erro ao excluir o processo. Arquivos foram enviados.', "error");
      }
    },
    abrirLog(up) {
      this.logSelecionado = up.log || "";
      this.isModalLogOpen = true;
    },
    fecharLog() {
      this.isModalLogOpen = false;
      this.logSelecionado = "";
    },
    getTotalPontosProcesso(up) {
      if (up.processo_pontos != null) return up.processo_pontos;
      if (up.processo && up.processo.pontos != null) return up.processo.pontos;
      if (up.pontos_maximos != null) return up.pontos_maximos;
      return 0;
    },
    calcularPorcentagem(up) {
      const total = this.getTotalPontosProcesso(up);
      if (!total) return 0;
      return Math.round((up.total_pontos / total) * 100);
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      this.fetchUsuarioProcessos();
    }
  }
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

.pontos-col {
  width: 120px;
  min-width: 100px;
  max-width: 140px;
  text-align: left;
  padding-right: 0;
}

.progress-bar-outer {
  position: relative;
  height: 18px;
  width: 100px;
  background: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.progress-bar-inner {
  height: 100%;
  background: linear-gradient(90deg, #48c774, #2176ae);
  transition: width 0.4s;
}

.progress-label {
  position: absolute;
  width: 100%;
  text-align: center;
  font-size: 0.82em;
  color: #234;
  font-weight: 600;
  z-index: 2;
  pointer-events: none;
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

.submit-btn {
  background: #14b714;
}

.submit-btn:hover {
  background: #0e860e;
}

.delete-btn {
  background: #d92424;
}

.delete-btn:hover {
  background: #a50d0d;
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

/* Modal de log e confirmação */
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