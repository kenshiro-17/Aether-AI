import React, { createContext, useContext, useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
console.log("[AuthContext] API Base URL:", API_BASE);


interface User {
    username: string;
    email: string;
    full_name: string;
    avatar_url: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (username: string, password: string) => Promise<void>;
    register: (username: string, email: string, password: string, fullName: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (token) {
            fetchUser(token);
        } else {
            setIsLoading(false);
        }
    }, [token]);

    const fetchUser = async (authToken: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/auth/me`, {
                headers: { Authorization: `Bearer ${authToken}` }
            });
            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
            } else {
                logout(); // Invalid token
            }
        } catch (e) {
            console.error("Auth check failed", e);
            logout();
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (username: string, password: string) => {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);

        const res = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Login failed");
        }

        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
    };

    const register = async (username: string, email: string, password: string, full_name: string) => {
        let res;
        try {
            res = await fetch(`${API_BASE}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, full_name }),
            });
        } catch (e: any) {
            console.error("Fetch Error:", e);
            if (e.message.includes('Failed to fetch')) {
                throw new Error(`Cannot connect to Backend at ${API_BASE}. Please check if the server is running.`);
            }
            throw e;
        }

        if (!res.ok) {
            const err = await res.json();
            console.error("[AuthContext] Registration Error:", err);
            throw new Error(err.detail || "Registration failed");
        }

        // Auto login after register
        await login(username, password);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, isLoading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
