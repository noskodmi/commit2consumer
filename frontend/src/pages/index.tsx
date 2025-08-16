import { useState } from 'react';
import Layout from '@/components/Layout';
import RepositoryCard from '@/components/RepositoryCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useRepositories } from '@/hooks/useRepositories';
import { PlusIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

const statusOptions = [
  { value: '', label: 'All Repositories' },
  { value: 'completed', label: 'Completed' },
  { value: 'processing', label: 'Processing' },
  { value: 'pending', label: 'Pending' },
  { value: 'failed', label: 'Failed' },
];

export default function HomePage() {
  const [statusFilter, setStatusFilter] = useState('');
  const { repositories, loading, error } = useRepositories({ 
    status: statusFilter || undefined 
  });

  return (
    <Layout title="Repositories - Repo2Chat">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              Repositories
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Transform GitHub repositories into intelligent chat interfaces
            </p>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <Link
              href="/submit"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Repository
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-6 flex items-center space-x-4">
          <label htmlFor="status" className="text-sm font-medium text-gray-700">
            Filter by status:
          </label>
          <select
            id="status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border-gray-300 text-sm focus:border-primary-500 focus:ring-primary-500"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Content */}
        <div className="mt-8">
          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" text="Loading repositories..." />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600">Error loading repositories: {error.message}</p>
            </div>
          ) : repositories && repositories.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {repositories.map((repository) => (
                <RepositoryCard key={repository.id} repository={repository} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">
                No repositories found. 
                <Link href="/submit" className="text-primary-600 hover:text-primary-700 ml-1">
                  Add one to get started
                </Link>
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}