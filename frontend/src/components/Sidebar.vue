<script>
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'Sidebar',
  computed: {
    authStore() {
      return useAuthStore();
    },
    isStaff() {
      return this.authStore.isAuthenticated && (localStorage.getItem('isStaff') === 'true');
    },
    isUser() {
      return this.authStore.isAuthenticated && localStorage.getItem('userId');
    }
  }
};
</script>

<template>
  <div class="sidebar">
    <ul>
      <li>
        <router-link :to="{ name: 'Home' }">Home</router-link>
      </li>

      <!-- Apenas para Staff -->
      <li class="menu-item" v-if="isStaff">
        <b>Admin</b>
        <ul class="submenu">
          <li>
            <router-link :to="{ name: 'ListarProcesso' }">Processos</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'ListarUsuarioProcesso' }">Processos dos Usuários</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'ListarUsuarios' }">Usuários</router-link>
          </li>
        </ul>
      </li>

      <!-- Sempre visível -->
      <li class="menu-item">
        <b>User</b>
        <ul class="submenu">
          <li>
            <router-link :to="{ name: 'Home' }">Processos</router-link>
          </li>
          <li v-if="isUser">
            <router-link :to="{ name: 'ListarUsuarioProcessoUser' }">Meus Processos</router-link>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<style>
.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 20px;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin: 10px 0;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

.sidebar li a {
  text-decoration: none;
  color: #333;
  font-weight: bold;
  display: block;
}

.sidebar li a:hover {
  color: #f44336;
}

.submenu {
  padding-left: 20px;
  margin-top: 5px;
}

.submenu li {
  margin: 5px 0;
  padding-left: 20px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

.menu-item>b {
  color: #007bff;
  font-weight: bold;
  font-size: 16px;
}
</style>