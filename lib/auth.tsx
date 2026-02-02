"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  email: string;
  role: string;
}

interface Client {
  id: string;
  name: string;
  plan: string;
  status: string;
}

interface AuthContextType {
  user: User | null;
  client: Client | null;
  apiKey: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    name: string,
    email: string,
    password: string,
    plan: string,
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [client, setClient] = useState<Client | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check if user is logged in on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUserInfo(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setClient(data.client);
        setApiKey(data.api_key);
      } else {
        // Token invalid, clear it
        localStorage.removeItem("access_token");
      }
    } catch (error) {
      console.error("Failed to fetch user info:", error);
      localStorage.removeItem("access_token");
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }

    const data = await response.json();

    // Save token
    localStorage.setItem("access_token", data.access_token);

    // Set state
    setUser(data.user);
    setClient(data.client);
    setApiKey(data.api_key);

    // Redirect to dashboard
    router.push("/dashboard");
  };

  const register = async (
    name: string,
    email: string,
    password: string,
    plan: string,
  ) => {
    const response = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password, plan }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }

    const data = await response.json();

    // Save token
    localStorage.setItem("access_token", data.access_token);

    // Set state
    setUser(data.user);
    setClient(data.client);
    setApiKey(data.api_key);

    // Redirect to dashboard
    router.push("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setClient(null);
    setApiKey(null);
    router.push("/");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        client,
        apiKey,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
