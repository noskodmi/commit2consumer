import type { AppProps } from 'next/app';
import { SWRConfig } from 'swr';
import { api } from '@/lib/api';
import '@/styles/globals.css';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function App({ Component, pageProps }: AppProps) {
  return (
    <SWRConfig
      value={{
        fetcher,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
      }}
    >
      <Component {...pageProps} />
    </SWRConfig>
  );
}