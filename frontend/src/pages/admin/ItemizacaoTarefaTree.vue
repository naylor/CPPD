<template>
    <div class="arvore-wrapper">
        <div class="arvore-header">
            <h2>Árvore de Itemizações</h2>
            <div style="display: flex; align-items: center; gap: 12px;">
                <button class="btn-acoes voltar-btn" @click="voltar">
                    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none" stroke="#fff"
                        stroke-width="2" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                        <path d="M15 18l-6-6 6-6" />
                    </svg>
                    Voltar
                </button>
                <button class="btn-acoes salvar-btn" @click="openItemizacaoModal(null)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="#fff"
                        stroke-width="2" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                        <path d="M12 5v14M5 12h14" />
                    </svg>
                    Itemização Raiz
                </button>
            </div>
        </div>
        <!-- Mensagem de instrução para drag-and-drop -->
        <div class="drag-info">
            Arraste os itens com o mouse para trocar de lugar.
        </div>
        <div class="arvore-card">
            <div class="arvore-lista">
                <draggable v-model="treeData" item-key="id" group="{ name: 'tree' }"
                    @end="onItemizacaoDrop(treeData, null)">
                    <template #item="{ element, index }">
                        <div class="itemizacao-raiz">
                            <TreeNode :node="element" :nivel="0" @addItemizacao="openItemizacaoModal"
                                @addTarefa="openTarefaModal" @removeNode="confirmRemoveNode"
                                @updateTitle="handleUpdateTitle" @ordemChanged="onSubItemizacaoDrop"
                                @editItemizacao="openEditItemizacaoModal" @editTarefa="openEditTarefaModal" />
                        </div>
                    </template>
                </draggable>
            </div>
        </div>

        <!-- Modal para Itemização -->
        <div v-if="showItemizacaoModal" class="modal modal-log" @click.self="closeItemizacaoModal">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="#ffa600"
                            stroke-width="2" viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                            <rect x="4" y="4" width="16" height="16" rx="2" />
                            <path d="M8 9h8M8 13h4" />
                        </svg>
                        Nova Itemização
                    </h3>
                    <button class="modal-close" @click="closeItemizacaoModal">&times;</button>
                </div>
                <hr class="section-divider" />
                <form @submit.prevent="confirmAddItemizacao">
                    <label>
                        Nome:
                        <input v-model="novaItemizacao.nome" required autofocus />
                    </label>
                    <label>
                        Descrição:
                        <input v-model="novaItemizacao.descricao" />
                    </label>
                    <div class="modal-actions">
                        <button class="btn-acoes salvar-btn" type="submit">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#fff"
                                viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 3px;">
                                <path d="M5 12l5 5L20 7" stroke="#fff" stroke-width="2" fill="none" />
                            </svg>
                            Adicionar
                        </button>
                        <button class="btn-acoes cancelar-btn" type="button" @click="closeItemizacaoModal">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#444"
                                viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 2px;">
                                <line x1="18" y1="6" x2="6" y2="18" stroke="#444" stroke-width="2" />
                                <line x1="6" y1="6" x2="18" y2="18" stroke="#444" stroke-width="2" />
                            </svg>
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal para editar Itemização -->
        <div v-if="showEditItemizacaoModal" class="modal modal-log" @click.self="closeEditItemizacaoModal">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#ffa600" stroke-width="2"
                            viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                            <rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="#ffa600" />
                        </svg>
                        Editar Itemização
                    </h3>
                    <button class="modal-close" @click="closeEditItemizacaoModal">&times;</button>
                </div>
                <hr class="section-divider" />
                <form @submit.prevent="confirmEditItemizacao">
                    <label>
                        Nome:
                        <input v-model="editItemizacaoData.nome" required autofocus />
                    </label>
                    <label>
                        Descrição:
                        <input v-model="editItemizacaoData.descricao" />
                    </label>
                    <div class="modal-actions">
                        <button class="btn-acoes salvar-btn" type="submit">
                            Salvar
                        </button>
                        <button class="btn-acoes cancelar-btn" type="button" @click="closeEditItemizacaoModal">
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal para Tarefa -->
        <div v-if="showTarefaModal" class="modal modal-log" @click.self="closeTarefaModal">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#43a047"
                            viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                            <circle cx="12" cy="12" r="10" stroke="#43a047" stroke-width="2" fill="none" />
                            <path d="M8 12l2 2l4-4" stroke="#43a047" stroke-width="2" fill="none" />
                        </svg>
                        Nova Tarefa
                    </h3>
                    <button class="modal-close" @click="closeTarefaModal">&times;</button>
                </div>
                <hr class="section-divider" />
                <form @submit.prevent="confirmAddTarefa">
                    <label>
                        Nome:
                        <input v-model="novaTarefa.nome" required autofocus />
                    </label>
                    <label>
                        Descrição:
                        <input v-model="novaTarefa.descricao" />
                    </label>
                    <label>
                        Pontuação:
                        <input v-model.number="novaTarefa.ponto" type="number" required min="0" step="0.01" /> </label>
                    <label>
                        Mínimo:
                        <input v-model.number="novaTarefa.minimo" type="number" required min="0" />
                    </label>
                    <label>
                        Máximo:
                        <input v-model.number="novaTarefa.maximo" type="number" required min="0" />
                    </label>
                    <div class="modal-actions">
                        <button class="btn-acoes salvar-btn" type="submit">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#fff"
                                viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 3px;">
                                <path d="M5 12l5 5L20 7" stroke="#fff" stroke-width="2" fill="none" />
                            </svg>
                            Adicionar
                        </button>
                        <button class="btn-acoes cancelar-btn" type="button" @click="closeTarefaModal">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#444"
                                viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 2px;">
                                <line x1="18" y1="6" x2="6" y2="18" stroke="#444" stroke-width="2" />
                                <line x1="6" y1="6" x2="18" y2="18" stroke="#444" stroke-width="2" />
                            </svg>
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal para editar Tarefa -->
        <div v-if="showEditTarefaModal" class="modal modal-log" @click.self="closeEditTarefaModal">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#43a047"
                            viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                            <circle cx="12" cy="12" r="10" stroke="#43a047" stroke-width="2" fill="none" />
                        </svg>
                        Editar Tarefa
                    </h3>
                    <button class="modal-close" @click="closeEditTarefaModal">&times;</button>
                </div>
                <hr class="section-divider" />
                <form @submit.prevent="confirmEditTarefa">
                    <label>
                        Nome:
                        <input v-model="editTarefaData.nome" required autofocus />
                    </label>
                    <label>
                        Descrição:
                        <input v-model="editTarefaData.descricao" />
                    </label>
                    <label>
                        Pontuação:
                        <input v-model.number="editTarefaData.ponto" type="number" required min="0" />
                    </label>
                    <label>
                        Mínimo:
                        <input v-model.number="editTarefaData.minimo" type="number" required min="0" />
                    </label>
                    <label>
                        Máximo:
                        <input v-model.number="editTarefaData.maximo" type="number" required min="0" />
                    </label>
                    <div class="modal-actions">
                        <button class="btn-acoes salvar-btn" type="submit">
                            Salvar
                        </button>
                        <button class="btn-acoes cancelar-btn" type="button" @click="closeEditTarefaModal">
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Modal de confirmação para apagar -->
        <div v-if="modalConfirmacao.visivel" class="modal modal-log" @click.self="fecharModalConfirmacao">
            <div class="modal-content modal-content-log">
                <div class="modal-header">
                    <h3>
                        <svg v-if="modalConfirmacao.isItemizacao" xmlns="http://www.w3.org/2000/svg" width="18"
                            height="18" fill="#ffa600" viewBox="0 0 24 24"
                            style="vertical-align: middle; margin-right: 4px;">
                            <rect x="4" y="4" width="16" height="16" rx="2" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#d92424"
                            viewBox="0 0 24 24" style="vertical-align: middle; margin-right: 4px;">
                            <circle cx="12" cy="12" r="10" stroke="#d92424" stroke-width="2" fill="none" />
                        </svg>
                        {{ modalConfirmacao.titulo }}
                    </h3>
                    <button class="modal-close" @click="fecharModalConfirmacao">&times;</button>
                </div>
                <hr class="section-divider" />
                <div>
                    <p>{{ modalConfirmacao.mensagem }}</p>
                </div>
                <div class="modal-actions">
                    <button class="btn-acoes salvar-btn" @click="removerNodeConfirmado">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#fff" viewBox="0 0 24 24"
                            style="vertical-align: middle; margin-right: 3px;">
                            <path d="M5 12l5 5L20 7" stroke="#fff" stroke-width="2" fill="none" />
                        </svg>
                        Remover
                    </button>
                    <button class="btn-acoes cancelar-btn" @click="fecharModalConfirmacao">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#444" viewBox="0 0 24 24"
                            style="vertical-align: middle; margin-right: 2px;">
                            <line x1="18" y1="6" x2="6" y2="18" stroke="#444" stroke-width="2" />
                            <line x1="6" y1="6" x2="18" y2="18" stroke="#444" stroke-width="2" />
                        </svg>
                        Cancelar
                    </button>
                </div>
            </div>
        </div>

        <!-- Toast/Snackbar -->
        <Toast ref="toast" />

    </div>
</template>

<script>
import Toast from "@/components/Toast.vue";
import draggable from 'vuedraggable'
import TreeNode from './TreeNode.vue'
import api from '@/services/api'

export default {
    components: {
        Toast,
        draggable,
        TreeNode
    },
    data() {
        return {
            treeData: [],
            showItemizacaoModal: false,
            novaItemizacao: { nome: '', descricao: '' },
            itemizacaoParent: null,
            showTarefaModal: false,
            novaTarefa: { nome: '', descricao: '', ponto: 0, minimo: 0, maximo: 0 },
            tarefaParent: null,
            modalConfirmacao: {
                visivel: false,
                node: null,
                isItemizacao: false,
                titulo: "",
                mensagem: ""
            },
            // Novos estados para edição
            showEditItemizacaoModal: false,
            editItemizacaoTarget: null,
            editItemizacaoData: { nome: '', descricao: '' },
            showEditTarefaModal: false,
            editTarefaTarget: null,
            editTarefaData: { nome: '', descricao: '', ponto: 0, minimo: 0, maximo: 0 }
        }
    },
    created() {
        this.fetchArvore()
    },
    methods: {
        voltar() { this.$router.back(); },
        async fetchArvore() {
            try {
                const processoId = this.$route.params.processoId
                const resp = await api.get(`/processo/${processoId}/arvore/`)
                this.treeData = Array.isArray(resp.data.arvore)
                    ? resp.data.arvore
                    : Array.isArray(resp.data)
                        ? resp.data
                        : []
            } catch (e) {
                this.showToast("Erro ao buscar árvore.", "error")
                this.treeData = []
            }
        },
        showToast(message, type = "info") {
            if (this.$refs.toast && typeof this.$refs.toast.show === "function") {
                this.$refs.toast.show({ message, type });
            }
        },
        async persistOrder(itemizacoes, parentId) {
            try {
                await Promise.all(itemizacoes.map((item, idx) => {
                    return api.patch(`/itemizacao/${item.id}/`, {
                        ordem: idx,
                        itemSuperior: parentId
                    })
                }))
                this.showToast("Ordem atualizada com sucesso!", "success")
            } catch (e) {
                this.showToast("Erro ao atualizar ordem!", "error")
            }
        },
        onItemizacaoDrop(itemizacoes, parentId) { this.persistOrder(itemizacoes, parentId) },
        onSubItemizacaoDrop({ subitemizacoes, parentNode }) { this.persistOrder(subitemizacoes, parentNode.id) },
        openItemizacaoModal(parentNode) {
            this.novaItemizacao = { nome: '', descricao: '' }
            this.itemizacaoParent = parentNode
            this.showItemizacaoModal = true
        },
        closeItemizacaoModal() { this.showItemizacaoModal = false; },
        async confirmAddItemizacao() {
            this.showItemizacaoModal = false
            const processoId = this.$route.params.processoId
            const payload = {
                nome: this.novaItemizacao.nome,
                descricao: this.novaItemizacao.descricao,
                processo: processoId,
                itemSuperior: this.itemizacaoParent ? this.itemizacaoParent.id : null
            }
            const resp = await api.post(`/itemizacao/`, payload)
            if (this.itemizacaoParent) {
                if (!Array.isArray(this.itemizacaoParent.subitemizacoes))
                    this.itemizacaoParent.subitemizacoes = []
                this.itemizacaoParent.subitemizacoes.push(resp.data)
                this.persistOrder(this.itemizacaoParent.subitemizacoes, this.itemizacaoParent.id)
            } else {
                this.treeData.push(resp.data)
                this.persistOrder(this.treeData, null)
            }
            this.showToast("Itemização adicionada!", "success")
        },
        openTarefaModal(parentNode) {
            this.novaTarefa = { nome: '', descricao: '', ponto: 0, minimo: 0, maximo: 0 }
            this.tarefaParent = parentNode
            this.showTarefaModal = true
        },
        closeTarefaModal() { this.showTarefaModal = false; },
        async confirmAddTarefa() {
            this.showTarefaModal = false
            const processoId = this.$route.params.processoId
            const payload = {
                nome: this.novaTarefa.nome,
                descricao: this.novaTarefa.descricao,
                ponto: this.novaTarefa.ponto,
                minimo: this.novaTarefa.minimo,
                maximo: this.novaTarefa.maximo,
                processo: processoId,
                item: this.tarefaParent.id
            }
            const resp = await api.post(`/tarefa-processo/`, payload)
            if (!Array.isArray(this.tarefaParent.tarefas))
                this.tarefaParent.tarefas = []
            this.tarefaParent.tarefas.push(resp.data)
            this.showToast("Tarefa adicionada!", "success")
        },
        confirmRemoveNode(node) {
            const isItemizacao = Array.isArray(node.subitemizacoes) || Array.isArray(node.tarefas);
            this.modalConfirmacao = {
                visivel: true,
                node,
                isItemizacao,
                titulo: isItemizacao ? "Remover Itemização" : "Remover Tarefa",
                mensagem: isItemizacao
                    ? "Deseja remover esta itemização e todas as subitemizações/tarefas abaixo dela?"
                    : "Deseja remover esta tarefa?"
            }
        },
        fecharModalConfirmacao() {
            this.modalConfirmacao.visivel = false
            this.modalConfirmacao.node = null
        },
        async removerNodeConfirmado() {
            const node = this.modalConfirmacao.node
            if (this.modalConfirmacao.isItemizacao) {
                try {
                    await api.delete(`/itemizacao/${node.id}/`)
                    this.removeFromTree(this.treeData, node)
                    this.showToast("Itemização removida.", "success")
                } catch (error) {
                    let mensagem = "Erro ao excluir a itemização.";
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
                }
            } else {
                try {
                    await api.delete(`/tarefa-processo/${node.id}/`)
                    this.removeTarefaFromTree(this.treeData, node)
                    this.showToast("Tarefa removida.", "success")
                } catch (error) {
                    let mensagem = "Erro ao excluir a tarefa.";
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
                }
            }
            this.fecharModalConfirmacao()
        },
        removeFromTree(arr, node) {
            const idx = arr.findIndex(el => el.id === node.id)
            if (idx !== -1) {
                arr.splice(idx, 1)
                this.persistOrder(arr, null)
                return true
            }
            for (const item of arr) {
                if (Array.isArray(item.subitemizacoes) && this.removeFromTree(item.subitemizacoes, node)) {
                    this.persistOrder(item.subitemizacoes, item.id)
                    return true
                }
            }
            return false
        },
        removeTarefaFromTree(arr, node) {
            for (const item of arr) {
                if (Array.isArray(item.tarefas)) {
                    const idx = item.tarefas.findIndex(t => t.id === node.id)
                    if (idx !== -1) {
                        item.tarefas.splice(idx, 1)
                        return true
                    }
                }
                if (Array.isArray(item.subitemizacoes) && this.removeTarefaFromTree(item.subitemizacoes, node)) {
                    return true
                }
            }
            return false
        },
        async handleUpdateTitle({ node, title }) {
            try {
                if (Array.isArray(node.subitemizacoes) || Array.isArray(node.tarefas)) {
                    await api.patch(`/itemizacao/${node.id}/`, { nome: title });
                    node.nome = title;
                    this.showToast("Itemização renomeada!", "success");
                } else {
                    await api.patch(`/tarefa-processo/${node.id}/`, { nome: title });
                    node.nome = title;
                    this.showToast("Tarefa renomeada!", "success");
                }
            } catch (e) {
                this.showToast("Erro ao renomear.", "error");
            }
        },
        // --- EDIÇÃO ---
        openEditItemizacaoModal(node) {
            this.editItemizacaoTarget = node;
            this.editItemizacaoData = { nome: node.nome, descricao: node.descricao };
            this.showEditItemizacaoModal = true;
        },
        closeEditItemizacaoModal() {
            this.showEditItemizacaoModal = false;
        },
        async confirmEditItemizacao() {
            try {
                const { id } = this.editItemizacaoTarget;
                const payload = { ...this.editItemizacaoData };
                await api.patch(`/itemizacao/${id}/`, payload);
                Object.assign(this.editItemizacaoTarget, payload);
                this.showToast("Itemização atualizada!", "success");
            } catch (e) {
                this.showToast("Erro ao atualizar itemização.", "error");
            }
            this.closeEditItemizacaoModal();
        },
        openEditTarefaModal(node) {
            this.editTarefaTarget = node;
            this.editTarefaData = {
                nome: node.nome,
                descricao: node.descricao,
                ponto: node.ponto,
                minimo: node.minimo,
                maximo: node.maximo
            };
            this.showEditTarefaModal = true;
        },
        closeEditTarefaModal() {
            this.showEditTarefaModal = false;
        },
        async confirmEditTarefa() {
            try {
                const { id } = this.editTarefaTarget;
                const payload = { ...this.editTarefaData };
                await api.patch(`/tarefa-processo/${id}/`, payload);
                Object.assign(this.editTarefaTarget, payload);
                this.showToast("Tarefa atualizada!", "success");
            } catch (e) {
                this.showToast("Erro ao atualizar tarefa.", "error");
            }
            this.closeEditTarefaModal();
        }
    }
}
</script>

<style scoped>
.arvore-wrapper {
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 2px 5px #0001;
    padding: 22px 20px 32px 20px;
}

.arvore-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 22px;
    margin-bottom: 18px;
}

.drag-info {
    background: #e9f3ff;
    color: #195ca6;
    font-size: 0.99rem;
    margin-bottom: 14px;
    border-radius: 5px;
    padding: 7px 18px;
    border-left: 4px solid #1976d2;
    box-shadow: 0 1px 2px #0001;
}

.arvore-card {
    background: #f5f7fa;
    border-radius: 7px;
    padding: 18px 12px 10px 18px;
    min-height: 90px;
    box-shadow: 0 2px 5px #0001;
}

.arvore-lista {
    margin-top: 2px;
}

/* Espaçamento entre itemizações raiz */
.itemizacao-raiz {
    margin-bottom: 18px;
}

.itemizacao-raiz:last-child {
    margin-bottom: 0;
}

/* Modal */
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
    padding: 16px 18px 10px 18px;
    min-width: 260px;
    max-width: 96vw;
    min-height: 0;
    max-height: 86vh;
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

.modal-header h3 {
    font-size: 1.02rem;
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

.modal label {
    display: flex;
    flex-direction: column;
    margin-bottom: 8px;
    font-size: 0.98em;
}

.modal input {
    margin-top: 3px;
    padding: 3px 6px;
    font-size: 0.97em;
    border-radius: 4px;
    border: 1px solid #ddd;
    background: #fafbfc;
}

.modal-actions {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 5px;
}

.section-divider {
    border: none;
    border-top: 1px solid #eee;
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

.voltar-btn {
    background: #1976d2;
}

.voltar-btn:hover {
    background: #1251a1;
}
</style>