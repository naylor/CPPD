<template>
  <div class="padrao-form">
    <h1>{{ isEditing ? 'Editar' : 'Criar' }} Usuário Processo</h1>
    <form @submit.prevent="salvarUsuarioProcesso">
      <!-- Campo para selecionar o usuário -->
      <div class="form-group">
        <label for="usuario">Usuário</label>
        <select v-model="usuarioProcesso.usuario" id="usuario" required>
          <option v-for="usuario in usuarios" :key="usuario.id" :value="usuario.id">{{ usuario.nome }}</option>
        </select>
      </div>

      <!-- Campo para selecionar o processo -->
      <div class="form-group">
        <label for="processo">Processo</label>
        <select v-model="usuarioProcesso.processo" id="processo" required>
          <option v-for="processo in processos" :key="processo.id" :value="processo.id">{{ processo.nome }}</option>
        </select>
      </div>

      <!-- Campo para o valor de submetido -->
      <div class="form-group">
        <label for="submetido">Submetido</label>
        <input type="number" v-model="usuarioProcesso.submetido" id="submetido" required />
      </div>

      <!-- Campo para o status -->
      <div class="form-group">
        <label for="status">Status</label>
        <input type="text" v-model="usuarioProcesso.status" id="status" required />
      </div>

      <!-- Botão para salvar -->
      <div class="form-group">
        <button type="submit" class="btn">{{ usuarioProcesso.id ? 'Salvar' : 'Criar' }}</button>
      </div>
    </form>

    <!-- Carregando -->
    <div v-if="loading" class="loading">
      <p>Salvando...</p>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  inheritAttrs: false,
  data() {
    return {
      isEditing: false,
      usuarioProcesso: {
        usuario: '',
        processo: '',
        submetido: '',
        status: ''
      },
      usuarios: [],
      processos: [],
      loading: false
    };
  },
  methods: {
    async fetchUsuarios() {
      try {
        const response = await api.get('/usuarios');
        this.usuarios = response.data;
      } catch (error) {
        console.error("Erro ao carregar os usuários:", error);
      }
    },
    async fetchProcessos() {
      try {
        const response = await api.get('/processos');
        this.processos = response.data;
      } catch (error) {
        console.error("Erro ao carregar os processos:", error);
      }
    },
    async salvarUsuarioProcesso() {
      this.loading = true;
      try {
        if (this.isEditing) {
          // Edição
          await api.put(`/usuario-processo/${this.usuarioProcesso.id}/`, this.usuarioProcesso);
        } else {
          // Criação
          await api.post('/usuario-processo/', this.usuarioProcesso);
        }
        this.$router.push({ name: 'ListarUsuarioProcesso' });
      } catch (error) {
        console.error("Erro ao salvar usuário e processo:", error);
      } finally {
        this.loading = false;
      }
    },
    async carregarUsuarioProcesso() {
      if (this.$route.params.id) {
        this.isEditing = true;
        try {
          const response = await api.get(`/usuario-processo/${this.$route.params.id}/`);
          this.usuarioProcesso = response.data;
        } catch (error) {
          console.error("Erro ao carregar usuário e processo:", error);
        }
      }
    }
  },
  mounted() {
    this.fetchUsuarios();
    this.fetchProcessos();
    if (this.$route.params.id) {
      this.carregarUsuarioProcesso();
    }
  }
};
</script>

<style scoped></style>