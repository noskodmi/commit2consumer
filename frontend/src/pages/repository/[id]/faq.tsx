import { useRouter } from 'next/router';
import { useState } from 'react';
import Layout from '@/components/Layout';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useRepository } from '@/hooks/useRepositories';
import { repositoryApi } from '@/lib/api';
import useSWR from 'swr';
import { 
  QuestionMarkCircleIcon, 
  ArrowLeftIcon, 
  MagnifyingGlassIcon,
  ChevronDownIcon,
  ChevronRightIcon 
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function FAQPage() {
  const router = useRouter();
  const { id } = router.query;
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  
  const { repository, loading: repoLoading } = useRepository(id as string);
  
  const { data: faqData, loading: faqLoading, error } = useSWR(
    repository?.status === 'completed' ? `faq-${id}` : null,
    () => repositoryApi.getFaq(id as string)
  );

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  // Filter FAQ items based on search
  const filteredFAQ = faqData?.faq?.filter((item: any) =>
    item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.answer.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  if (repoLoading || faqLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <LoadingSpinner size="lg" text="Loading FAQ..." />
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

  return (
    <Layout title={`${repository.name} FAQ - Repo2Chat`}>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            href={`/repository/${repository.id}`}
            className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Repository
          </Link>
          
          <div className="flex items-center space-x-3">
            <QuestionMarkCircleIcon className="h-8 w-8 text-primary-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Frequently Asked Questions</h1>
              <p className="text-gray-600">Common questions about {repository.name}</p>
            </div>
          </div>
        </div>

        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-600">Failed to load FAQ</p>
          </div>
        ) : !faqData ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-yellow-800">FAQ not available yet</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search FAQ..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* FAQ Items */}
            <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
              {filteredFAQ.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  {searchQuery ? 'No FAQ items match your search' : 'No FAQ items available'}
                </div>
              ) : (
                filteredFAQ.map((item: any, index: number) => (
                  <div key={index} className="p-6">
                    <button
                      onClick={() => toggleExpanded(index)}
                      className="flex items-center justify-between w-full text-left"
                    >
                      <h3 className="text-lg font-medium text-gray-900 pr-4">
                        {item.question}
                      </h3>
                      {expandedItems.has(index) ? (
                        <ChevronDownIcon className="h-5 w-5 text-gray-500 flex-shrink-0" />
                      ) : (
                        <ChevronRightIcon className="h-5 w-5 text-gray-500 flex-shrink-0" />
                      )}
                    </button>
                    
                    {expandedItems.has(index) && (
                      <div className="mt-4 prose prose-sm max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {item.answer}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Help Section */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                Didn't find what you're looking for?
              </h3>
              <p className="text-blue-700 mb-4">
                Try chatting with our AI assistant for more specific questions about this repository.
              </p>
              <Link
                href={`/repository/${repository.id}/chat`}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
              >
                Start Chat
              </Link>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}