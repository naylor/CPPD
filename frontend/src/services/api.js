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
      
      alert("Faça o login novamente!");
      
      window.location.reload();
      console.log('Erro 401: Não autorizado');
      // Aqui você pode adicionar lógica para redirecionar o usuário para login ou qualquer outra ação
    }

    // Se necessário, pode retornar o erro para que ele seja tratado em outros lugares
    return Promise.reject(error);
  }
);
export default axiosInstance;
