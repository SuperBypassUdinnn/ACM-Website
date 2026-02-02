import Link from "next/link";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-black text-white py-6 px-8 border-b border-zinc-800">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">AI Chatbot Documentation</h1>
          <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
            ← Back to Dashboard
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto p-8">
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-black mb-4">
            API Documentation
          </h2>
          <p className="text-gray-600 text-lg">
            Complete guide untuk mengintegrasikan AI Chatbot ke aplikasi Anda.
          </p>
        </div>

        {/* Coming Soon */}
        <div className="bg-gray-100 rounded-xl p-12 text-center mb-8">
          <div className="text-6xl mb-4">🚧</div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Coming Soon</h3>
          <p className="text-gray-600">
            Dokumentasi lengkap sedang dalam pengembangan.
          </p>
        </div>

        {/* Quick Start */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h3 className="text-2xl font-bold text-black mb-4">Quick Start</h3>

          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-black mb-2">1. Endpoint</h4>
              <div className="bg-black text-green-400 p-4 rounded font-mono text-sm">
                POST http://localhost:8000/chat
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-black mb-2">2. Headers</h4>
              <div className="bg-black text-green-400 p-4 rounded font-mono text-sm">
                Content-Type: application/json
                <br />
                x-api-key: YOUR_API_KEY
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-black mb-2">3. Request Body</h4>
              <div className="bg-black text-green-400 p-4 rounded font-mono text-sm overflow-x-auto">
                {`{
  "message": "Halo, apa kabar?",
  "session_id": "unique-session-id"
}`}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-black mb-2">4. Response</h4>
              <div className="bg-black text-green-400 p-4 rounded font-mono text-sm overflow-x-auto">
                {`{
  "reply": "Halo! Saya baik, terima kasih..."
}`}
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="border border-gray-200 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-black mb-2">
              🎯 Features
            </h4>
            <ul className="space-y-2 text-gray-700">
              <li>✓ Context-aware responses</li>
              <li>✓ Session management</li>
              <li>✓ Rate limiting</li>
              <li>✓ Custom knowledge base</li>
            </ul>
          </div>

          <div className="border border-gray-200 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-black mb-2">📦 SDKs</h4>
            <ul className="space-y-2 text-gray-700">
              <li>• JavaScript/TypeScript</li>
              <li>• Python</li>
              <li>• cURL</li>
              <li>• More coming soon...</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
