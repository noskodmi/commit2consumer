import { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Toaster } from 'react-hot-toast';
import { CodeBracketIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export default function Layout({ children, title = 'Repository to Chat' }: LayoutProps) {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Transform GitHub repositories into intelligent chat interfaces" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <CodeBracketIcon className="h-8 w-8 text-primary-600" />
                  <span className="text-xl font-bold text-gray-900">Repo2Chat</span>
                </Link>
                
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    href="/"
                    className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Repositories
                  </Link>
                  <Link
                    href="/submit"
                    className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Submit Repository
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main content */}
        <main>{children}</main>
        
        <Toaster position="top-right" />
      </div>
    </>
  );
}
