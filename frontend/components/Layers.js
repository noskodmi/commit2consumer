import { useState } from "react";
import Link from "next/link";
import WalletConnect from "./WalletConnect";

export default function Layout({ children }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-blue-600 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="/">
            <span className="text-xl font-bold cursor-pointer">Commit2Consumer</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/">
              <span className="hover:text-blue-200 cursor-pointer">Repos</span>
            </Link>
            <Link href="/add-repo">
              <span className="hover:text-blue-200 cursor-pointer">Add Repo</span>
            </Link>
            <div className="ml-4">
              <WalletConnect />
            </div>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path>
              </svg>
            </button>
          </div>
        </div>
        
        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-2 space-y-2">
            <Link href="/">
              <span className="block hover:bg-blue-700 p-2 rounded cursor-pointer">Repos</span>
            </Link>
            <Link href="/add-repo">
              <span className="block hover:bg-blue-700 p-2 rounded cursor-pointer">Add Repo</span>
            </Link>
            <div className="p-2">
              <WalletConnect />
            </div>
          </div>
        )}
      </nav>
      
      <main className="container mx-auto py-6 px-4">
        {children}
      </main>
      
      <footer className="bg-gray-800 text-white p-4 mt-8">
        <div className="container mx-auto text-center">
          <p>Commit2Consumer - Rewarding Open Source Contributions on Mantle</p>
          <p className="text-sm mt-1">Built for Mantle Hackathon 2025</p>
        </div>
      </footer>
    </div>
  );
}