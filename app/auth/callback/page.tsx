"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("token");
    const provider = searchParams.get("provider");
    const error = searchParams.get("error");

    if (token) {
      // Save token to localStorage
      localStorage.setItem("token", token);

      // Redirect to dashboard or home
      console.log(`Logged in successfully with ${provider}`);
      router.push("/");
    } else if (error) {
      // Redirect to login with error message
      router.push(`/login?error=${error}`);
    } else {
      // No token or error, redirect to login
      router.push("/login");
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Processing login...</p>
      </div>
    </div>
  );
}
