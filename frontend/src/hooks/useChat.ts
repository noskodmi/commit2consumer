import { useState } from 'react';
import { chatApi, ChatResponse } from '@/lib/api';
import toast from 'react-hot-toast';

export const useChat = () => {
  const [loading, setLoading] = useState(false);

  const sendMessage = async (
    repoId: string, 
    content: string, 
    conversationId?: string
  ): Promise<ChatResponse | null> => {
    setLoading(true);
    try {
      const response = await chatApi.sendMessage(repoId, content, conversationId);
      return response;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send message');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { sendMessage, loading };
};