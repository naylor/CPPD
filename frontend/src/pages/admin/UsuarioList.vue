<template>
    <div>
        <!-- Mensagem de autenticação -->
        <div v-if="!isAuthenticated" class="auth-message">
            <p>Por favor, faça login para acessar os usuários.</p>
        </div>

        <!-- Conteúdo principal -->
        <div v-if="isAuthenticated" class="padrao-list">
            <div class="header-actions">
                <h1>Lista de Usuários</h1>
            </div>
            <div v-if="usuarios.length > 0" class="table-wrapper">
                <table class="usuario-processos-table">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Usuário</th>
                            <th>Email</th>
                            <th>Ativo?</th>
                            <th>Membro da equipe?</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="usuario in usuarios" :key="usuario.id">
                            <td>
                                <span class="processo-nome" :title="usuario.first_name || usuario.username">
                                    {{ usuario.first_name || usuario.username }}
                                </span>
                            </td>
                            <td>{{ usuario.username }}</td>
                            <td>{{ usuario.email }}</td>
                            <td>
                                <input type="checkbox" :checked="usuario.is_active" @change="toggleAtivo(usuario)"
                                    :disabled="usuario.id === userIdAtual" title="Ativar/desativar usuário" />
                            </td>
                            <td>
                                <input type="checkbox" :checked="usuario.is_staff" @change="toggleEquipe(usuario)"
                                    :disabled="usuario.id === userIdAtual" title="Tornar/remover membro da equipe" />
                            </td>
                            <td>
                                <div class="actions-container">
                                    <button class="btn-acoes icon-btn delete-btn" title="Excluir"
                                        @click="abrirModalExcluir(usuario.id)" :disabled="usuario.id === userIdAtual">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="none"
                                            stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                            stroke-linejoin="round" viewBox="0 0 24 24">
                                            <polyline points="3 6 5 6 21 6" />
                                            <path
                                                d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m5 0V4a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v2" />
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
                <p>Nenhum usuário encontrado.</p>
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
                    <p>Tem certeza que deseja excluir esse usuário?</p>
                </div>
                <div class="modal-actions">
                    <button class="btn-acoes salvar-btn" @click="confirmarExcluirUsuario">
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
    components: { Toast },
    data() {
        return {
            usuarios: [],
            isAuthenticated: !!localStorage.getItem('access_token'),
            showConfirmModal: false,
            usuarioParaExcluir: null,
            userIdAtual: null,
        };
    },
    methods: {
        async fetchUsuarios() {
            try {
                const response = await api.get("/usuario/");
                // Se for paginado, ajuste para response.data.results
                let lista = Array.isArray(response.data.results)
                    ? response.data.results.filter(u => u && u.id)
                    : response.data.filter(u => u && u.id);
                this.usuarios = lista;
            } catch (error) {
                this.showToast("Erro ao carregar os usuários.", "error");
                console.error("Erro ao carregar os usuários:", error);
            }
        },
        abrirModalExcluir(id) {
            this.usuarioParaExcluir = id;
            this.showConfirmModal = true;
        },
        fecharModalExcluir() {
            this.showConfirmModal = false;
            this.usuarioParaExcluir = null;
        },
        async confirmarExcluirUsuario() {
            try {
                await api.delete(`/usuario/${this.usuarioParaExcluir}/`);
                this.showToast("Usuário excluído com sucesso!", "success");
                this.fetchUsuarios();
            } catch (error) {
                this.showToast(error, "error");
            }
            this.fecharModalExcluir();
        },
        async toggleAtivo(usuario) {
            try {
                await api.patch(`/usuario/${usuario.id}/`, { is_active: !usuario.is_active });
                usuario.is_active = !usuario.is_active;
                this.showToast(`Usuário ${usuario.is_active ? 'ativado' : 'desativado'} com sucesso!`, "success");
            } catch (error) {
                this.showToast("Erro ao alterar status do usuário.", "error");
                console.error("Erro ao alterar usuário:", error);
            }
        },
        async toggleEquipe(usuario) {
            try {
                await api.patch(`/usuario/${usuario.id}/`, { is_staff: !usuario.is_staff });
                usuario.is_staff = !usuario.is_staff;
                this.showToast(`Usuário ${usuario.is_staff ? 'agora é membro da equipe' : 'não é mais membro da equipe'}.`, "success");
            } catch (error) {
                this.showToast("Erro ao alterar tipo de usuário.", "error");
                console.error("Erro ao alterar tipo de usuário:", error);
            }
        },
        showToast(message, type = "info") {
            if (this.$refs.toast && typeof this.$refs.toast.show === "function") {
                this.$refs.toast.show({ message, type });
            }
        },
        getCurrentUserId() {
            // Supondo que você armazene o ID do usuário logado no localStorage (ajuste se usar outro método)
            const payload = localStorage.getItem('user_id');
            if (payload) return parseInt(payload);
            return null;
        }
    },
    mounted() {
        if (this.isAuthenticated) {
            this.fetchUsuarios();
            this.userIdAtual = this.getCurrentUserId();
        }
    }
};
</script>

<style scoped>
/* O mesmo CSS do ProcessoList.vue, aproveite tudo para manter o padrão visual. */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 3000;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
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
    gap: 12px;
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