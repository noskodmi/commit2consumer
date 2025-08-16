import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useRepository } from '@/hooks/useRepositories';
import { repositoryApi } from '@/lib/api';
import useSWR from 'swr';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { DocumentTextIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function DocumentationPage() {
  const router = useRouter();
  const { id } = router.query;
  
  const { repository, loading: repoLoading } = useRepository(id as string);
  
const { data: documentation, error } = useSWR(
  repository?.status === 'completed' ? `documentation-${id}` : null,
  () => repositoryApi.getDocumentation(id as string)
);

const docLoading = !documentation && !error;


  if (repoLoading || docLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <LoadingSpinner size="lg" text="Loading documentation..." />
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

  const sections = documentation?.documentation ? [
    { key: 'overview', title: 'Overview', content: documentation.documentation.overview },
    { key: 'setup_guide', title: 'Setup Guide', content: documentation.documentation.setup_guide },
    { key: 'api_documentation', title: 'API Documentation', content: documentation.documentation.api_documentation },
    { key: 'architecture', title: 'Architecture', content: documentation.documentation.architecture },
  ] : [];

  return (
    <Layout title={`${repository.name} Documentation - Repo2Chat`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            <DocumentTextIcon className="h-8 w-8 text-primary-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{repository.name} Documentation</h1>
              <p className="text-gray-600">Auto-generated documentation and guides</p>
            </div>
          </div>
        </div>

        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-600">Failed to load documentation</p>
          </div>
        ) : !documentation ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-yellow-800">Documentation not available yet</p>
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg">
            {/* Table of Contents */}
            <div className="border-b border-gray-200 px-6 py-4">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Table of Contents</h2>
              <nav className="space-y-2">
                {sections.map((section) => (
                  <a
                    key={section.key}
                    href={`#${section.key}`}
                    className="block text-primary-600 hover:text-primary-700 text-sm"
                  >
                    {section.title}
                  </a>
                ))}
              </nav>
            </div>

            {/* Documentation Content */}
            <div className="px-6 py-8 space-y-12">
              {sections.map((section) => (
                <div key={section.key} id={section.key}>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
                    {section.title}
                  </h2>
                  <div className="prose prose-lg max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {section.content}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}