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
                            <button class="btn-back" @click.stop="handleVoltar">&#8592; Voltar</button>
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
                                                                <div class="doc-filename-container">
                                                                    <span>
                                                                        <a class="doc-filename"
                                                                            :class="{ reajustada: isDocReajustada(doc) }"
                                                                            @click.stop.prevent="openDocumento(doc.file)"
                                                                            href="#">
                                                                            {{ formatFilename(doc.filename, true) }}
                                                                        </a>
                                                                        <span class="document-quantity-inline">
                                                                            <template v-if="isDocReajustada(doc)">
                                                                                Qde: <s>{{ doc.quantidade }}</s> {{
                                                                                doc.qdeReajustada }}
                                                                            </template>
                                                                            <template v-else>
                                                                                Qde: {{ doc.quantidade }}
                                                                            </template>
                                                                        </span>
                                                                    </span>
                                                                    <template
                                                                        v-if="isDocReajustada(doc) && doc.obsReajuste">
                                                                        <div class="obs-reajuste-doc">
                                                                            ({{ doc.obsReajuste }})
                                                                        </div>
                                                                    </template>
                                                                </div>
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    <ul v-if="subitem.tarefas && subitem.tarefas.length">
                                        <li v-for="tarefa in subitem.tarefas" :key="tarefa.id">
                                            <div class="tarefa">
                                                <div @click.stop="openTarefa(tarefa)">
                                                    {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                                </div>
                                                <ul v-if="tarefa.documentos && tarefa.documentos.length">
                                                    <li v-for="doc in tarefa.documentos" :key="doc.id"
                                                        style="margin-left: 10px;">
                                                        <div class="doc-filename-container">
                                                            <span>
                                                                <a class="doc-filename"
                                                                    :class="{ reajustada: isDocReajustada(doc) }"
                                                                    @click.stop.prevent="openDocumento(doc.file)"
                                                                    href="#">
                                                                    {{ formatFilename(doc.filename, true) }}
                                                                </a>
                                                                <span class="document-quantity-inline">
                                                                    <template v-if="isDocReajustada(doc)">
                                                                        Qde: <s>{{ doc.quantidade }}</s> {{
                                                                        doc.qdeReajustada }}
                                                                    </template>
                                                                    <template v-else>
                                                                        Qde: {{ doc.quantidade }}
                                                                    </template>
                                                                </span>
                                                            </span>
                                                            <template v-if="isDocReajustada(doc) && doc.obsReajuste">
                                                                <div class="obs-reajuste-doc">
                                                                    ({{ doc.obsReajuste }})
                                                                </div>
                                                            </template>
                                                        </div>
                                                    </li>
                                                </ul>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <ul v-if="itemizacao.tarefas && itemizacao.tarefas.length">
                                <li v-for="tarefa in itemizacao.tarefas" :key="tarefa.id">
                                    <div class="tarefa" @click.stop="openTarefa(tarefa)">
                                        {{ tarefa.nome }} ({{ tarefa.ponto }} pts)
                                        <ul v-if="tarefa.documentos && tarefa.documentos.length">
                                            <li v-for="doc in tarefa.documentos" :key="doc.id"
                                                style="margin-left: 10px;">
                                                <div class="doc-filename-container">
                                                    <span>
                                                        <a class="doc-filename"
                                                            :class="{ reajustada: isDocReajustada(doc) }"
                                                            @click.stop.prevent="openDocumento(doc.file)" href="#">
                                                            {{ formatFilename(doc.filename, true) }}
                                                        </a>
                                                        <span class="document-quantity-inline">
                                                            <template v-if="isDocReajustada(doc)">
                                                                Qde: <s>{{ doc.quantidade }}</s> {{ doc.qdeReajustada }}
                                                            </template>
                                                            <template v-else>
                                                                Qde: {{ doc.quantidade }}
                                                            </template>
                                                        </span>
                                                    </span>
                                                    <template v-if="isDocReajustada(doc) && doc.obsReajuste">
                                                        <div class="obs-reajuste-doc">
                                                            ({{ doc.obsReajuste }})
                                                        </div>
                                                    </template>
                                                </div>
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

        <!-- Modal de Documento -->
        <div v-if="isModalDocOpen" class="modal modal-doc" @click.self="closeModalDoc">
            <div class="modal-content modal-content-doc">
                <div class="header-actions">
                    <h1>Documento</h1>
                    <button type="button" class="btn-close" @click.stop="closeModalDoc">Fechar</button>
                </div>
                <hr class="section-divider" />
                <iframe :src="pdfUrl"></iframe>
            </div>
        </div>

        <!-- Modal de Tarefa -->
        <div v-if="isModalTarefaOpen" class="modal modal-tarefa" @click.self="closeModalTarefa">
            <div class="modal-content modal-content-tarefa modal-flex-vertical">
                <div class="descricao-tarefa-topo" v-if="tarefaSelecionada && tarefaSelecionada.descricao">
                    <strong>Descrição da Tarefa:</strong>
                    <div class="descricao-tarefa-texto">{{ tarefaSelecionada.descricao }}</div>
                </div>
                <div class="modal-flex">
                    <div class="form-section modal-flex-left">
                        <form @submit.prevent="submitForm()" enctype="multipart/form-data">
                            <div class="form-group">
                                <label for="inputArquivo">Arquivo:</label>
                                <label class="custom-file-upload">
                                    <input type="file" ref="inputArquivo" id="inputArquivo"
                                        @change="handleFileChange($event)" :disabled="isEditMode" v-if="!isEditMode" />
                                    <span>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none"
                                            viewBox="0 0 24 24">
                                            <path fill="#007bff"
                                                d="M12 16.5c-.41 0-.75-.34-.75-.75V7.81l-2.22 2.22a.75.75 0 0 1-1.06-1.06l3.5-3.5a.75.75 0 0 1 1.06 0l3.5 3.5a.75.75 0 1 1-1.06 1.06L12.75 7.81v7.94c0 .41-.34.75-.75.75ZM6 19.25a.75.75 0 0 1 0-1.5h12a.75.75 0 0 1 0 1.5H6Z" />
                                        </svg>
                                        <span>{{ formData.file ? formData.file.name : 'Selecionar arquivo' }}</span>
                                    </span>
                                </label>
                            </div>
                            <div class="form-group">
                                <label :for="formData.quantidade">
                                    Quantidade (máx: {{ tarefaSelecionada?.maximo || '-' }})
                                </label>
                                <input type="number" v-model="formData.quantidade" :id="formData.quantidade" required
                                    min="1"
                                    :max="tarefaSelecionada?.maximo ? tarefaSelecionada.maximo - totalEnviadoExcetoEdit : null" />
                            </div>
                            <div class="form-group">
                                <label :for="formData.descricao">Descrição:</label>
                                <textarea v-model="formData.descricao" :id="formData.descricao"></textarea>
                            </div>
                            <div v-if="avisoMaximo" class="aviso-maximo">
                                {{ avisoMaximo }}
                            </div>
                            <div class="button-container">
                                <button type="submit">{{ isEditMode ? 'Alterar' : 'Enviar' }}</button>
                                <button type="button" @click="cancelEdit" v-if="isEditMode">Cancelar</button>
                                <button type="button" @click.stop="closeModalTarefa">Fechar</button>
                            </div>
                        </form>
                    </div>
                    <div class="vertical-divider"></div>
                    <div class="modal-flex-right">
                        <h4 class="section-title">Documentos Enviados</h4>
                        <div class="dialog-scrollable">
                            <div v-if="uploadedDocuments && uploadedDocuments.length">
                                <div v-for="(docTask, index) in uploadedDocuments" :key="index"
                                    class="uploaded-document">
                                    <div class="document-details">
                                        <div class="doc-filename-container">
                                            <span>
                                                <a class="download doc-filename"
                                                    :class="{ reajustada: isDocReajustada(docTask) }"
                                                    @click.stop.prevent="openDocumento(docTask.file)" href="#"
                                                    :title="formatFilename(docTask.filename, false)">
                                                    {{ formatFilename(docTask.filename, true) }}
                                                </a>
                                                <span class="document-quantity-inline">
                                                    <template v-if="isDocReajustada(docTask)">
                                                        Qde: <s>{{ docTask.quantidade }}</s> {{ docTask.qdeReajustada }}
                                                    </template>
                                                    <template v-else>
                                                        Qde: {{ docTask.quantidade }}
                                                    </template>
                                                </span>
                                            </span>
                                            <template v-if="isDocReajustada(docTask) && docTask.obsReajuste">
                                                <div class="obs-reajuste-doc">
                                                    ({{ docTask.obsReajuste }})
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="vertical-action-divider"></div>
                                    <div class="action-buttons">
                                        <button class="btn edit-btn btn-sm" @click="editDocument(docTask)">
                                            Alterar
                                        </button>
                                        <button class="btn delete-btn btn-sm"
                                            @click="abrirConfirmacaoExcluir(docTask.id)">
                                            Excluir
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="no-docs">Nenhum documento enviado.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal de Confirmação Exclusão -->
        <div v-if="modalConfirmacao.visivel" class="modal modal-log" @click.self="fecharModalConfirmacao">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>{{ modalConfirmacao.titulo }}</h3>
                </div>
                <hr class="section-divider" />
                <div>
                    <p>{{ modalConfirmacao.mensagem }}</p>
                </div>
                <div class="modal-actions">
                    <button class="btn-acoes salvar-btn" @click="confirmarAcaoExcluir">{{
                        modalConfirmacao.textoConfirmar }}</button>
                    <button class="btn-acoes cancelar-btn" @click="fecharModalConfirmacao">Cancelar</button>
                </div>
            </div>
        </div>

        <div v-if="toast.show" :class="['custom-toast', toast.type]">
            {{ toast.message }}
        </div>
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
            formData: {
                file: null,
                descricao: null,
                quantidade: null
            },
            uploadedDocuments: [],
            isEditMode: false,
            editingDocumentIndex: null,
            tarefaSelecionada: null,
            taskId: null,
            avisoMaximo: "",
            modalConfirmacao: {
                visivel: false,
                docId: null,
                titulo: '',
                mensagem: '',
                textoConfirmar: ''
            },
            toast: {
                show: false,
                message: "",
                type: "info"
            },
            toastTimeout: null,
        };
    },
    computed: {
        totalEnviadoExcetoEdit() {
            let enviados = 0;
            this.uploadedDocuments.forEach(doc => {
                if (!this.isEditMode || doc.id !== this.editingDocumentIndex) {
                    enviados += Number(doc.quantidade || 0);
                }
            });
            return enviados;
        }
    },
    watch: {
        isModalTarefaOpen(val) { if (val) this.avisoMaximo = ""; },
        'formData.quantidade'(val) { this.avisoMaximo = ""; }
    },
    async mounted() {
        await this.fetchProcessoTreeUsuario();
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
        async fetchProcessoTreeUsuario() {
            try {
                const response = await api.get(`/usuario-processo/${this.usuarioProcessoId}/processo-tree/`);
                const processo = response.data;
                this.processos = [processo];
                this.pontos = processo.total_pontos;
                this.pontosPorItem = this.montarMapaPontos(processo);
            } catch (error) {
                this.showToast('Erro ao buscar processo do usuário.', 'error');
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
            this.formData = {
                file: null,
                descricao: null,
                quantidade: null
            };
            this.tarefaSelecionada = tarefa;
            this.taskId = tarefa.id;
            this.editingDocumentIndex = null;
            this.isEditMode = false;
            this.avisoMaximo = "";
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
                pdfjsLib.getDocument(pdfBlobUrl).promise.then(() => { }).catch(() => { });
            } catch (error) {
                this.showToast('Erro ao abrir o documento.', 'error');
            }
        },
        closeModalDoc() {
            this.isModalDocOpen = false;
        },
        handleVoltar() {
            window.history.length > 1 ? window.history.back() : window.location.href = '/';
        },
        closeModalTarefa() {
            this.isModalTarefaOpen = false;
        },
        handleFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                this.formData.file = file;
                this.formData.filename = file.name
            }
        },
        async submitForm() {
            const maximo = Number(this.tarefaSelecionada?.maximo);
            let enviados = 0;
            this.uploadedDocuments.forEach(doc => {
                if (!this.isEditMode || doc.id !== this.editingDocumentIndex) {
                    enviados += Number(doc.quantidade || 0);
                }
            });
            const novaQtd = Number(this.formData.quantidade || 0);

            if (maximo > 0 && (enviados + novaQtd) > maximo) {
                const disponivel = maximo - enviados;
                this.avisoMaximo = `O máximo permitido para esta tarefa é ${maximo}. Você já enviou ${enviados}. Só pode enviar mais ${disponivel < 0 ? 0 : disponivel}.`;
                this.showToast(this.avisoMaximo, 'error');
                return;
            }

            const form = new FormData();
            if (!this.isEditMode && this.formData) {
                form.append("file", this.formData.file);
                form.append("filename", this.formData.filename);
                form.append("tarefaProcesso", this.taskId);
                form.append("usuarioProcesso", this.usuarioProcessoId);
            }
            if (this.isEditMode) {
                form.append("id", this.editingDocumentIndex);
            }
            form.append("descricao", this.formData.descricao);
            form.append("quantidade", this.formData.quantidade);
            try {
                const response = this.isEditMode
                    ? await api.put(`/usuario-docs/${this.editingDocumentIndex}/`, form, {
                        headers: { "Content-Type": "multipart/form-data" }
                    })
                    : await api.post("/usuario-docs/", form, {
                        headers: { "Content-Type": "multipart/form-data" }
                    });
                await this.fetchProcessoTreeUsuario();
                if (this.tarefaSelecionada) {
                    const tarefaAtualizada = this.encontraTarefaPorId(this.taskId, this.processos[0]);
                    if (tarefaAtualizada) {
                        this.openTarefa(tarefaAtualizada);
                    }
                }
                this.showToast(this.isEditMode ? 'Documento alterado com sucesso!' : 'Documento enviado com sucesso!', 'success');
                this.formData = {};
                this.isEditMode = false;
                this.editingDocumentIndex = null;
                this.avisoMaximo = "";
            } catch (error) {
                let erro = "Erro ao salvar o documento.";
                if (error.response) {
                    if (error.response.data.non_field_errors) {
                        erro = error.response.data.non_field_errors[0];
                    } else {
                        erro = 'Erro desconhecido, tente novamente.';
                    }
                }
                this.showToast(erro, 'error');
            }
        },
        encontraTarefaPorId(id, processo) {
            function busca(arr) {
                for (const item of arr) {
                    if (item.tarefas) {
                        for (const tarefa of item.tarefas) {
                            if (tarefa.id === id) return tarefa;
                        }
                    }
                    if (item.subitemizacoes) {
                        const achou = busca(item.subitemizacoes);
                        if (achou) return achou;
                    }
                }
                return null;
            }
            if (processo.itemizacoes) {
                return busca(processo.itemizacoes);
            }
            return null;
        },
        editDocument(doc) {
            this.isEditMode = true;
            this.editingDocumentIndex = doc.id;
            this.formData = {
                file: null,
                descricao: doc.descricao,
                quantidade: doc.quantidade
            };
            this.avisoMaximo = "";
        },
        cancelEdit() {
            this.isEditMode = false;
            this.editingDocumentIndex = null;
            this.formData = {};
            this.avisoMaximo = "";
        },
        abrirConfirmacaoExcluir(docId) {
            this.modalConfirmacao = {
                visivel: true,
                docId,
                titulo: 'Excluir Documento',
                mensagem: 'Tem certeza que deseja excluir este documento?',
                textoConfirmar: 'Excluir'
            };
        },
        fecharModalConfirmacao() {
            this.modalConfirmacao = {
                visivel: false,
                docId: null,
                titulo: '',
                mensagem: '',
                textoConfirmar: ''
            };
        },
        async confirmarAcaoExcluir() {
            await this.deleteDocument(this.modalConfirmacao.docId);
            this.fecharModalConfirmacao();
        },
        async deleteDocument(docId) {
            try {
                await api.delete(`/usuario-docs/${docId}/`);
                await this.fetchProcessoTreeUsuario();
                if (this.tarefaSelecionada) {
                    const tarefaAtualizada = this.encontraTarefaPorId(this.taskId, this.processos[0]);
                    if (tarefaAtualizada) {
                        this.openTarefa(tarefaAtualizada);
                    }
                }
                this.showToast('Documento excluído com sucesso!', 'success');
            } catch (error) {
                this.showToast('Erro ao excluir o documento.', 'error');
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
        isDocReajustada(doc) {
            return doc.qdeReajustada !== null && doc.qdeReajustada !== undefined && doc.qdeReajustada !== doc.quantidade;
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

.doc-filename-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 0px;
}

.document-quantity-inline {
    margin-left: 10px;
    color: #555;
    font-size: 0.98em;
    display: inline-block;
    vertical-align: middle;
}

.obs-reajuste-doc {
    color: #d32f2f;
    font-size: 0.93em;
    margin-left: 0px;
    margin-top: 2px;
    line-height: 1;
    font-style: italic;
}

.modal-tarefa {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: -50;
}

.modal,
.modal-doc {
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

.modal-content.modal-content-log {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 16px #0004;
    padding: 26px 28px 18px 28px;
    /* padding moderado */
    min-width: 320px;
    max-width: 90vw;
    min-height: 0;
    max-height: 92vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 19px;
    align-items: flex-start;
}

.modal-content-log .modal-header {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
}

.modal-content-log .modal-header h3 {
    font-size: 1.08rem;
    font-weight: bold;
    margin: 0;
    color: #222;
}

.modal-content-log p {
    font-size: 1.02rem;
    margin-bottom: 10px;
    margin-top: 8px;
}

.modal-content-log .modal-actions {
    display: flex;
    gap: 18px;
    /* espaçamento entre os botões */
    margin-top: 10px;
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

.header-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.btn-back {
    background-color: #f0f0f0;
    color: #555;
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 1rem;
    margin-right: 10px;
    cursor: pointer;
    transition: background 0.18s;
}

.btn-back:hover {
    background: #e2e2e2;
    color: #222;
    border-color: #888;
}

.btn-close {
    background: #dc3545;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    margin-left: 8px;
    transition: background 0.18s;
}

.btn-close:hover {
    background: #a71d2a;
}

.modal-content-tarefa {
    width: 100%;
    min-width: 320px;
    max-width: 900px;
    min-height: 350px;
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

.descricao-tarefa-topo {
    width: 100%;
    background: #f3f8ff;
    border-bottom: 1px solid #d5e2f5;
    padding: 14px 24px 10px 24px;
    margin-bottom: 0;
    font-size: 1.07rem;
}

.descricao-tarefa-texto {
    margin-top: 4px;
    color: #305080;
    font-size: 1.01rem;
    font-weight: 500;
    white-space: pre-line;
}

.modal-flex-left {
    flex: 1 1 0;
    padding: 24px 18px 18px 24px;
    min-width: 260px;
    max-width: 350px;
    display: flex;
    align-items: flex-start;
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

.vertical-divider {
    width: 2px;
    background: #ededed;
    min-height: 280px;
    margin: 0 8px;
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

.vertical-action-divider {
    width: 1px;
    height: 28px;
    background: #d6dbe2;
    margin: 0 10px;
    align-self: stretch;
}

.action-buttons {
    display: flex;
    flex-direction: row;
    gap: 5px;
    align-items: center;
    flex-shrink: 0;
    flex-wrap: wrap;
}

.btn-sm {
    font-size: 0.92rem;
    padding: 5px 10px;
    border-radius: 3px;
}

.edit-btn {
    background-color: #007bff;
    color: white;
    border: none;
}

.delete-btn {
    background-color: #dc3545;
    color: white;
    border: none;
}

.edit-btn:hover,
.delete-btn:hover {
    opacity: 0.9;
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

.button-container {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-top: 16px;
}

.button-container button {
    padding: 8px 18px;
    font-size: 15px;
    cursor: pointer;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    transition: background-color 0.3s ease;
}

.button-container button:hover {
    background-color: #0056b3;
}

.button-container button:nth-child(2) {
    background-color: #dc3545;
}

.button-container button:nth-child(2):hover {
    background-color: #a71d2a;
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

.form-group label {
    font-size: 1rem;
    margin-bottom: 3px;
    display: block;
}

.custom-file-upload {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #f7faff;
    cursor: pointer;
    transition: border 0.2s;
    margin-top: 2px;
    margin-bottom: 7px;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
}

.custom-file-upload:hover,
.custom-file-upload:focus-within {
    border: 1.5px solid #007bff;
    background: #f0f8ff;
}

.custom-file-upload input[type="file"] {
    display: none;
}

.custom-file-upload svg {
    margin-right: 6px;
}

.form-group input,
.form-group textarea {
    font-size: 1rem;
    width: 100%;
    margin-bottom: 7px;
    padding: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
}

.aviso-maximo {
    color: #c00;
    background: #ffeaea;
    margin-bottom: 6px;
    padding: 5px 7px;
    border-radius: 4px;
    font-size: 0.98rem;
    border: 1px solid #c00;
}

@media (max-width: 850px) {
    .modal-content-tarefa {
        max-width: 55vw;
        min-width: 0;
        padding: 0;
    }

    .modal-content-doc {
        width: 96vw;
        min-width: 0;
        height: 75vh;
        min-height: 220px;
    }

    .modal-flex {
        flex-direction: column;
    }

    .vertical-divider {
        display: none;
    }

    .modal-flex-right {
        max-width: 100%;
        min-width: 0;
        padding: 12px !important;
    }

    .uploaded-document {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }

    .action-buttons {
        margin-top: 6px;
    }
}

.btn-download-processo {
    background: #399b3a;
    color: #fff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 1rem;
    margin-left: 0;
    margin-right: 10px;
    cursor: pointer;
    transition: background 0.18s;
    white-space: nowrap;
}

.btn-download-processo:hover {
    background: #2d7330;
}

.pontos-info {
    color: #007bff;
    font-size: 1em;
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
    min-width: 190px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
}

.pdf-download-link {
    color: #007bff;
    text-decoration: none;
    font-weight: 600;
    margin-left: 3px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.pdf-download-link:hover {
    text-decoration: underline;
    color: #004999;
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