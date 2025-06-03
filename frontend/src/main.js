import './assets/main.css'

import { createApp, h } from 'vue'; // Certifique-se de que o nome do pacote está correto.
import App from './App.vue';
import router from './router'; // Adiciona o roteador.
import { createPinia } from 'pinia'

const app = createApp(App);

app.use(createPinia())
app.use(router);
app.mount('#app');
