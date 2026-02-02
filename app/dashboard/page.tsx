"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function DashboardPage() {
  const { user, client, apiKey, isAuthenticated, isLoading, logout } =
    useAuth();
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const copyApiKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user || !client) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Welcome, {client.name}! 👋
            </h1>
            <p className="text-gray-400">{user.email}</p>
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Plan Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-400 text-sm font-medium">Your Plan</h3>
              <span className="text-2xl">📊</span>
            </div>
            <p className="text-3xl font-bold text-white capitalize">
              {client.plan}
            </p>
            <p className="text-gray-500 text-sm mt-1">
              Status: <span className="text-green-500">{client.status}</span>
            </p>
          </div>

          {/* API Key Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-400 text-sm font-medium">API Key</h3>
              <span className="text-2xl">🔑</span>
            </div>
            <div className="flex items-center gap-2">
              <code className="text-sm text-blue-400 font-mono truncate flex-1">
                {apiKey ? `${apiKey.substring(0, 20)}...` : "N/A"}
              </code>
              <button
                onClick={copyApiKey}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
              >
                {copied ? "✓" : "Copy"}
              </button>
            </div>
            <p className="text-gray-500 text-xs mt-2">
              Use this key for API calls
            </p>
          </div>

          {/* Usage Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-400 text-sm font-medium">
                Usage (Mock)
              </h3>
              <span className="text-2xl">📈</span>
            </div>
            <p className="text-3xl font-bold text-white">45</p>
            <p className="text-gray-500 text-sm mt-1">requests this month</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              href="/chat"
              className="p-6 bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors group"
            >
              <div className="text-3xl mb-3">💬</div>
              <h3 className="text-white font-semibold mb-1">Go to Chat</h3>
              <p className="text-blue-100 text-sm">Try the chatbot interface</p>
            </Link>

            <Link
              href="/docs"
              className="p-6 bg-zinc-800 hover:bg-zinc-700 rounded-xl transition-colors group"
            >
              <div className="text-3xl mb-3">📚</div>
              <h3 className="text-white font-semibold mb-1">Documentation</h3>
              <p className="text-gray-400 text-sm">API guides and tutorials</p>
            </Link>

            <div className="p-6 bg-zinc-800 rounded-xl opacity-50 cursor-not-allowed">
              <div className="text-3xl mb-3">📄</div>
              <h3 className="text-white font-semibold mb-1">Upload Docs</h3>
              <p className="text-gray-400 text-sm">Coming soon...</p>
            </div>
          </div>
        </div>

        {/* API Key Full Display */}
        <div className="mt-8 bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-3">
            Full API Key
          </h3>
          <div className="bg-black rounded-lg p-4 border border-zinc-700">
            <code className="text-green-400 font-mono text-sm break-all">
              {apiKey}
            </code>
          </div>
          <p className="text-gray-500 text-sm mt-3">
            ⚠️ Keep this key secret. Do not share it publicly.
          </p>
        </div>
      </div>
    </div>
  );
}
