<template>
    <div class="usuario-form-outer">
        <div class="usuario-form-panel">
            <form class="usuario-form" @submit.prevent="handleSubmit">
                <h2 v-if="!isEditMode">Cadastrar Usuário</h2>
                <h2 v-else>Alterar Usuário</h2>
                <div class="form-field">
                    <label for="nome">Nome</label>
                    <input id="nome" v-model="form.nome" type="text" class="input-form" required />
                </div>
                <div class="form-field">
                    <label for="login">Login</label>
                    <input id="login" v-model="form.login" type="text" class="input-form" required />
                </div>
                <div class="form-field">
                    <label for="email">E-mail</label>
                    <input id="email" v-model="form.email" type="email" class="input-form" required />
                </div>
                <div class="form-field">
                    <label for="email2">Confirmar E-mail</label>
                    <input id="email2" v-model="form.email2" type="email" class="input-form" required />
                </div>
                <div class="form-field" v-if="!isEditMode">
                    <label for="password">Senha</label>
                    <input id="password" v-model="form.password" type="password" class="input-form" required />
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-acoes submit-btn" :disabled="loading">
                        <span v-if="loading">Salvando...</span>
                        <span v-else>{{ isEditMode ? 'Salvar Alterações' : 'Cadastrar' }}</span>
                    </button>
                    <button type="button" class="btn-acoes cancel-btn" @click="goBack" :disabled="loading">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
        <div class="usuario-form-divider"></div>
        <div class="usuario-form-messages">
            <div class="form-message-section">
                <div v-if="errorMessage" class="form-error">
                    {{ errorMessage }}
                </div>
                <div v-if="successMessage" class="form-success">
                    {{ successMessage }}
                    <button class="btn-acoes" @click="goBack" style="margin-left: 16px; margin-top:8px;">OK</button>
                </div>
                <div v-if="!isEditMode" class="form-info">
                    <span>
                        Após o cadastro, você receberá um e-mail para confirmar sua conta. Seu cadastro ficará pendente
                        até
                        a confirmação do e-mail.
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from "@/services/api";

export default {
    name: "UsuarioForm",
    data() {
        return {
            form: {
                nome: "",
                login: "",
                email: "",
                email2: "",
                password: "",
            },
            loading: false,
            errorMessage: "",
            successMessage: "",
            isEditMode: false,
            usuarioId: null,
        };
    },
    mounted() {
        this.usuarioId = this.$route.params.id || null;
        if (this.usuarioId) {
            this.isEditMode = true;
            this.fetchUsuario();
        }
    },
    methods: {
        async fetchUsuario() {
            this.loading = true;
            this.errorMessage = "";
            try {
                const { data } = await api.get(`/usuario/${this.usuarioId}/`);
                this.form.nome = data.first_name || "";
                this.form.login = data.username || "";
                this.form.email = data.email || "";
                this.form.email2 = data.email || "";
            } catch (e) {
                this.errorMessage = "Erro ao carregar dados do usuário.";
            } finally {
                this.loading = false;
            }
        },
        async handleSubmit() {
            this.errorMessage = "";
            this.successMessage = "";
            if (this.form.email !== this.form.email2) {
                this.errorMessage = "Os e-mails não coincidem.";
                return;
            }
            if (!this.isEditMode && !this.form.password) {
                this.errorMessage = "A senha é obrigatória.";
                return;
            }
            this.loading = true;
            try {
                if (this.isEditMode) {
                    await api.put(`/usuario/${this.usuarioId}/`, {
                        username: this.form.login,
                        first_name: this.form.nome,
                        email: this.form.email,
                        email2: this.form.email2,
                    });
                    this.successMessage = "Usuário alterado com sucesso.";
                    setTimeout(() => {
                        this.goBack();
                    }, 2000);
                } else {
                    await api.post("/usuario/", {
                        username: this.form.login,
                        first_name: this.form.nome,
                        email: this.form.email,
                        email2: this.form.email2,
                        password: this.form.password,
                    });
                    this.successMessage = "Usuário cadastrado com sucesso. Verifique seu e-mail para confirmar o cadastro!";
                    this.form = { nome: "", login: "", email: "", email2: "", password: "" };
                    // Não chama goBack automaticamente, espera o usuário clicar em OK
                }
            } catch (e) {
                if (e.response && e.response.data) {
                    const errors = e.response.data;
                    this.errorMessage = Object.values(errors).flat().join(" ");
                } else {
                    this.errorMessage = "Erro ao salvar usuário.";
                }
            } finally {
                this.loading = false;
            }
        },
        goBack() {
            this.$router.back();
        },
    },
};
</script>

<style scoped>
.usuario-form-outer {
    display: flex;
    align-items: flex-start;
    margin-top: 32px;
    margin-left: 32px;
}

.usuario-form-panel {
    min-width: 320px;
    background: #fff;
    border-radius: 6px 0 0 6px;
    box-shadow: 0 2px 5px #0001;
    padding: 18px 20px 20px 20px;
    /* Menos padding */
    display: flex;
    flex-direction: column;
    gap: 0;
}

.usuario-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    /* Menor espaçamento entre campos */
}

.usuario-form-divider {
    width: 1px;
    background: #e1e1e1;
    height: 100%;
    min-height: 320px;
    margin: 0 24px;
    /* Menos espaço lateral */
}

.usuario-form-messages {
    min-width: 240px;
    max-width: 320px;
    display: flex;
    align-items: flex-start;
    padding-top: 14px;
}

.form-message-section {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
    /* Menor gap */
}

h2 {
    font-size: 1.08rem;
    color: #12366e;
    letter-spacing: 1px;
    text-align: left;
    font-weight: 700;
    margin-bottom: 15px;
    margin-top: 0;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 2px;
    /* Menor gap label/input */
    margin-bottom: 0;
    /* Remove margem extra */
}

.form-field label {
    color: #1f3c74;
    font-weight: 600;
    font-size: 0.97rem;
    margin-bottom: 1px;
}

.input-form {
    padding: 6px 10px;
    /* Menos padding */
    border: 1.2px solid #e6e8f0;
    border-radius: 4px;
    background: #fafbfc;
    color: #26334d;
    font-size: 0.96rem;
    outline: none;
    transition: border-color 0.18s;
}

.input-form:focus {
    border-color: #0075ff;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    /* Menos gap nos botões */
    margin-top: 4px;
}

.btn-acoes {
    padding: 5px 13px;
    background: #0075ff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.18s;
}

.btn-acoes:disabled {
    background: #e0e0e0;
    color: #aaa;
    cursor: not-allowed;
}

.btn-acoes:hover:enabled {
    background: #0050a4;
}

.submit-btn {
    background: #14b714;
}

.submit-btn:hover:enabled {
    background: #0e860e;
}

.cancel-btn {
    background: #d92424;
}

.cancel-btn:hover:enabled {
    background: #a50d0d;
}

.form-error {
    margin-top: 7px;
    color: #c00;
    background: #fff4f4;
    border: 1px solid #fbcaca;
    border-radius: 5px;
    padding: 8px 10px;
    text-align: center;
    font-size: 0.95rem;
    font-weight: 500;
}

.form-success {
    margin-top: 7px;
    color: #14b714;
    background: #f4fff4;
    border: 1px solid #caffca;
    border-radius: 5px;
    padding: 8px 10px;
    text-align: center;
    font-size: 0.95rem;
    font-weight: 500;
}

.form-success .btn-acoes {
    background: #0075ff;
    color: #fff;
    margin-left: 14px;
    margin-top: 6px;
    font-size: 0.93rem;
    padding: 4px 10px;
}

.form-info {
    margin-top: 4px;
    color: #333;
    font-size: 0.93rem;
    background: #f5f7fa;
    border-radius: 5px;
    padding: 10px 10px 10px 10px;
    text-align: left;
    border-left: 4px solid #0075ff;
}

@media (max-width: 900px) {
    .usuario-form-outer {
        flex-direction: column;
        margin-left: 0;
        margin-top: 12px;
    }

    .usuario-form-divider {
        display: none;
    }

    .usuario-form-messages {
        padding-top: 12px;
        padding-left: 0;
        margin-left: 0;
    }

    .usuario-form-panel {
        border-radius: 6px 6px 0 0;
        padding: 12px 8px 12px 8px;
    }
}
</style>