import axios from 'axios';
const API_URL = 'http://localhost:8000/';

const API_URL_TOKEN = `${API_URL}/token/`

export const login = async (username, password) => {
  try {
    const response = await axios.post(API_URL_TOKEN, { username, password });
    const { access, refresh, userId , is_staff} = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('userId', userId);
    localStorage.setItem("isStaff", is_staff);
    return { access, refresh, userId };
  } catch (error) {
    if (
      error.response &&
      error.response.data &&
      (error.response.data.error === 'not_activated' ||
       error.response.data.detail === 'Usuário não ativado')
    ) {
      return { error: 'not_activated' };
    }
    throw new Error('Login falhou. Verifique suas credenciais.');
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Função para reenviar link de ativação
export const resendActivationLink = async (username) => {
  try {
    const response = await axios.post(`${API_URL}resend-activation/`, { username });
    if (response.data && response.data.detail === "Usuário já está ativado.") {
      // Retorne um status ou mensagem diferente para o frontend tratar
      return { alreadyActivated: true };
    }
    return { success: true };
  } catch (error) {
    throw new Error('Erro ao reenviar o link de ativação.');
  }
};

export const changePassword = async (username, currentPassword, newPassword) => {
  try {
    const accessToken = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_URL}change-password/`,
      {
        username,
        current_password: currentPassword,
        new_password: newPassword
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    // Sucesso esperado: { success: true } ou { detail: "Senha alterada com sucesso" }
    return response.data;
  } catch (error) {
    // Mensagem de erro amigável
    let msg = "Erro ao alterar senha. Tente novamente.";
    if (error.response && error.response.data && error.response.data.detail) {
      msg = error.response.data.detail;
    } else if (error.response && error.response.data && error.response.data.error) {
      msg = error.response.data.error;
    }
    const err = new Error(msg);
    err.response = error.response;
    throw err;
  }
};