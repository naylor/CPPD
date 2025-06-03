<template>
    <div :class="['tree-node', { 'has-parent': nivel > 0 }]" :style="indentStyle">
        <div class="tree-content">
            <span>
                {{ node.nome }}
                <button class="rename-btn" @click="$emit('editItemizacao', node)" title="Editar">✏️</button>
            </span>
            <span class="tree-actions">
                <button class="btn-arvore" @click="$emit('addItemizacao', node)">+I</button>
                <button class="btn-arvore" @click="$emit('addTarefa', node)">+T</button>
                <button class="btn-arvore delete-btn" @click="$emit('removeNode', node)">🗑️</button>
            </span>
        </div>
        <!-- Subitemizações -->
        <div v-if="node.subitemizacoes && node.subitemizacoes.length > 0">
            <draggable v-model="node.subitemizacoes" :group="{ name: 'tree', pull: true, put: true }" item-key="id"
                animation="200" @end="emitOrdemChanged">
                <template #item="{ element }">
                    <div class="subitemizacao-separador">
                        <TreeNode :node="element" :nivel="nivel + 1" @addItemizacao="$emit('addItemizacao', $event)"
                            @addTarefa="$emit('addTarefa', $event)" @removeNode="$emit('removeNode', $event)"
                            @updateTitle="$emit('updateTitle', $event)" @ordemChanged="$emit('ordemChanged', $event)"
                            @editItemizacao="$emit('editItemizacao', $event)"
                            @editTarefa="$emit('editTarefa', $event)" />
                    </div>
                </template>
            </draggable>
        </div>
        <!-- Tarefas -->
        <div v-if="node.tarefas && node.tarefas.length > 0" class="tarefas-indent" :style="indentStyle">
            <ul class="tarefas-list">
                <li v-for="t in node.tarefas" :key="t.id || t.nome">
                    <span>
                        <span class="tarefa">{{ t.nome }}</span>
                        <button class="rename-btn" @click="$emit('editTarefa', t)" title="Editar">✏️</button>
                    </span>
                    <button class="btn-arvore delete-btn" @click="$emit('removeNode', t)">🗑️</button>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'

const props = defineProps({
    node: Object,
    nivel: { type: Number, default: 0 }
})
const emit = defineEmits(['addItemizacao', 'addTarefa', 'removeNode', 'updateTitle', 'ordemChanged', 'editItemizacao', 'editTarefa'])

const indentStyle = computed(() =>
    props.nivel > 0
        ? { marginLeft: `${props.nivel * 32}px`, position: 'relative' }
        : {}
)

function setParents() {
    if (props.node.subitemizacoes) {
        props.node.subitemizacoes.forEach(child => child._parent = props.node)
    }
    if (props.node.tarefas) {
        props.node.tarefas.forEach(t => t._parent = props.node)
    }
}
onMounted(setParents)
watch(() => props.node.subitemizacoes, setParents)
watch(() => props.node.tarefas, setParents)

// Emite a ordem das subitemizações para o componente pai persistir no backend
function emitOrdemChanged() {
    emit('ordemChanged', { subitemizacoes: props.node.subitemizacoes, parentNode: props.node })
}
</script>

<style scoped>
.tree-node {
    border-left: 2px solid #c0c0c0;
    padding-left: 18px;
    margin-top: 6px;
    position: relative;
}

.tree-node.has-parent {
    border-left: 2.5px solid #a0a0a0;
}

.subitemizacao-separador {
    margin-bottom: 12px;
}

.subitemizacao-separador:last-child {
    margin-bottom: 0;
}

.tree-content {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 32px;
    font-size: 1.05em;
}

.tarefas-indent {
    border-left: 2px solid #c0c0c0;
    padding-left: 18px;
    margin-top: 2px;
}

.tarefas-list {
    list-style: none;
    margin: 0 0 0 0;
    padding: 0;
}

.tarefas-list li {
    min-height: 28px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tarefa {
    color: #43a047;
}

.tree-actions .btn-arvore {
    margin-left: 3px;
    font-size: 0.95em;
    background: #e0e0e0;
    border: none;
    border-radius: 3px;
    padding: 3px 6px;
    cursor: pointer;
    color: #1976d2;
    transition: background 0.16s;
}

.tree-actions .btn-arvore:hover {
    background: #bdbdbd;
    color: #0d3a70;
}

.delete-btn {
    color: #d92424 !important;
    background: #f9e0e0 !important;
}

.delete-btn:hover {
    background: #e8bdbd !important;
    color: #a50d0d !important;
}

.rename-btn {
    background: none;
    border: none;
    cursor: pointer;
    margin-left: 5px;
    color: #aaa;
    font-size: 0.95em;
}

.rename-btn:hover {
    color: #1976d2;
}

input {
    font-size: 1em;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 2px 6px;
}
</style>