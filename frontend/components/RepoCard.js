import Link from "next/link";

export default function RepoCard({ repo }) {
  // Extract repo name from URL for display
  const repoName = repo.url.split('/').slice(-2).join('/');

  return (
    <div className="bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow p-6">
      <h2 className="font-bold text-lg text-gray-800 mb-2">{repoName}</h2>
      <p className="text-gray-600 mb-4">{repo.chunks} code chunks indexed</p>
      
      <div className="flex justify-between items-center">
        <a 
          href={repo.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          View on GitHub
        </a>
        
        <Link href={`/repo/${repo.id}`}>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm transition-colors">
            View & Chat
          </button>
        </Link>
      </div>
    </div>
  );
}