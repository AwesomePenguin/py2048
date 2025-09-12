import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Auth() {
  const [invitationCode, setInvitationCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  // TODO: This should be fetched from backend in a real implementation
  const VALID_INVITATION_CODE = 'GAME2048';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simple validation - in production, this would be validated against backend
    if (invitationCode.trim().toUpperCase() === VALID_INVITATION_CODE) {
      // Store auth state in sessionStorage (non-persistent as requested)
      sessionStorage.setItem('py2048_authenticated', 'true');
      router.push('/game-select');
    } else {
      setError('Invalid invitation code. Please try again.');
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
          <p>Hint: Try "GAME2048" (case-insensitive)</p>
        </div>
      </div>
    </div>
  );
}
