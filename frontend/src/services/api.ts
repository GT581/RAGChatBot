import axios from 'axios';
import { ChatSession, Message } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createSession = async (userId: string): Promise<ChatSession> => {
  const response = await api.post(`/chat/sessions/?user_id=${userId}`);
  return response.data;
};

export const getUserSessions = async (userId: string): Promise<ChatSession[]> => {
  const response = await api.get(`/chat/sessions/${userId}`);
  return response.data;
};

export const getChatHistory = async (sessionId: string): Promise<Message[]> => {
  const response = await api.get(`/chat/sessions/${sessionId}/messages`);
  return response.data;
};

export const sendMessage = async (sessionId: string, content: string): Promise<Message[]> => {
  const response = await api.post(`/chat/sessions/${sessionId}/messages`, { content });
  return response.data;
};

export const uploadFile = async (formData: FormData, sessionId: string): Promise<any> => {
  const response = await api.post(`/ingest/upload?session_id=${sessionId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/chat/sessions/${sessionId}`);
}; 