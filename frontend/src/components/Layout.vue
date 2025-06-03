<template>
  <div class="layout">
    <!-- Header -->
    <Header @logout="handleLogout" />

    <!-- Corpo principal -->
    <div class="main">
      <!-- Sidebar -->
      <SidebarComponent />

      <!-- Conteúdo da página -->
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import SidebarComponent from "@/components/Sidebar.vue";

export default {
  components: {
    Header,
    SidebarComponent,
  },
  methods: {
    handleLogout() {
      this.$router.push({ name: 'Home' });
    },
  },
};
</script>

<style>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main {
  display: flex;
  flex: 1;
  margin-top: 80px;
  /* Ajusta o espaço para o header fixo */
  padding-left: 250px;
  /* Dá espaço para o sidebar fixo */
}

.sidebar {
  position: fixed;
  /* Sidebar fixo à esquerda */
  top: 80px;
  /* Espaço para o header fixo */
  left: 0;
  width: 250px;
  /* Largura do sidebar */
  background-color: #f4f4f4;
  padding: 20px;
  height: calc(100vh - 80px);
  /* Garante que o sidebar ocupe a altura restante da tela */
  z-index: 999;
  /* Sidebar deve ficar abaixo do header */
}

.content {
  flex: 1;
  padding: 20px;
  background-color: #fff;
  overflow-y: auto;
  /* Permite rolagem no conteúdo */
  width: 70vw;
  /* Largura do sidebar */

}
</style>
