import { createRouter, createWebHistory } from 'vue-router';
import ProcessoList from '@/pages/admin/ProcessoList.vue';
import ProcessoForm from '@/pages/admin/ProcessoForm.vue';
import UsuarioProcessoList from '@/pages/admin/UsuarioProcessoList.vue';
import UsuarioProcessoForm from '@/pages/admin/UsuarioProcessoForm.vue';
import UsuarioProcessoDocs from '@/pages/admin/UsuarioProcessoDocs.vue';
import ItemizacaoTarefaTree from '@/pages/admin/ItemizacaoTarefaTree.vue';
import ListarUsuarios from '@/pages/admin/UsuarioList.vue';
import Home from '@/pages/Home.vue';
import UsuarioUserForm from '@/pages/user/UsuarioForm.vue';
import UsuarioProcessoUser from '@/pages/user/UsuarioProcessoList.vue';
import UsuarioProcessoDocsUser from '@/pages/user/UsuarioProcessoDocs.vue';
import AtivarConta from '@/components/AtivarConta.vue';

const routes = [
  { path: '/', component: Home },
  { //HOME
    path: '/home',
    name: 'Home',
    component: Home,
  },
  //PROCESSO ADM, LISTAR, NOVO, EDITAR
  {
    path: "/processo",
    name: "ListarProcesso",
    component: ProcessoList,
  },
  {
    path: "/processo/novo",
    name: "NovoProcesso",
    component: ProcessoForm,
  },
  {
    path: "/processo/editar/:id",
    name: "EditarProcesso",
    component: ProcessoForm,
    props: true,
  },
  {
    path: '/processo/:processoId/arvore',
    name: 'ItemizacaoTarefaTree',
    component: ItemizacaoTarefaTree,
    props: true
  },
  //USUARIO PROCESSO ADM, LISTAR, NOVO, EDITAR
  {
    path: "/usuario-processo",
    name: "ListarUsuarioProcesso",
    component: UsuarioProcessoList,
  },
  {
    path: "/usuario-processo/novo",
    name: "NovoUsuarioProcesso",
    component: UsuarioProcessoForm,
  },
  {
    path: "/usuario-processo/editar/:id",
    name: "EditarUsuarioProcesso",
    component: UsuarioProcessoForm,
    props: true,
  },
  {
    path: "/usuario-processo-docs",
    name: "DocsUsuarioProcesso",
    component: UsuarioProcessoDocs,
  },
  //USUARIO USER, NOVO, EDITAR
  {
    path: "/usuario-user/novo",
    name: "NovoUsuarioUser",
    component: UsuarioUserForm,
  },
  {
    path: "/usuario-user/editar/:id",
    name: "EditarUsuarioUser",
    component: UsuarioUserForm,
    props: true,
  }, 
  //USUARIO PROCESSO USER, LISTAR E ENVIAR DOCUMENTOS
  {
    path: "/usuario-processo-user",
    name: "ListarUsuarioProcessoUser",
    component: UsuarioProcessoUser,
  },
  {
    path: "/usuario-processo-docs-user",
    name: "DocsUsuarioProcessoUser",
    component: UsuarioProcessoDocsUser,
  },
  //USUARIO - ATIVAR CONTA
  {
    path: '/ativar-conta/:uid/:token',
    name: 'AtivarConta',
    component: AtivarConta
  },
  {
    path: '/activate/:uidb64/:token',
    name: 'ActivateUser',
    component: AtivarConta,
    props: true
  },
  {
    path: '/user',
    name: 'ListarUsuarios',
    component: ListarUsuarios,
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Verifica se a rota requer autenticação e se o usuário está autenticado
    if (!localStorage.getItem('access_token')) {
      next('/login'); // Redireciona para a página de login se não estiver autenticado
    } else {
      next(); // Permite a navegação se autenticado
    }
  } else {
    next(); // Permite a navegação para rotas públicas
  }
});

export default router;
