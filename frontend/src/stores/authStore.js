import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: !!localStorage.getItem('access_token'),
    username: localStorage.getItem('username') || '',
  }),
  actions: {
    login(username) {
      this.isAuthenticated = true;
      this.username = username;
    },
    logout() {
      this.isAuthenticated = false;
      this.username = '';
    },
    syncFromStorage() {
      this.isAuthenticated = !!localStorage.getItem('access_token');
      this.username = localStorage.getItem('username') || '';
    }
  }
});