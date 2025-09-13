import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function GameSelect() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const isAuthenticated = sessionStorage.getItem('py2048_authenticated');
    if (!isAuthenticated) {
      router.push('/auth');
    }
  }, [router]);

  const handleLogout = () => {
    sessionStorage.removeItem('py2048_authenticated');
    router.push('/auth');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Choose Your Game Mode</h1>
          <p className="text-gray-600">Select how you would like to play 2048</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Standard Game */}
          <Link 
            href="/game?mode=standard"
            className="group block p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-green-600 transition-colors">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Standard Game</h3>
              <p className="text-gray-600 text-sm">
                Classic 2048 game with default settings
              </p>
              <ul className="mt-3 text-xs text-gray-500 space-y-1">
                <li>• 4x4 board</li>
                <li>• Win at 2048</li>
                <li>• Standard merge rules</li>
                <li>• AI hints available</li>
              </ul>
            </div>
          </Link>

          {/* Custom Game */}
          <Link 
            href="/game-config"
            className="group block p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
          >
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-600 transition-colors">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Custom Game</h3>
              <p className="text-gray-600 text-sm">
                Customize your game experience
              </p>
              <ul className="mt-3 text-xs text-gray-500 space-y-1">
                <li>• Custom board size</li>
                <li>• Adjust win target</li>
                <li>• Merge strategies</li>
                <li>• Streak bonuses</li>
              </ul>
            </div>
          </Link>
        </div>

        <div className="flex justify-between items-center pt-6 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors"
          >
            ← Logout
          </button>
          
          <div className="text-right text-sm text-gray-500">
            <p>Ready to challenge your mind?</p>
          </div>
        </div>
      </div>
    </div>
  );
}
