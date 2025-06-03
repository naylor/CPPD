<template>
    <div class="ativar-conta-page">
        <div v-if="status === 'success'" class="ativacao-msg success">
            <h2>Conta ativada com sucesso!</h2>
            <p>Sua conta foi ativada. Agora você pode acessar normalmente.</p>
        </div>
        <div v-else-if="status === 'error'" class="ativacao-msg error">
            <h2>Erro na ativação</h2>
            <p>{{ errorMsg }}</p>
        </div>
        <div v-else class="ativacao-msg">
            <p>Validando seu link de ativação...</p>
        </div>
    </div>
</template>

<script>
import api from "@/services/api";
export default {
    name: "AtivarConta",
    data() {
        return {
            status: "", // '', 'success', 'error'
            errorMsg: "",
        };
    },
    async mounted() {
        // Suporta tanto /ativar-conta/:uid/:token quanto /activate/:uidb64/:token
        const { uid, uidb64, token } = this.$route.params;
        const userId = uid || uidb64;
        try {
            await api.get(`/activate/${userId}/${token}/`);
            this.status = "success";
        } catch (e) {
            this.status = "error";
            this.errorMsg =
                e.response?.data?.detail ||
                "Falha na ativação da conta. O link pode estar expirado ou inválido.";
        }
    },
};
</script>

<style scoped>
.ativar-conta-page {
    min-height: 100vh;
    height: 100vh;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
}

.ativacao-msg {
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 2px 5px #0001;
    padding: 2rem 2.5rem;
    text-align: left;
    min-width: 320px;
    max-width: 95vw;
    margin: 32px 0 0 32px;
}

.ativacao-msg.success h2 {
    color: #14b714;
}

.ativacao-msg.error h2 {
    color: #c00;
}

.ativacao-msg p {
    font-size: 1.08rem;
    margin-top: 1rem;
}
</style>