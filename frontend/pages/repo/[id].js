import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

export default function RepoDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [repo, setRepo] = useState(null);
  const [docs, setDocs] = useState("");
  const [faq, setFaq] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState(null);
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch repo data, docs, and FAQ
  useEffect(() => {
    if (!id) return;

    const fetchRepoData = async () => {
      try {
        setLoading(true);
        
        // Fetch all repos to get this repo's metadata
        const reposRes = await fetch(`${API_URL}/repos`);
        if (!reposRes.ok) throw new Error("Failed to fetch repositories");
        const repos = await reposRes.ok ? await reposRes.json() : [];
        const currentRepo = repos.find(r => r.id === id);
        setRepo(currentRepo);
        
        // Fetch docs
        const docsRes = await fetch(`${API_URL}/repos/${id}/docs`);
        if (docsRes.ok) {
          const docsData = await docsRes.json();
          setDocs(docsData.docs);
        }
        
        // Fetch FAQ
        const faqRes = await fetch(`${API_URL}/repos/${id}/faq`);
        if (faqRes.ok) {
          const faqData = await faqRes.json();
          setFaq(faqData.faq);
        }
        
        setError(null);
      } catch (err) {
        console.error("Error fetching repo data:", err);
        setError("Failed to load repository data");
      } finally {
        setLoading(false);
      }
    };

    fetchRepoData();
  }, [id, API_URL]);

  // Handle asking a question
  const askQuestion = async () => {
    if (!question.trim()) return;
    
    try {
      setChatLoading(true);
      setAnswer("");
      
      const res = await fetch(`${API_URL}/repos/${id}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      
      if (!res.ok) {
        throw new Error("Failed to get answer");
      }
      
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      console.error("Error asking question:", err);
      setAnswer("Sorry, I couldn't process your question. Please try again.");
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-10">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-2 text-gray-600">Loading repository data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <Link href="/">
          <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
            Back to Repositories
          </button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Link href="/">
          <button className="text-blue-600 hover:text-blue-800 flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Back to Repositories
          </button>
        </Link>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          {repo?.url.split('/').slice(-2).join('/')}
        </h1>
        <p className="text-gray-600 mb-4">
          {repo?.chunks} code chunks indexed
        </p>
        <a 
          href={repo?.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800"
        >
          View on GitHub
        </a>
      </div>
      
      {/* Documentation Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Documentation</h2>
        <div className="bg-gray-50 p-4 rounded-md whitespace-pre-wrap">
          {docs || "No documentation available yet."}
        </div>
      </div>
      
      {/* FAQ Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Frequently Asked Questions</h2>
        {faq.length > 0 ? (
          <div className="space-y-4">
            {faq.map((item, i) => (
              <div key={i} className="bg-gray-50 p-4 rounded-md">
                {item}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No FAQs available yet.</p>
        )}
      </div>
      
      {/* Chat Section */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Ask about this Repository</h2>
        
        <div className="mb-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this repository..."
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            disabled={chatLoading}
          />
        </div>
        
        <button
          onClick={askQuestion}
          disabled={chatLoading || !question.trim()}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-md font-medium transition-colors disabled:opacity-50 mb-4"
        >
          {chatLoading ? "Thinking..." : "Ask Question"}
        </button>
        
        {answer && (
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-md">
            <h3 className="font-medium text-blue-800 mb-2">Answer:</h3>
            <div className="text-gray-800 whitespace-pre-wrap">
              {answer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}