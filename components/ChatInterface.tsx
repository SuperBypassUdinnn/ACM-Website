"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [typingMessage, setTypingMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, typingMessage]);

  // Load template message on mount
  useEffect(() => {
    const loadTemplateMessage = async () => {
      try {
        const response = await fetch("http://localhost:8000/template_message", {
          headers: {
            "x-api-key": "852130f6-a7bd-48e2-bf66-539ff4fde4e6",
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.template) {
            typewriterEffect(data.template);
          }
        }
      } catch (error) {
        console.error("Failed to load template message:", error);
      }
    };

    loadTemplateMessage();
  }, []); // Run only on mount

  const typewriterEffect = (text: string) => {
    setIsTyping(true);
    setTypingMessage("");
    let index = 0;

    const interval = setInterval(() => {
      if (index < text.length) {
        setTypingMessage(text.substring(0, index + 1)); // Fix: use substring instead of prev + char
        index++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
        // Add the complete message to messages array
        setMessages((prev) => [...prev, { role: "assistant", content: text }]);
        setTypingMessage("");
      }
    }, 5); // 5ms per character for very fast typing effect

    return () => clearInterval(interval);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");

    // Add user message to chat
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": "852130f6-a7bd-48e2-bf66-539ff4fde4e6", // Toko ABC (Test) API key
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setLoading(false);

      // Use typewriter effect for assistant response
      typewriterEffect(data.reply || "Tidak ada respons.");
    } catch (error) {
      console.error("Error:", error);
      setLoading(false);
      typewriterEffect(
        "Maaf, terjadi kesalahan. Pastikan backend API berjalan di localhost:8000.",
      );
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[600px]">
      {/* Header */}
      <div className="bg-black text-white px-6 py-4 border-b border-gray-800 flex-shrink-0">
        <h1 className="text-xl font-semibold">Asisten AI Layanan Pelanggan</h1>
        <p className="text-sm text-gray-400">Online • Siap membantu Anda</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
        {messages.length === 0 && !isTyping ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p className="text-center">
              Mulai percakapan dengan mengetik pesan di bawah
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                    msg.role === "user"
                      ? "bg-black text-white rounded-br-none"
                      : "bg-white border border-gray-300 text-gray-900 rounded-bl-none shadow-sm"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-3 prose-li:my-1.5 prose-li:leading-relaxed">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}

            {/* Animated Typing Indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] px-4 py-3 rounded-2xl bg-white border border-gray-300 text-gray-900 rounded-bl-none shadow-sm">
                  <div className="flex items-center space-x-1">
                    <div className="flex space-x-1">
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Typewriter Effect Message */}
            {isTyping && typingMessage && (
              <div className="flex justify-start">
                <div className="max-w-[80%] px-4 py-3 rounded-2xl bg-white border border-gray-300 text-gray-900 rounded-bl-none shadow-sm">
                  <div className="prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-3 prose-li:my-1.5 prose-li:leading-relaxed">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {typingMessage}
                    </ReactMarkdown>
                    <span className="inline-block w-0.5 h-4 bg-gray-900 ml-0.5 animate-pulse"></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4 flex-shrink-0">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Ketik pesan Anda..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading || isTyping}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#00D9FF] focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={sendMessage}
            disabled={loading || isTyping || !input.trim()}
            className="px-6 py-3 bg-black text-white rounded-full font-medium hover:bg-[#00D9FF] transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading || isTyping ? "..." : "Kirim"}
          </button>
        </div>
      </div>
    </div>
  );
}
