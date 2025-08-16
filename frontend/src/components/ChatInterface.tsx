import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { useChat } from '@/hooks/useChat';
import { ChatMessage, Repository } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import clsx from 'clsx';
import { formatDistanceToNow } from 'date-fns';

interface ChatInterfaceProps {
  repository: Repository;
  conversationId?: string;
  messages: ChatMessage[];
  onNewMessage?: (message: ChatMessage, conversationId: string) => void;
  suggestedQuestions?: string[];
}

export default function ChatInterface({
  repository,
  conversationId,
  messages,
  onNewMessage,
  suggestedQuestions
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [currentConversationId, setCurrentConversationId] = useState(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, loading } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString()
    };

    // Add user message immediately
    onNewMessage?.(userMessage, currentConversationId || '');

    const response = await sendMessage(repository.id, input.trim(), currentConversationId);
    
    if (response) {
      setCurrentConversationId(response.conversation_id);
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        context_used: [],
        created_at: new Date().toISOString()
      };

      onNewMessage?.(assistantMessage, response.conversation_id);
    }

    setInput('');
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Start chatting about {repository.name}
            </h3>
            <p className="mt-2 text-gray-500">
              Ask questions about the code, architecture, or how to use this repository.
            </p>
            
            {suggestedQuestions && suggestedQuestions.length > 0 && (
              <div className="mt-6 space-y-2">
                <p className="text-sm font-medium text-gray-700">Suggested questions:</p>
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="block w-full max-w-md mx-auto p-3 text-left text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={clsx(
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}>
              <div className={clsx(
                'max-w-3xl rounded-lg px-4 py-2',
                message.role === 'user' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-white border shadow-sm'
              )}>
                <div className="prose prose-sm max-w-none">
                  {message.role === 'user' ? (
                    <p className="text-white m-0">{message.content}</p>
                  ) : ( "lol"
                    // <ReactMarkdown
                    //   remarkPlugins={[remarkGfm]}
                    //   components={{
                    //     code({ node, inline, className, children, ...props }) {
                    //       const match = /language-(\w+)/.exec(className || '');
                    //       return !inline && match ? (
                    //         <SyntaxHighlighter
                    //           style={tomorrow}
                    //           language={match[1]}
                    //           PreTag="div"
                    //           {...props}
                    //         >
                    //           {String(children).replace(/\n$/, '')}
                    //         </SyntaxHighlighter>
                    //       ) : (
                    //         <code className={className} {...props}>
                    //           {children}
                    //         </code>
                    //       );
                    //     },
                    //   }}
                    // >
                    //   {message.content}
                    // </ReactMarkdown>
                  )}
                </div>
                
                <div className={clsx(
                  'mt-2 text-xs',
                  message.role === 'user' ? 'text-primary-200' : 'text-gray-500'
                )}>
                  {formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this repository..."
            disabled={loading}
            className="flex-1 min-w-0 rounded-md border border-gray-300 px-3 py-2 focus:border-primary-500 focus:ring-primary-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className={clsx(
              'inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
              !input.trim() || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            )}
          >
            <PaperAirplaneIcon className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
