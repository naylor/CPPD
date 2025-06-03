<template>
    <div v-if="isAuthenticated" class="padrao-list">
        <div v-for="processo in processos" :key="processo.id">
            <div class="accordion-item">
                <div class="accordion-header" @click="toggleAccordion(processo.id)">
                    <div class="processo-header-flex">
                        <h3 class="processo-title">
                            {{ processo.nome }}
                            <span v-if="pontosPorItem[processo.id] !== undefined" class="pontos-info">
                                | Pontuação do usuário: {{ pontosPorItem[processo.id] }}
                                / Pontuação necessária: {{ processo.pontos }}
                            </span>
                        </h3>
                        <span v-if="processo.link_processo_pdf" class="pdf-link-right">
                            <button class="btn-back-processo" @click.stop="voltarParaTelaAnterior">
                                Voltar
                            </button>
                            <button class="btn-download-processo"
                                @click.stop="openDocumento(processo.link_processo_pdf)">
                                Download
                            </button>
                        </span>
                    </div>
                </div>
                <div class="accordion-content" v-show="isOpen(processo.id)">
                    <div v-for="itemizacao in processo.itemizacoes" :key="itemizacao.id" class="accordion-item">
                        <div class="accordion-header" @click="toggleAccordion(itemizacao.id)">
                            <h4 class="itemizacao-title">
                                {{ itemizacao.nome }}
                                <span v-if="pontosPorItem[itemizacao.id] !== undefined" class="pontos-info">
                                    | {{ pontosPorItem[itemizacao.id] }}
                                </span>
                            </h4>
                        </div>
                        <div class="accordion-content" v-show="isOpen(itemizacao.id)">
                            <div v-for="subitem in itemizacao.subitemizacoes" :key="subitem.id" class="accordion-item">
                                <div class="accordion-header" @click="toggleAccordion(subitem.id)">
                                    <h5 class="subitem-title">
                                        {{ subitem.nome }}
                                        <span v-if="pontosPorItem[subitem.id] !== undefined" class="pontos-info">
                                            | {{ pontosPorItem[subitem.id] }}
                                        </span>
                                    </h5>
                                </div>
                                <div class="accordion-content" v-show="isOpen(subitem.id)">
                                    <!-- SubSubItemizações -->
                                    <div v-for="subsubitem in subitem.subitemizacoes" :key="subsubitem.id"
                                        class="accordion-item">
                                        <div class="accordion-header" @click="toggleAccordion(subsubitem.id)">
                                            <h6 class="subsubitem-title">
                                                {{ subsubitem.nome }}
                                                <span v-if="pontosPorItem[subsubitem.id] !== undefined"
                                                    class="pontos-info">
                                                    | {{ pontosPorItem[subsubitem.id] }}
                                                </span>
                                            </h6>
                                        </div>
                                        <div class="accordion-content" v-show="isOpen(subsubitem.id)">
                                            <ul v-if="subsubitem.tarefas && subsubitem.tarefas.length">
                                                <li v-for="tarefa in subsubitem.tarefas" :key="tarefa.id">
                                                    <div class="tarefa">
                                                        <div @click.stop="openTarefa(tarefa)">
                                                            {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                                        </div>
                                                        <ul v-if="tarefa.documentos && tarefa.documentos.length">
                                                            <li v-for="doc in tarefa.documentos" :key="doc.id"
                                                                style="margin-left: 10px;">
                                                                <a class="doc-filename"
                                                                    :class="{ reajustada: doc.qdeReajustada !== null && doc.qdeReajustada !== undefined }"
                                                                    @click.prevent="openDocumento(doc.file)" href="#">
                                                                    {{ formatFilename(doc.filename, true) }}
                                                                </a>
                                                                <span class="document-quantity">
                                                                    Qtd: {{ doc.qdeReajustada != null ?
                                                                        doc.qdeReajustada : doc.quantidade }}
                                                                    <a href="#" class="reajustar-link"
                                                                        @click.prevent="openReajusteModal(doc, processo)">
                                                                        reajustar
                                                                    </a>
                                                                </span>
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    <!-- Tarefas de subitem -->
                                    <ul v-if="subitem.tarefas && subitem.tarefas.length">
                                        <li v-for="tarefa in subitem.tarefas" :key="tarefa.id">
                                            <div class="tarefa">
                                                <div @click.stop="openTarefa(tarefa)">
                                                    {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                                </div>
                                                <ul v-if="tarefa.documentos && tarefa.documentos.length">
                                                    <li v-for="doc in tarefa.documentos" :key="doc.id"
                                                        style="margin-left: 10px;">
                                                        <a class="doc-filename"
                                                            :class="{ reajustada: doc.qdeReajustada !== null && doc.qdeReajustada !== undefined }"
                                                            @click.prevent="openDocumento(doc.file)" href="#">
                                                            {{ formatFilename(doc.filename, true) }}
                                                        </a>
                                                        <span class="document-quantity">
                                                            Qtd: {{ doc.qdeReajustada != null ? doc.qdeReajustada :
                                                                doc.quantidade }}
                                                            <a href="#" class="reajustar-link"
                                                                @click.prevent="openReajusteModal(doc, processo)">
                                                                reajustar
                                                            </a>
                                                        </span>
                                                    </li>
                                                </ul>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <!-- Tarefas de itemização -->
                            <ul v-if="itemizacao.tarefas && itemizacao.tarefas.length">
                                <li v-for="tarefa in itemizacao.tarefas" :key="tarefa.id">
                                    <div class="tarefa" @click.stop="openTarefa(tarefa)">
                                        {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                        <ul v-if="tarefa.documentos && tarefa.documentos.length">
                                            <li v-for="doc in tarefa.documentos" :key="doc.id"
                                                style="margin-left: 10px;">
                                                <a class="doc-filename"
                                                    :class="{ reajustada: doc.qdeReajustada !== null && doc.qdeReajustada !== undefined }"
                                                    @click.prevent="openDocumento(doc.file)" href="#">
                                                    {{ formatFilename(doc.filename, true) }}
                                                </a>
                                                <span class="document-quantity">
                                                    Qtd: {{ doc.qdeReajustada != null ? doc.qdeReajustada :
                                                        doc.quantidade }}
                                                    <a href="#" class="reajustar-link"
                                                        @click.prevent="openReajusteModal(doc, processo)">
                                                        reajustar
                                                    </a>
                                                </span>
                                            </li>
                                        </ul>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal de Documento (PDF/Imagem) -->
        <div v-if="isModalDocOpen" class="modal modal-doc" @click.self="closeModalDoc">
            <div class="modal-content modal-content-doc">
                <div class="header-actions">
                    <h1>Documento</h1>
                    <button type="button" @click.stop="closeModalDoc">Fechar</button>
                </div>
                <hr class="section-divider" />
                <iframe :src="pdfUrl"></iframe>
            </div>
        </div>

        <!-- Modal de Reajuste -->
        <div v-if="isModalReajusteOpen" class="modal modal-doc" @click.self="closeModalReajuste">
            <div class="modal-content modal-content-reajuste">
                <div class="header-actions">
                    <h1>Reajustar Quantidade</h1>
                    <button type="button" @click="closeModalReajuste">Fechar</button>
                </div>
                <hr class="section-divider" />
                <form @submit.prevent="submitReajuste">
                    <div>
                        <label>Nova quantidade:</label>
                        <input type="number" v-model="reajusteForm.qdeReajustada" min="0" required />
                    </div>
                    <div>
                        <label>Justificativa:</label>
                        <textarea v-model="reajusteForm.obsReajuste" required></textarea>
                    </div>
                    <button type="submit" class="btn-reajustar">Salvar</button>
                </form>
            </div>
        </div>

        <!-- Modal de Aviso de Reajuste -->
        <div v-if="isModalAvisoReajusteOpen" class="modal modal-doc" @click.self="closeModalAvisoReajuste">
            <div class="modal-content modal-content-reajuste">
                <div class="header-actions">
                    <h1>Aviso</h1>
                    <button type="button" @click="closeModalAvisoReajuste">Fechar</button>
                </div>
                <hr class="section-divider" />
                <div>
                    <p>O reajuste só é permitido quando o processo estiver <b>Submetido</b>.</p>
                </div>
            </div>
        </div>

        <ConfirmDialog ref="confirmDialog" class="confirm-dialog-modal" />
        <MessageDialog ref="messageDialog" />
    </div>
</template>

<script>
import api from "@/services/api";
import * as pdfjsLib from 'pdfjs-dist/webpack';

export default {
    data() {
        return {
            processoId: localStorage.getItem("processoId"),
            usuarioProcessoId: localStorage.getItem("usuarioProcessoId"),
            processos: [],
            pontos: null,
            pontosPorItem: {},
            openAccordions: [],
            isAuthenticated: !!localStorage.getItem('access_token'),
            pdfUrl: null,
            isModalTarefaOpen: false,
            isModalDocOpen: false,
            uploadedDocuments: [],
            tarefaSelecionada: null,
            taskId: null,
            isModalReajusteOpen: false,
            isModalAvisoReajusteOpen: false,
            docSelecionado: null,
            reajusteForm: {
                qdeReajustada: null,
                obsReajuste: '',
            },
        };
    },
    async mounted() {
        await this.fetchProcessoTreeUsuario();
    },
    methods: {
        async fetchProcessoTreeUsuario() {
            try {
                const response = await api.get(`/usuario-processo/${this.usuarioProcessoId}/processo-tree/`);
                const processo = response.data;
                this.processos = [processo];
                this.pontos = processo.total_pontos;
                this.pontosPorItem = this.montarMapaPontos(processo);
            } catch (error) {
                console.error('Erro ao buscar processo do usuário:', error);
            }
        },
        montarMapaPontos(processo) {
            const mapa = {};
            function recItemizacoes(arr) {
                arr.forEach(item => {
                    mapa[item.id] = item.total_pontos || 0;
                    if (item.subitemizacoes) recItemizacoes(item.subitemizacoes);
                });
            }
            if (processo.itemizacoes) recItemizacoes(processo.itemizacoes);
            mapa[processo.id] = processo.total_pontos;
            return mapa;
        },
        isOpen(id) {
            return this.openAccordions.includes(id);
        },
        toggleAccordion(id) {
            if (this.openAccordions.includes(id)) {
                this.openAccordions = this.openAccordions.filter((accordionId) => accordionId !== id);
            } else {
                this.openAccordions.push(id);
            }
        },
        openTarefa(tarefa) {
            this.uploadedDocuments = tarefa.documentos || [];
            this.tarefaSelecionada = tarefa;
            this.taskId = tarefa.id;
            this.isModalTarefaOpen = true;
        },
        async openDocumento(filename) {
            this.isModalDocOpen = true;
            this.pdfUrl = filename;
            try {
                const response = await fetch(this.pdfUrl);
                if (!response.ok) throw new Error('Error fetching PDF file');
                const pdfBlob = await response.blob();
                const pdfBlobUrl = URL.createObjectURL(pdfBlob);
                pdfjsLib.getDocument(pdfBlobUrl).promise.then(() => { }).catch((error) => {
                    console.error('Error loading PDF:', error);
                });
            } catch (error) {
                console.error('Error fetching PDF URL:', error);
            }
        },
        closeModalDoc() {
            this.isModalDocOpen = false;
        },
        closeModalTarefa() {
            this.isModalTarefaOpen = false;
        },
        openReajusteModal(doc, processo) {
            if ((processo.status || '').toLowerCase() !== 'submetido') {
                this.isModalAvisoReajusteOpen = true;
                return;
            }
            this.docSelecionado = doc;
            this.reajusteForm.qdeReajustada = doc.qdeReajustada ?? doc.quantidade;
            this.reajusteForm.obsReajuste = doc.obsReajuste || '';
            this.isModalReajusteOpen = true;
        },
        closeModalReajuste() {
            this.isModalReajusteOpen = false;
            this.docSelecionado = null;
            this.reajusteForm.qdeReajustada = null;
            this.reajusteForm.obsReajuste = '';
        },
        closeModalAvisoReajuste() {
            this.isModalAvisoReajusteOpen = false;
        },
        async submitReajuste() {
            try {
                await api.patch(`/usuario-docs/${this.docSelecionado.id}/`, {
                    qdeReajustada: this.reajusteForm.qdeReajustada,
                    obsReajuste: this.reajusteForm.obsReajuste,
                });
                this.closeModalReajuste();
                await this.fetchProcessoTreeUsuario(); // <- aqui recarrega a árvore com pontos atualizados!
            } catch (err) {
                alert("Erro ao reajustar documento");
            }
        },
        formatFilename(filename, limit = true) {
            const maxLength = 40;
            if (!filename) return '';
            const [name, extension] = filename.split(/(?=\.[^.]+$)/);
            if (!limit || filename.length <= maxLength) {
                return filename;
            }
            const ext = extension || '';
            const truncatedName = name.slice(0, maxLength - (ext.length ? ext.length + 3 : 3));
            return `${truncatedName}...${ext}`;
        },
        voltarParaTelaAnterior() {
            if (this.$router) {
                this.$router.go(-1);
            } else {
                window.history.back();
            }
        },
    }
};
</script>

<style scoped>
.pontos-info {
    color: #007bff;
    font-size: 1em;
}

.processo-title {
    font-size: 1rem;
    font-weight: bold;
}

.itemizacao-title {
    font-size: 0.90rem;
    font-weight: bold;
}

.subitem-title {
    font-size: 0.80rem;
    font-weight: bold;
}

.subsubitem-title {
    font-size: 0.70rem;
    font-weight: 600;
}

.tarefa {
    cursor: pointer;
    font-size: 0.85rem;
}

.accordion-item {
    border: 1px solid #ccc;
    margin: 8px 0;
    border-radius: 5px;
}

.accordion-header {
    background: #f4f4f4;
    padding: 10px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.accordion-header:hover {
    background: #eaeaea;
}

.accordion-content {
    padding: 9px 10px;
    border-top: 1px solid #ccc;
}

.modal,
.modal-doc,
.modal-tarefa {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw !important;
    height: 100vh !important;
    background-color: rgba(0, 0, 0, 0.5) !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.modal {
    z-index: 20000 !important;
}

.modal-doc {
    z-index: 20001 !important;
}

.confirm-dialog-modal,
.modal.confirm-dialog-modal,
.modal[data-confirm-dialog] {
    z-index: 20000 !important;
    position: fixed !important;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* AUMENTADO: Modal para documentos */
.modal-content-doc {
    width: 90vw !important;
    height: 90vh !important;
    min-width: 0;
    min-height: 0;
    max-width: 98vw;
    max-height: 98vh;
}

/* MANTIDO: Modal pequeno para "reajustar" */
.modal-content-reajuste {
    width: 360px !important;
    min-width: 0 !important;
    max-width: 96vw !important;
    height: auto !important;
    max-height: 90vh !important;
    padding: 18px 18px 16px 18px;
    overflow-y: auto;
    box-sizing: border-box;
}

.modal-content-doc iframe {
    width: 100% !important;
    height: 87% !important;
}

/* AUMENTADO: Modal para tarefas */
.modal-content-tarefa {
    width: 100%;
    min-width: 400px;
    max-width: 1200px;
    min-height: 500px;
    display: flex;
    flex-direction: column;
    padding: 0;
    box-sizing: border-box;
    overflow-x: auto;
}

.modal-flex-vertical {
    display: flex;
    flex-direction: column;
}

.modal-flex {
    display: flex;
    flex-direction: row;
    gap: 0;
    width: 100%;
    flex: 1;
    box-sizing: border-box;
}

.modal-flex-right {
    flex: 1.1 1 0;
    min-width: 200px;
    padding: 24px 24px 18px 18px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    box-sizing: border-box;
}

.vertical-action-divider {
    width: 1px;
    height: 28px;
    background: #d6dbe2;
    margin: 0 10px;
    align-self: stretch;
}

.uploaded-document {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    flex-wrap: nowrap;
    box-sizing: border-box;
    max-width: 100%;
}

.document-details {
    flex: 1 0 0;
    min-width: 0;
}

.doc-filename {
    display: inline-block;
    max-width: 180px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
}

.doc-filename:hover,
.doc-filename:focus {
    color: #004999;
    outline: none;
}

.doc-filename.reajustada {
    color: #d32f2f !important;
    font-weight: bold;
}

.document-quantity {
    white-space: nowrap;
    font-size: 0.99em;
    color: #555;
}

.reajustar-link {
    color: #d32f2f;
    margin-left: 10px;
    cursor: pointer;
    text-decoration: underline;
    font-weight: bold;
}

.dialog-scrollable {
    overflow-y: auto;
    margin-bottom: 12px;
    padding-right: 4px;
    max-height: 210px;
    text-align: left;
}

.dialog-scrollable::-webkit-scrollbar {
    width: 8px;
}

.dialog-scrollable::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;
}

.dialog-scrollable::-webkit-scrollbar-thumb:hover {
    background: #888;
}

.section-title {
    color: #6c757d;
    font-size: 1.07rem;
    font-weight: normal;
    margin-bottom: 8px;
}

.header-actions h1 {
    font-size: 1.5rem;
}

.no-docs {
    color: #999;
    font-size: 1rem;
    margin-top: 20px;
}

.btn-download-processo {
    background: #399b3a;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 1rem;
    margin-left: 10px;
    cursor: pointer;
    transition: background 0.18s;
    white-space: nowrap;
}

.btn-download-processo:hover {
    background: #2d7330;
}

.btn-back-processo {
    background: #bdbdbd;
    color: #222;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 1rem;
    margin-right: 8px;
    cursor: pointer;
    transition: background 0.18s;
    white-space: nowrap;
}

.btn-back-processo:hover {
    background: #868686;
}

.processo-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 12px;
}

.pdf-link-right {
    margin-left: auto;
    min-width: 110px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
}
</style>
