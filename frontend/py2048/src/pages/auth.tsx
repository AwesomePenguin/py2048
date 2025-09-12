import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Auth() {
  const [invitationCode, setInvitationCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Call backend API for authentication
      const response = await fetch('http://127.0.0.1:8000/auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          invitation_code: invitationCode.trim(),
        }),
      });

      const data = await response.json();

      if (data.success && data.authenticated) {
        // Store auth state in sessionStorage (non-persistent as requested)
        sessionStorage.setItem('py2048_authenticated', 'true');
        sessionStorage.setItem('py2048_auth_message', data.message);
        router.push('/game-select');
      } else {
        setError(data.message || 'Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Auth API error:', error);
      setError('Unable to connect to server. Please check if the backend is running.');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">py2048</h1>
          <p className="text-gray-600">Enter your invitation code to play</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="invitation-code" className="block text-sm font-medium text-gray-700 mb-2">
              Invitation Code
            </label>
            <input
              id="invitation-code"
              type="text"
              value={invitationCode}
              onChange={(e) => setInvitationCode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your code"
              required
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Validating...' : 'Enter Game'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Need help? Contact your administrator for an invitation code.</p>
        </div>
      </div>
    </div>
  );
}
