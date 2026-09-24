import React, { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

interface AuthPanelProps {
  onAuthenticated: () => void;
}

const AuthPanel: React.FC<AuthPanelProps> = ({ onAuthenticated }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/auth/me`, { credentials: 'include' })
      .then((response) => {
        if (response.ok) onAuthenticated();
      })
      .catch(() => {});
  }, [onAuthenticated]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage('');
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/auth/${mode === 'login' ? 'login' : 'register'}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        },
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || 'Authentication failed');
      if (data.authenticated) {
        onAuthenticated();
      } else {
        setMessage('Check your email to confirm your account, then sign in.');
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-8 bg-white rounded-lg border border-stone-200 shadow-lg">
      <h2 className="text-2xl font-bold text-stone-900 mb-2">
        {mode === 'login' ? 'Welcome back' : 'Create your SpazaChef account'}
      </h2>
      <p className="text-stone-600 mb-6">
        Your account keeps recipe access secure and lets SpazaChef manage your future saved recipes and subscription.
      </p>

      <form onSubmit={submit} className="space-y-4">
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email address"
          className="w-full p-3 border border-stone-300 rounded-lg"
        />
        <input
          type="password"
          required
          minLength={8}
          maxLength={128}
          autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Password (8+ characters)"
          className="w-full p-3 border border-stone-300 rounded-lg"
        />
        {message && (
          <p role="alert" className="text-sm text-stone-700 bg-orange-50 border border-orange-200 rounded-lg p-3">
            {message}
          </p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-stone-400 font-semibold"
        >
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
        </button>
      </form>

      <button
        type="button"
        onClick={() => {
          setMode(mode === 'login' ? 'register' : 'login');
          setMessage('');
        }}
        className="w-full mt-4 text-sm text-orange-600 font-semibold hover:underline"
      >
        {mode === 'login' ? 'Need an account? Create one' : 'Already have an account? Sign in'}
      </button>
    </div>
  );
};

export default AuthPanel;
