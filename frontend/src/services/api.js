import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (message, sessionId = null) => {
    try {
      const response = await api.post('/chat/', {
        message,
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  getSuggestedQuestions: async (count = 3) => {
    try {
      const response = await api.get(`/suggested-questions/?count=${count}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching suggested questions:', error);
      throw error;
    }
  },

  getConversationHistory: async (sessionId) => {
    try {
      const response = await api.get(`/conversations/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      throw error;
    }
  },

  getAllConversations: async () => {
    try {
      const response = await api.get('/conversations/');
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  deleteConversation: async (sessionId) => {
    try {
      const response = await api.delete(`/conversations/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },

  deleteAllConversations: async () => {
    try {
      const response = await api.delete('/conversations/delete-all/');
      return response.data;
    } catch (error) {
      console.error('Error deleting all conversations:', error);
      throw error;
    }
  },

  ingestData: async (source = 'initial') => {
    try {
      const response = await api.post('/ingest-data/', { source });
      return response.data;
    } catch (error) {
      console.error('Error ingesting data:', error);
      throw error;
    }
  },

  healthCheck: async () => {
    try {
      const response = await api.get('/health/');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },
};

export default api;

