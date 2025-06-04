import axios from 'axios';

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  const envPort = import.meta.env.VITE_API_PORT;

  if (envUrl) {
    return envPort ? `${envUrl}:${envPort}` : envUrl;
  }

  const { protocol, hostname } = window.location;

  // Fallback: localhost + porta padrão
  const defaultPort = '8000';
  const port = envPort || defaultPort;

  return `${protocol}//${hostname}:${port}`;
};

const API_URL = getBaseUrl();

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adicionar o token no cabeçalho para todas as requisições
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Adicionar o interceptor de resposta
axiosInstance.interceptors.response.use(
  (response) => {
    // Se a resposta for bem-sucedida, retorne ela normalmente
    return response;
  },
  (error) => {
    // Verificar se o erro é devido a status 401 Unauthorized
    if (error.response && error.response.status === 401 ||
      error.response && error.response.status === 400
    ) {
      localStorage.removeItem("userId");
      localStorage.removeItem("username");
      localStorage.removeItem('access_token');
      
      //alert("Faça o login novamente!");
      if (error.response && error.response.data.username[0].includes('já existe')) {
        return Promise.reject("Este nome de usuário já está em uso. Tente outro.");
      } else {
        return Promise.reject("Erro ao cadastrar usuário.", "error");
      }
      //window.location.reload();
    }
    if (error.response && error.response.status === 403) {
      return Promise.reject(error.response.data.detail || "Acesso negado. Você não tem permissão para acessar este recurso.");
    }
    if (error.response && error.response.status === 500) {
      return Promise.reject("Usuário criado, porém o Serviço de E-mail não está funcionando para envio do link de ativação. Entre em contato com o administrador do sistema.");
    }
    console.error("Erro inesperado:", error.response || error.message);
    return Promise.reject("Erro inesperado. Tente novamente mais tarde.");
  }
);
export default axiosInstance;
