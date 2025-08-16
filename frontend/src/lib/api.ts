import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Types
export interface Repository {
  id: string;
  name: string;
  full_name: string;
  url: string;
  description?: string;
  language?: string;
  stars: number;
  forks: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processed_at?: string;
  error_message?: string;
  document_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  context_used?: any[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

export interface ChatResponse {
  answer: string;
  conversation_id: string;
  sources: string[];
  suggested_questions?: string[];
}

// API functions
export const repositoryApi = {
  submit: async (url: string, name?: string) => {
    const response = await api.post('/repositories/', { url, name });
    return response.data;
  },

  list: async (params?: { skip?: number; limit?: number; status?: string }) => {
    const response = await api.get('/repositories/', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(`/repositories/${id}`);
    return response.data;
  },

  getFiles: async (id: string, params?: { skip?: number; limit?: number; language?: string }) => {
    const response = await api.get(`/repositories/${id}/files`, { params });
    return response.data;
  },

  getDocumentation: async (id: string) => {
    const response = await api.get(`/repositories/${id}/documentation`);
    return response.data;
  },

  getFaq: async (id: string) => {
    const response = await api.get(`/repositories/${id}/faq`);
    return response.data;
  },

  search: async (id: string, query: string, limit = 5) => {
    const response = await api.get(`/search/${id}`, { params: { query, limit } });
    return response.data;
  },
};

export const chatApi = {
  sendMessage: async (repoId: string, content: string, conversationId?: string) => {
    const response = await api.post(`/repositories/${repoId}/chat`, {
      content,
      conversation_id: conversationId
    });
    return response.data;
  },

  getConversations: async (repoId: string, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/repositories/${repoId}/conversations`, { params });
    return response.data;
  },

  getMessages: async (conversationId: string, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/conversations/${conversationId}/messages`, { params });
    return response.data;
  },
};