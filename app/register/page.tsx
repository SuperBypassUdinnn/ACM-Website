"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import Link from "next/link";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "Rp 0",
    features: ["100 requests/month", "1 document", "Email support"],
  },
  {
    id: "basic",
    name: "Basic",
    price: "Rp 99,000",
    features: ["1,000 requests/month", "5 documents", "Email + Chat support"],
  },
  {
    id: "pro",
    name: "Pro",
    price: "Rp 299,000",
    popular: true,
    features: [
      "10,000 requests/month",
      "Unlimited documents",
      "Priority support",
    ],
  },
];

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [selectedPlan, setSelectedPlan] = useState("pro");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(name, email, password, selectedPlan);
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Daftar & Pilih Plan Anda
          </h1>
          <p className="text-gray-400">
            Mulai dalam hitungan menit, tanpa kartu kredit
          </p>
        </div>

        <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Error Message */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Step 1: Account Info */}
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">
                Step 1: Informasi Akun
              </h2>
              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Nama Lengkap
                  </label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="John Doe"
                  />
                </div>

                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="nama@example.com"
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    className="w-full px-4 py-3 bg-black border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Min. 6 karakter"
                  />
                </div>
              </div>
            </div>

            {/* Step 2: Choose Plan */}
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">
                Step 2: Pilih Plan
              </h2>
              <div className="grid md:grid-cols-3 gap-4">
                {PLANS.map((plan) => (
                  <div
                    key={plan.id}
                    onClick={() => setSelectedPlan(plan.id)}
                    className={`relative p-6 rounded-xl border-2 cursor-pointer transition-all ${
                      selectedPlan === plan.id
                        ? "border-blue-500 bg-blue-500/10"
                        : "border-zinc-700 bg-zinc-800 hover:border-zinc-600"
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                        <span className="bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                          POPULER
                        </span>
                      </div>
                    )}

                    <div className="text-center mb-4">
                      <h3 className="text-lg font-bold text-white mb-1">
                        {plan.name}
                      </h3>
                      <p className="text-2xl font-bold text-white">
                        {plan.price}
                      </p>
                      <p className="text-gray-400 text-sm">/bulan</p>
                    </div>

                    <ul className="space-y-2 mb-4">
                      {plan.features.map((feature, i) => (
                        <li
                          key={i}
                          className="text-sm text-gray-300 flex items-center"
                        >
                          <span className="mr-2">✓</span> {feature}
                        </li>
                      ))}
                    </ul>

                    <button
                      type="button"
                      onClick={() => setSelectedPlan(plan.id)}
                      className={`w-full py-2 rounded-lg font-medium transition-colors ${
                        selectedPlan === plan.id
                          ? "bg-blue-600 text-white"
                          : "bg-zinc-700 text-gray-300 hover:bg-zinc-600"
                      }`}
                    >
                      {selectedPlan === plan.id ? "Terpilih" : "Pilih"}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 text-lg"
            >
              {loading ? "Mendaftar..." : "Daftar Sekarang"}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              Sudah punya akun?{" "}
              <Link
                href="/login"
                className="text-blue-500 hover:text-blue-400 font-medium"
              >
                Masuk
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-gray-500 hover:text-gray-400 text-sm">
            ← Kembali ke Beranda
          </Link>
        </div>
      </div>
    </div>
  );
}
