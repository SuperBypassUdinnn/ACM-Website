"use client";

export default function ChatInterface() {
  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[600px]">
      {/* Header */}
      <div className="bg-black text-white px-6 py-4 border-b border-gray-800">
        <h1 className="text-xl font-semibold">AI Customer Service Bot</h1>
        <p className="text-sm text-gray-400">Online • Ready to help</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
        <div className="flex items-center justify-center h-full text-gray-400">
          <p className="text-center">
            Start a conversation by typing a message below
          </p>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Type your message..."
            disabled
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-[#00D9FF] focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            disabled
            className="px-6 py-3 bg-black text-white rounded-full font-medium hover:bg-[#00D9FF] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
