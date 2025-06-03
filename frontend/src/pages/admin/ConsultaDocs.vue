<template>
    <div v-if="isAuthenticated" class="padrao-list">
        <div v-for="(processo, procIdx) in processos" :key="processo.id">
            <div class="accordion-item">
                <div class="accordion-header" @click="toggleAccordion(processo.id)">
                    <h3 class="processo-title">
                        {{ processo.nome }}
                        <span v-if="pontosPorItem[processo.id] !== undefined" class="pontos-info">
                            | Pontuação do usuário: {{ pontosPorItem[processo.id] }}
                            / Pontuação necessária: {{ processo.pontos }}
                        </span>
                    </h3>
                    <!-- Botão download só no primeiro processo exibido -->
                    <template v-if="procIdx === 0">
                        <button class="btn-download-processo" @click.stop="openDocumento(processo.link_processo_pdf)">
                            Download
                        </button>
                    </template>
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
                                                    <div class="tarefa" @click.stop="toggleTarefa(tarefa)">
                                                        {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                                    </div>
                                                    <div v-if="isTarefaOpen(tarefa)" class="documentos-tarefa">
                                                        <div class="descricao-tarefa-topo" v-if="tarefa.descricao">
                                                            <strong>Descrição da Tarefa:</strong>
                                                            <div class="descricao-tarefa-texto">{{ tarefa.descricao }}
                                                            </div>
                                                        </div>
                                                        <h4 class="section-title">Documentos Enviados</h4>
                                                        <div class="dialog-scrollable">
                                                            <div
                                                                v-if="uploadedDocs[tarefa.id] && uploadedDocs[tarefa.id].length">
                                                                <div v-for="(docTask, index) in uploadedDocs[tarefa.id]"
                                                                    :key="index" class="uploaded-document">
                                                                    <div class="document-details">
                                                                        <a class="download doc-filename" href="#"
                                                                            @click.prevent="openDocumento(docTask.file)"
                                                                            :title="formatFilename(docTask.filename, false)">
                                                                            {{ formatFilename(docTask.filename, true) }}
                                                                        </a>
                                                                    </div>
                                                                    <div class="vertical-action-divider"></div>
                                                                    <span class="document-quantity">Quantidade: {{
                                                                        docTask.quantidade
                                                                        }}</span>
                                                                </div>
                                                            </div>
                                                            <div v-else class="no-docs">Nenhum documento enviado.</div>
                                                        </div>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    <ul v-if="subitem.tarefas && subitem.tarefas.length">
                                        <li v-for="tarefa in subitem.tarefas" :key="tarefa.id">
                                            <div class="tarefa" @click.stop="toggleTarefa(tarefa)">
                                                {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                            </div>
                                            <div v-if="isTarefaOpen(tarefa)" class="documentos-tarefa">
                                                <div class="descricao-tarefa-topo" v-if="tarefa.descricao">
                                                    <div class="descricao-tarefa-texto">{{ tarefa.descricao }}</div>
                                                </div>
                                                <div class="dialog-scrollable">
                                                    <div
                                                        v-if="uploadedDocs[tarefa.id] && uploadedDocs[tarefa.id].length">
                                                        <div v-for="(docTask, index) in uploadedDocs[tarefa.id]"
                                                            :key="index" class="uploaded-document">
                                                            <div class="document-details">
                                                                <a class="download doc-filename" href="#"
                                                                    @click.prevent="openDocumento(docTask.file)"
                                                                    :title="formatFilename(docTask.filename, false)">
                                                                    {{ formatFilename(docTask.filename, true) }}
                                                                </a>
                                                            </div>
                                                            <div class="vertical-action-divider"></div>
                                                            <span class="document-quantity">Quantidade: {{
                                                                docTask.quantidade }}</span>
                                                        </div>
                                                    </div>
                                                    <div v-else class="no-docs">Nenhum documento enviado.</div>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <ul v-if="itemizacao.tarefas && itemizacao.tarefas.length">
                                <li v-for="tarefa in itemizacao.tarefas" :key="tarefa.id">
                                    <div class="tarefa" @click.stop="toggleTarefa(tarefa)">
                                        {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                    </div>
                                    <div v-if="isTarefaOpen(tarefa)" class="documentos-tarefa">
                                        <div class="descricao-tarefa-topo" v-if="tarefa.descricao">
                                            <strong>Descrição da Tarefa:</strong>
                                            <div class="descricao-tarefa-texto">{{ tarefa.descricao }}</div>
                                        </div>
                                        <h4 class="section-title">Documentos Enviados</h4>
                                        <div class="dialog-scrollable">
                                            <div v-if="uploadedDocs[tarefa.id] && uploadedDocs[tarefa.id].length">
                                                <div v-for="(docTask, index) in uploadedDocs[tarefa.id]" :key="index"
                                                    class="uploaded-document">
                                                    <div class="document-details">
                                                        <a class="download doc-filename" href="#"
                                                            @click.prevent="openDocumento(docTask.file)"
                                                            :title="formatFilename(docTask.filename, false)">
                                                            {{ formatFilename(docTask.filename, true) }}
                                                        </a>
                                                    </div>
                                                    <div class="vertical-action-divider"></div>
                                                    <span class="document-quantity">Quantidade: {{ docTask.quantidade
                                                        }}</span>
                                                </div>
                                            </div>
                                            <div v-else class="no-docs">Nenhum documento enviado.</div>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal de Documento (PDF/Imagem ou Processo Completo) -->
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
            tarefaAbertas: [],
            uploadedDocs: {}, // mapped by tarefa.id
            isModalDocOpen: false,
            pdfUrl: null,
        };
    },
    async mounted() {
        await this.fetchProcessos();
        await this.fetchUsuarioProcessos();
    },
    methods: {
        async fetchProcessos() {
            try {
                const response = await api.get('/processo-tree/');
                this.processos = response.data.filter((processo) => processo.id === this.processoId);
                await this.calcularPontuacaoTodos(this.processos);
            } catch (error) {
                console.error('Erro ao buscar processos:', error);
            }
        },
        async fetchUsuarioProcessos() {
            try {
                const response = await api.get(`/usuario-processo/by-uuid/${this.usuarioProcessoId}`);
                this.pontos = response.data.total_pontos;
                console.log("Pontos do usuário:", response);
            } catch (error) {
                console.error("Erro ao carregar o processo do usuário:", error);
            }
        },
        async calcularPontosDoItem(item) {
            let soma = 0;
            if (item.subitemizacoes && item.subitemizacoes.length) {
                for (const subitem of item.subitemizacoes) {
                    await this.calcularPontosDoItem(subitem);
                    soma += this.pontosPorItem[subitem.id] || 0;
                }
            } else if (item.itemizacoes && item.itemizacoes.length) {
                for (const itemizacao of item.itemizacoes) {
                    await this.calcularPontosDoItem(itemizacao);
                    soma += this.pontosPorItem[itemizacao.id] || 0;
                }
            } else if (item.tarefas && item.tarefas.length) {
                for (const tarefa of item.tarefas) {
                    try {
                        const response = await api.get(`/usuario-docs/filtro_por_usuario_tarefa_usuarioProcesso`, {
                            params: {
                                tarefa: tarefa.id,
                                usuarioProcesso: this.usuarioProcessoId
                            }
                        });
                        if (response.data && response.data.length) {
                            for (const doc of response.data) {
                                soma += (doc.quantidade || 0) * (tarefa.ponto || 0);
                            }
                        }
                    } catch (err) { }
                }
            }
            this.pontosPorItem[item.id] = soma;
        },
        async calcularPontuacaoTodos(lista) {
            for (const item of lista) {
                await this.calcularPontosDoItem(item);
                if (item.itemizacoes && item.itemizacoes.length) {
                    await this.calcularPontuacaoTodos(item.itemizacoes);
                }
                if (item.subitemizacoes && item.subitemizacoes.length) {
                    await this.calcularPontuacaoTodos(item.subitemizacoes);
                }
            }
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
        isTarefaOpen(tarefa) {
            return this.tarefaAbertas.includes(tarefa.id);
        },
        async toggleTarefa(tarefa) {
            if (this.isTarefaOpen(tarefa)) {
                this.tarefaAbertas = this.tarefaAbertas.filter(id => id !== tarefa.id);
            } else {
                this.tarefaAbertas.push(tarefa.id);
                if (!this.uploadedDocs[tarefa.id]) {
                    await this.fetchUploadedDocuments(tarefa);
                }
            }
        },
        async fetchUploadedDocuments(tarefa) {
            if (!this.usuarioProcessoId || !tarefa?.id) return;
            try {
                const response = await api.get(`/usuario-docs/filtro_por_usuario_tarefa_usuarioProcesso`, {
                    params: {
                        tarefa: tarefa.id,
                        usuarioProcesso: this.usuarioProcessoId
                    }
                });
                this.uploadedDocs[tarefa.id] = response.data || [];
            } catch (error) {
                console.error("Erro ao buscar documentos enviados:", error);
                this.uploadedDocs[tarefa.id] = [];
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
        async openDocumento(filename) {
            this.isModalDocOpen = true;
            this.pdfUrl = filename;
            console.log('Abrindo documento:', this.pdfUrl);
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
        }
    }
};
</script>

<style scoped>
/* ...demais estilos... */
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

pontos-info {
    color: #007bff;
    font-size: 1em;
}

.processo-title {
    font-size: 1.4rem;
    font-weight: bold;
}

.itemizacao-title {
    font-size: 1.15rem;
    font-weight: bold;
}

.subitem-title {
    font-size: 1.05rem;
    font-weight: bold;
}

.subsubitem-title {
    font-size: 0.98rem;
    font-weight: 600;
}

.tarefa {
    cursor: pointer;
    font-size: 1rem;
    margin-top: 0.5em;
    margin-bottom: 0.2em;
    color: #234;
}

.tarefa:hover {
    text-decoration: underline;
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

.documentos-tarefa {
    background: #f8faff;
    border: 1px solid #e6e6f5;
    border-radius: 6px;
    margin: 6px 0 15px 0;
    padding: 13px 16px 10px 16px;
}

.descricao-tarefa-topo {
    width: 100%;
    background: #f3f8ff;
    border-bottom: 1px solid #d5e2f5;
    padding: 10px 0 5px 0;
    margin-bottom: 10px;
    font-size: 1.07rem;
}

.descricao-tarefa-texto {
    margin-top: 4px;
    color: #305080;
    font-size: 1.01rem;
    font-weight: 500;
    white-space: pre-line;
}

.section-title {
    color: #6c757d;
    font-size: 1.07rem;
    font-weight: normal;
    margin-bottom: 8px;
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
    background: #fff;
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

.vertical-action-divider {
    width: 1px;
    height: 28px;
    background: #d6dbe2;
    margin: 0 10px;
    align-self: stretch;
}

.document-quantity {
    white-space: nowrap;
    font-size: 0.99em;
    color: #555;
}

.no-docs {
    color: #999;
    font-size: 1rem;
    margin-top: 20px;
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

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
}

.modal-doc {
    z-index: 16000;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.modal-content-doc {
    width: 80vw !important;
    height: 80vh !important;
    min-width: 0;
    min-height: 0;
    max-width: 98vw;
    max-height: 98vh;
}

.modal-content-doc iframe {
    width: 100% !important;
    height: 90% !important;
}

.header-actions h1 {
    font-size: 1.5rem;
}

@media (max-width: 850px) {
    .uploaded-document {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }

    .modal-content-doc {
        width: 80vw !important;
        height: 80vh !important;
        min-width: 0;
        min-height: 0;
        max-width: 98vw;
        max-height: 98vh;
    }
}
</style>