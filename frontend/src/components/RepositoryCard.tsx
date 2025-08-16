import Link from 'next/link';
import { Repository } from '@/lib/api';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  StarIcon,
  CodeBracketIcon, 
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { formatDistanceToNow } from 'date-fns';
import clsx from 'clsx';

interface RepositoryCardProps {
  repository: Repository;
}

const statusConfig = {
  pending: { icon: ClockIcon, color: 'text-yellow-500', bg: 'bg-yellow-50' },
  processing: { icon: ClockIcon, color: 'text-blue-500', bg: 'bg-blue-50' },
  completed: { icon: CheckCircleIcon, color: 'text-green-500', bg: 'bg-green-50' },
  failed: { icon: ExclamationCircleIcon, color: 'text-red-500', bg: 'bg-red-50' },
};

export default function RepositoryCard({ repository }: RepositoryCardProps) {
  const StatusIcon = statusConfig[repository.status].icon;

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Link
              href={`/repository/${repository.id}`}
              className="text-lg font-semibold text-gray-900 hover:text-primary-600"
            >
              {repository.name}
            </Link>
            <p className="text-sm text-gray-500">{repository.full_name}</p>
            
            {repository.description && (
              <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                {repository.description}
              </p>
            )}
          </div>
          
          <div className={clsx(
            'flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium',
            statusConfig[repository.status].bg,
            statusConfig[repository.status].color
          )}>
            <StatusIcon className="h-3 w-3" />
            <span className="capitalize">{repository.status}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
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
          
          {repository.document_count && (
            <span>{repository.document_count} files</span>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Created {formatDistanceToNow(new Date(repository.created_at), { addSuffix: true })}
          </span>
          
          {repository.status === 'completed' && (
            <Link
              href={`/repository/${repository.id}/chat`}
              className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              <span>Chat</span>
            </Link>
          )}
        </div>

        {/* Error message */}
        {repository.status === 'failed' && repository.error_message && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{repository.error_message}</p>
          </div>
        )}
      </div>
    </div>
  );
}