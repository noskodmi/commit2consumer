import useSWR from 'swr';
import { repositoryApi, Repository } from '@/lib/api';

export const useRepositories = (params?: { status?: string }) => {
  const { data, error, mutate } = useSWR(
    ['repositories', params],
    () => repositoryApi.list(params)
  );

  return {
    repositories: data as Repository[],
    loading: !error && !data,
    error,
    mutate,
  };
};

export const useRepository = (id: string) => {
  const { data, error, mutate } = useSWR(
    id ? `repository-${id}` : null,
    () => repositoryApi.get(id)
  );

  return {
    repository: data as Repository,
    loading: !error && !data,
    error,
    mutate,
  };
};
