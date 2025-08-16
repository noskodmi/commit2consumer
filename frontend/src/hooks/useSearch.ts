import { useState } from 'react';
import { repositoryApi } from '@/lib/api';
import toast from 'react-hot-toast';

export const useSearch = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const search = async (repositoryId: string, query: string) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await repositoryApi.search(repositoryId, query.trim());
      setResults(response.results || []);
      return response.results;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Search failed');
      setResults([]);
      return [];
    } finally {
      setLoading(false);
    }
  };

  return { search, loading, results };
};

