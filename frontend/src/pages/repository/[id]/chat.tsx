import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import ChatInterface from '@/components/ChatInterface';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useRepository } from '@/hooks/useRepositories';
import { ChatMessage, chatApi } from '@/lib/api';
import useSWR from 'swr';

export default function ChatPage() {
  const router = useRouter();
  const { id } = router.query;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string>();
  
  const { repository, loading: repoLoading } = useRepository(id as string);

  // Load suggested questions when repository is ready
  const { data: suggestedQuestions } = useSWR(
    repository?.status === 'completed' ? `suggested-questions-${id}` : null,
    async () => {
      // This would call the RAG service to get suggested questions
      // For now, return some default questions
      return [
        'What is the main purpose of this repository?',
        'How do I set up and run this project?',
        'What are the key components or modules?',
        'What dependencies does this project have?',
        'How does the authentication work?'
      ];
    }
  );

  const handleNewMessage = (message: ChatMessage, conversationId: string) => {
    setMessages(prev => [...prev, message]);
    setCurrentConversationId(conversationId);
  };

  if (repoLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <LoadingSpinner size="lg" text="Loading repository..." />
        </div>
      </Layout>
    );
  }

  if (!repository) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-red-600">Repository not found</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (repository.status !== 'completed') {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">{repository.name}</h1>
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <p className="text-yellow-800">
                  {repository.status === 'processing' && '🔄 Repository is being processed...'}
                  {repository.status === 'pending' && '⏳ Repository is queued for processing...'}
                  {repository.status === 'failed' && '❌ Repository processing failed'}
                </p>
                <p className="text-sm text-yellow-600 mt-2">
                  Chat will be available once processing is complete.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`Chat with ${repository.name} - Repo2Chat`}>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b px-6 py-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Chat with {repository.name}
                </h1>
                <p className="text-sm text-gray-500">{repository.full_name}</p>
              </div>
              <div className="text-sm text-gray-500">
                {messages.length} messages
              </div>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 max-w-7xl mx-auto w-full">
          <ChatInterface
            repository={repository}
            conversationId={currentConversationId}
            messages={messages}
            onNewMessage={handleNewMessage}
            suggestedQuestions={suggestedQuestions}
          />
        </div>
      </div>
    </Layout>
  );
}