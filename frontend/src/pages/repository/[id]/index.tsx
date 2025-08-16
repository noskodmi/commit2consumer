import { useRouter } from 'next/router';
import { useState } from 'react';
import Layout from '@/components/Layout';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useRepository } from '@/hooks/useRepositories';
import { 
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  QuestionMarkCircleIcon,
  MagnifyingGlassIcon,
  CodeBracketIcon,
  StarIcon,
  EyeIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import clsx from 'clsx';

const statusConfig = {
  pending: { color: 'text-yellow-600', bg: 'bg-yellow-100' },
  processing: { color: 'text-blue-600', bg: 'bg-blue-100' },
  completed: { color: 'text-green-600', bg: 'bg-green-100' },
  failed: { color: 'text-red-600', bg: 'bg-red-100' },
};

export default function RepositoryDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [activeTab, setActiveTab] = useState('overview');
  
  const { repository, loading, error } = useRepository(id as string);

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <LoadingSpinner size="lg" text="Loading repository..." />
        </div>
      </Layout>
    );
  }

  if (error || !repository) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-red-600">Repository not found or failed to load</p>
          </div>
        </div>
      </Layout>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: DocumentTextIcon },
    { id: 'files', name: 'Files', icon: CodeBracketIcon },
    { id: 'search', name: 'Search', icon: MagnifyingGlassIcon },
  ];

  return (
    <Layout title={`${repository.name} - Repo2Chat`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h1 className="text-2xl font-bold text-gray-900">{repository.name}</h1>
                    <span className={clsx(
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize',
                    statusConfig[repository.status].color,
                    statusConfig[repository.status].bg
                  )}>
                    {repository.status}
                  </span>
                </div>
                <p className="text-gray-600 mt-1">{repository.full_name}</p>
                
                {repository.description && (
                  <p className="text-gray-700 mt-2">{repository.description}</p>
                )}
                
                <div className="flex items-center space-x-6 mt-3 text-sm text-gray-500">
                  {repository.language && (
                    <div className="flex items-center space-x-1">
                      <CodeBracketIcon className="h-4 w-4" />
                      <span>{repository.language}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1">
                    <StarIcon className="h-4 w-4" />
                    <span>{repository.stars}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <EyeIcon className="h-4 w-4" />
                    <span>{repository.forks} forks</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <CalendarIcon className="h-4 w-4" />
                    <span>Added {formatDistanceToNow(new Date(repository.created_at), { addSuffix: true })}</span>
                  </div>
                </div>
              </div>
              
              {repository.status === 'completed' && (
                <div className="flex space-x-3">
                  <Link
                    href={`/repository/${repository.id}/documentation`}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <DocumentTextIcon className="h-4 w-4 mr-2" />
                    Documentation
                  </Link>
                  <Link
                    href={`/repository/${repository.id}/faq`}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <QuestionMarkCircleIcon className="h-4 w-4 mr-2" />
                    FAQ
                  </Link>
                  <Link
                    href={`/repository/${repository.id}/chat`}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-primary-600 text-sm font-medium text-white hover:bg-primary-700"
                  >
                    <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2" />
                    Chat
                  </Link>
                </div>
              )}
            </div>
          </div>
          
          {/* Status Messages */}
          {repository.status === 'processing' && (
            <div className="px-6 py-3 bg-blue-50 border-t">
              <p className="text-blue-700 text-sm">
                🔄 Repository is being processed. This usually takes 1-3 minutes...
              </p>
            </div>
          )}
          
          {repository.status === 'failed' && repository.error_message && (
            <div className="px-6 py-3 bg-red-50 border-t">
              <p className="text-red-700 text-sm">
                ❌ Processing failed: {repository.error_message}
              </p>
            </div>
          )}
        </div>

        {/* Tabs */}
        {repository.status === 'completed' && (
          <div className="bg-white shadow rounded-lg">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={clsx(
                        activeTab === tab.id
                          ? 'border-primary-500 text-primary-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                        'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2'
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{tab.name}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
            
            <div className="p-6">
              {activeTab === 'overview' && <OverviewTab repository={repository} />}
              {activeTab === 'files' && <FilesTab repositoryId={repository.id} />}
              {activeTab === 'search' && <SearchTab repositoryId={repository.id} />}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

// Overview Tab Component
function OverviewTab({ repository }: { repository: any }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Repository Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <DocumentTextIcon className="h-8 w-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">
                  {repository.document_count || 0}
                </p>
                <p className="text-sm text-gray-500">Files Processed</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <StarIcon className="h-8 w-8 text-yellow-500" />
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{repository.stars}</p>
                <p className="text-sm text-gray-500">GitHub Stars</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <CodeBracketIcon className="h-8 w-8 text-green-500" />
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">
                  {repository.language || 'Mixed'}
                </p>
                <p className="text-sm text-gray-500">Primary Language</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href={`/repository/${repository.id}/chat`}
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all"
          >
            <div className="flex items-center space-x-3">
              <ChatBubbleLeftRightIcon className="h-6 w-6 text-primary-600" />
              <div>
                <h4 className="font-medium text-gray-900">Start Chatting</h4>
                <p className="text-sm text-gray-500">Ask questions about this repository</p>
              </div>
            </div>
          </Link>
          
          <Link
            href={`/repository/${repository.id}/documentation`}
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all"
          >
            <div className="flex items-center space-x-3">
              <DocumentTextIcon className="h-6 w-6 text-primary-600" />
              <div>
                <h4 className="font-medium text-gray-900">View Documentation</h4>
                <p className="text-sm text-gray-500">Auto-generated docs and guides</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

// Files Tab Component
function FilesTab({ repositoryId }: { repositoryId: string }) {
  // This would fetch and display repository files
  return (
    <div>
      <p className="text-gray-600">Files tab implementation would go here</p>
      <p className="text-sm text-gray-500 mt-2">
        This would show a tree view of processed files with their languages and sizes.
      </p>
    </div>
  );
}

// Search Tab Component
function SearchTab({ repositoryId }: { repositoryId: string }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    try {
      const searchResults = await repositoryApi.search(repositoryId, query.trim());
      setResults(searchResults.results || []);
   } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Search Repository</h3>
        <form onSubmit={handleSearch} className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for functions, classes, or concepts..."
            className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={searching || !query.trim()}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-400"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Search Results</h4>
          {results.map((result: any, index: number) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-primary-600">{result.file_path}</span>
                <span className="text-xs text-gray-500">
                  {Math.round(result.relevance_score * 100)}% match
                </span>
              </div>
              <pre className="text-sm text-gray-800 bg-gray-50 p-2 rounded overflow-x-auto">
                {result.content}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
