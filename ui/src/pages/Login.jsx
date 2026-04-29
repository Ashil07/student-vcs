import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';

function Login() {
  const { user, signIn, signUp, signOut } = useAuth();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState({ type: '', text: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatus({ type: '', text: '' });

    try {
      const { error } = mode === 'login'
        ? await signIn(email, password)
        : await signUp(email, password);

      if (error) {
        setStatus({ type: 'error', text: error.message });
      } else {
        setStatus({
          type: 'success',
          text: mode === 'login' ? 'Signed in successfully!' : 'Account created! Check your email.'
        });
        setEmail('');
        setPassword('');
      }
    } catch (err) {
      setStatus({ type: 'error', text: 'Unexpected error occurred.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (user) {
    return (
      <div className="fade-in">
        <div className="page-header">
          <h1 className="page-title">Account</h1>
          <p className="page-subtitle">You are signed in as {user.email}</p>
        </div>
        <div className="glass-panel" style={{ maxWidth: '400px' }}>
          <Button onClick={signOut}>Sign Out</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">{mode === 'login' ? 'Sign In' : 'Create Account'}</h1>
        <p className="page-subtitle">Connect to your cloud repositories</p>
      </div>

      {status.text && (
        <div className={`alert ${status.type}`}>{status.text}</div>
      )}

      <div className="glass-panel" style={{ maxWidth: '400px' }}>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Email</label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <label className="input-label">Password</label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </Button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center' }}>
          {mode === 'login' ? (
            <span>
              No account?{' '}
              <button
                onClick={() => setMode('signup')}
                style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer' }}
              >
                Create one
              </button>
            </span>
          ) : (
            <span>
              Already have an account?{' '}
              <button
                onClick={() => setMode('login')}
                style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer' }}
              >
                Sign in
              </button>
            </span>
          )}
        </p>
      </div>
    </div>
  );
}

export default Login;
