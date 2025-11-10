import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Mail, User, ArrowRight, Loader2 } from 'lucide-react';

export default function AuthScreen() {
    const { login, register } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [form, setForm] = useState({
        username: '',
        password: '',
        email: '',
        fullName: ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await login(form.username, form.password);
            } else {
                await register(form.username, form.email, form.password, form.fullName);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-zinc-950 text-zinc-100 p-4">
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-purple-500/10 blur-[120px]" />
                <div className="absolute top-[40%] -right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent mb-2">
                            AETHER
                        </h1>
                        <p className="text-zinc-500">
                            {isLogin ? "Welcome back, Operator." : "Initialize System Access."}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <AnimatePresence mode="wait">
                            {!isLogin && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="space-y-4 overflow-hidden"
                                >
                                    <div className="space-y-2">
                                        <label className="text-xs font-medium text-zinc-400 ml-1">FULL NAME <span className="text-zinc-600">(Optional)</span></label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                            <input
                                                type="text"
                                                required={false}
                                                className="w-full bg-black/20 border border-white/5 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-white/20 transition-colors"
                                                placeholder="John Doe"
                                                value={form.fullName}
                                                onChange={e => setForm({ ...form, fullName: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-medium text-zinc-400 ml-1">EMAIL <span className="text-zinc-600">(Optional)</span></label>
                                        <div className="relative">
                                            <Mail className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                            <input
                                                type="email"
                                                required={false}
                                                className="w-full bg-black/20 border border-white/5 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-white/20 transition-colors"
                                                placeholder="operator@aether.ai"
                                                value={form.email}
                                                onChange={e => setForm({ ...form, email: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="space-y-2">
                            <label className="text-xs font-medium text-zinc-400 ml-1">USERNAME</label>
                            <div className="relative">
                                <User className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                <input
                                    type="text"
                                    required
                                    className="w-full bg-black/20 border border-white/5 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-white/20 transition-colors"
                                    placeholder="operator"
                                    value={form.username}
                                    onChange={e => setForm({ ...form, username: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-medium text-zinc-400 ml-1">PASSWORD</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                <input
                                    type="password"
                                    required
                                    className="w-full bg-black/20 border border-white/5 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-white/20 transition-colors"
                                    placeholder="••••••••"
                                    value={form.password}
                                    onChange={e => setForm({ ...form, password: e.target.value })}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-white text-black font-semibold rounded-xl py-3 flex items-center justify-center gap-2 hover:bg-zinc-200 transition-colors disabled:opacity-50 mt-6"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                                <>
                                    {isLogin ? "Access System" : "Create Identity"}
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <button
                            onClick={() => setIsLogin(!isLogin)}
                            className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                        >
                            {isLogin ? "New Operator? Create account" : "Already have access? Login"}
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
