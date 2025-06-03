<template>
  <div class="processos">
    <h2>Processos Disponíveis</h2>
    <div v-if="processos.length === 0" class="nenhum-processo">
      Nenhum processo disponível no momento.
    </div>
    <ul class="processos-lista">
      <li v-for="processo in processos" :key="processo.id" class="processo-card">
        <div class="processo-infos">
          <a href="#" class="processo-titulo-link" @click.prevent="openModal(processo)">{{ processo.nome }}</a>
          <div class="processo-dados">
            <span>
              <strong>Início:</strong>
              {{ formatDate(processo.inicio) }}
            </span>
            <span>
              <strong>Encerramento:</strong>
              {{ formatDate(processo.fim) }}
            </span>
            <span>
              <strong>Pontuação necessária:</strong>
              {{ processo.pontos }}
            </span>
          </div>
        </div>
        <div class="processo-acoes">
          <button class="btn-inscricao" v-if="canInscrever(processo)" @click="abrirModalConfirmacao(processo)">
            Inscrever-se
          </button>
          <span v-else class="processo-encerrado">Encerrado</span>
        </div>
      </li>
    </ul>

    <!-- Modal detalhes processo -->
    <div v-if="modalAberto" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <span class="modal-close" @click="closeModal">&times;</span>
        <h3 class="modal-titulo">{{ processoModal.nome }}</h3>
        <div class="modal-section">
          <strong>Descrição:</strong>
          <div>{{ processoModal.descricao || 'Não informado.' }}</div>
        </div>
        <div class="modal-section">
          <strong>Observação:</strong>
          <div>{{ processoModal.observacao || 'Não informado.' }}</div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmação inscrição -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="fecharModalConfirmacao">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirmação</h3>
          <button class="modal-close" @click="fecharModalConfirmacao">&times;</button>
        </div>
        <hr class="section-divider" />
        <div>
          <p>Deseja iniciar o processo de inscrição para <b>"{{ processoParaInscricao?.nome }}"</b>?</p>
        </div>
        <div class="modal-actions">
          <button class="btn-acoes salvar-btn" @click="confirmarInscricao">Inscrever-se</button>
          <button class="btn-acoes cancelar-btn" @click="fecharModalConfirmacao">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Dialog personalizado para sucesso -->
    <div v-if="dialogSucesso" class="custom-success-dialog">
      <div class="custom-success-content">
        <div class="custom-success-message">
          Inscrição iniciada com sucesso!
        </div>
        <button class="btn-preencher" @click="irParaDocs">
          Preencher Documentos
        </button>
        <span class="custom-success-close" @click="dialogSucesso = false">&times;</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  data() {
    return {
      processos: [],
      now: new Date(),
      modalAberto: false,
      processoModal: {},
      dialogSucesso: false,
      usuarioProcessoId: null,
      processoId: null,
      showConfirmModal: false,
      processoParaInscricao: null,
    };
  },
  created() {
    this.fetchProcessos();
  },
  methods: {
    async fetchProcessos() {
      try {
        const response = await api.get("/processo/");
        const results = Array.isArray(response.data.results)
          ? response.data.results
          : [];
        // Ordena por data de encerramento (fim) DESC, depois por início DESC se fim for igual
        results.sort((a, b) => {
          const dateA = a.fim ? new Date(a.fim) : new Date(0);
          const dateB = b.fim ? new Date(b.fim) : new Date(0);
          if (dateA.getTime() === dateB.getTime()) {
            // desempate por início
            const iniA = a.inicio ? new Date(a.inicio) : new Date(0);
            const iniB = b.inicio ? new Date(b.inicio) : new Date(0);
            return iniB - iniA;
          }
          return dateB - dateA;
        });
        this.processos = results;
      } catch (error) {
        alert("Erro ao carregar os processos.");
      }
    },
    abrirModalConfirmacao(processo) {
      this.processoParaInscricao = processo;
      this.showConfirmModal = true;
    },
    fecharModalConfirmacao() {
      this.showConfirmModal = false;
      this.processoParaInscricao = null;
    },
    async confirmarInscricao() {
      await this.submitProcess(this.processoParaInscricao);
      this.fecharModalConfirmacao();
    },
    async submitProcess(processo) {
      try {
        const usuarioId = localStorage.getItem("userId");
        const data = {
          usuario: usuarioId,
          processo: processo.id,
          status: "Iniciado",
          submetido: 0,
        };
        const response = await api.post("/usuario-processo/", data);
        const usuarioProcessoId = response.data.id;

        localStorage.setItem("usuarioProcessoId", usuarioProcessoId);
        localStorage.setItem("processoId", processo.id);

        // Exibe o dialog de sucesso com botão
        this.usuarioProcessoId = usuarioProcessoId;
        this.processoId = processo.id;
        this.dialogSucesso = true;
      } catch (error) {
        alert("Ocorreu um erro ao tentar iniciar o processo.");
      }
    },
    irParaDocs() {
      this.dialogSucesso = false;
      this.$router.push({ name: "DocsUsuarioProcessoUser" });
    },
    formatDate(dateString) {
      if (!dateString) return "-";
      const d = new Date(dateString);
      return d.toLocaleDateString("pt-BR");
    },
    canInscrever(processo) {
      if (!processo.fim) return true;
      const encerramento = new Date(processo.fim);
      encerramento.setHours(23, 59, 59, 999);
      return this.now <= encerramento;
    },
    openModal(processo) {
      this.processoModal = processo;
      this.modalAberto = true;
    },
    closeModal() {
      this.modalAberto = false;
      this.processoModal = {};
    },
  },
};
</script>

<style scoped>
.processos {
  width: 60vw;
  max-width: 80vw;
  min-width: 600px;
  margin: 32px auto;
  padding: 2px;
  background: #f9f9fc;
  border-radius: 5px;
  box-shadow: 0 2px 12px #00000022;
  font-size: 0.94rem;
}

h2 {
  margin-bottom: 16px;
  font-size: 1.2rem;
  color: #12366e;
  letter-spacing: 1px;
  text-align: left;
  font-weight: 700;
}

.nenhum-processo {
  color: #888;
  font-size: 1rem;
  padding: 20px;
  text-align: center;
}

.processos-lista {
  list-style-type: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

.processo-card {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  background: #fff;
  border: 1px solid #e6e8f0;
  padding: 18px 28px;
  transition: box-shadow 0.2s;
  box-shadow: 0 2px 5px #0001;
  font-size: 0.80rem;
  width: 100%;
}

.processo-card:hover {
  box-shadow: 0 4px 16px #0055a444;
  border-color: #bcd3ff;
}

.processo-infos {
  flex: 1 1 0;
  min-width: 0;
}

.processo-titulo-link {
  font-size: 0.90rem;
  font-weight: 600;
  color: #1f3c74;
  word-break: break-word;
  text-decoration: underline;
  cursor: pointer;
  background: none;
  border: none;
  outline: none;
  padding: 0;
}

.processo-titulo-link:hover,
.processo-titulo-link:focus {
  color: #0050a4;
  text-decoration: underline;
}

.processo-dados {
  display: flex;
  gap: 22px;
  font-size: 0.80rem;
  color: #2a4264;
  flex-wrap: wrap;
}

.processo-dados span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.processo-acoes {
  margin-left: 14px;
  /* distância reduzida */
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 120px;
  justify-content: center;
}

.btn-inscricao {
  padding: 8px 22px;
  background: #0075ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.97rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s;
}

.btn-inscricao:hover {
  background: #0050a4;
}

.processo-encerrado {
  color: #c00;
  font-weight: bold;
  font-size: 0.99rem;
  margin-top: 10px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 3000;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  max-width: 450px;
  width: 90vw;
  padding: 24px 28px 18px 28px;
  box-shadow: 0 10px 32px #0004;
  position: relative;
  animation: modalOpen 0.22s;
}

@keyframes modalOpen {
  from {
    transform: translateY(-40px) scale(0.98);
    opacity: 0.3;
  }

  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.modal-close {
  position: absolute;
  right: 17px;
  top: 10px;
  font-size: 1.5rem;
  color: #888;
  cursor: pointer;
  font-weight: bold;
  transition: color 0.14s;
  z-index: 10;
  background: none;
  border: none;
  line-height: 1;
}

.modal-close:hover {
  color: #c00;
}

.modal-titulo {
  font-size: 1.12rem;
  font-weight: 600;
  color: #112a54;
  margin-bottom: 12px;
  text-align: left;
  word-break: break-word;
}

.modal-section {
  margin-bottom: 13px;
  font-size: 0.98rem;
  color: #223366;
}

.modal-actions {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 18px;
}

.btn-acoes {
  padding: 7px 18px;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background 0.18s;
}

.salvar-btn {
  background: #1976d2;
  color: #fff;
}

.salvar-btn:hover {
  background: #1251a1;
}

.cancelar-btn {
  background: #e0e0e0;
  color: #444;
}

.cancelar-btn:hover {
  background: #bdbdbd;
  color: #222;
}

/* Custom Success Dialog */
.custom-success-dialog {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 3000;
  width: 100vw;
  height: 100vh;
  background: #0006;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-success-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 32px #0004;
  padding: 28px 38px 22px 38px;
  max-width: 350px;
  width: 90vw;
  position: relative;
  text-align: center;
  animation: modalOpen 0.2s;
}

.custom-success-message {
  font-size: 1.06rem;
  color: #197c12;
  font-weight: 600;
  margin-bottom: 22px;
}

.btn-preencher {
  padding: 9px 28px;
  background: #0075ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.03rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s;
}

.btn-preencher:hover {
  background: #0050a4;
}

.custom-success-close {
  position: absolute;
  right: 15px;
  top: 8px;
  font-size: 1.25rem;
  color: #aaa;
  cursor: pointer;
  font-weight: bold;
  transition: color 0.14s;
}

.custom-success-close:hover {
  color: #c00;
}
</style>