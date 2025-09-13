import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

// Game configuration interface matching backend Pydantic models
interface GameConfig {
  board_size?: [number, number];
  win_target?: number;
  merge_strategy?: 'standard' | 'reverse';
  streak_enabled?: boolean;
  streak_multiplier?: number;
  redo_limit?: number;
}

export default function GameConfig() {
  const router = useRouter();
  const [config, setConfig] = useState<GameConfig>({
    board_size: [4, 4],
    win_target: 2048,
    merge_strategy: 'standard',
    streak_enabled: true,
    streak_multiplier: 1.5,
    redo_limit: 3,
  });

  useEffect(() => {
    // Check if user is authenticated
    const isAuthenticated = sessionStorage.getItem('py2048_authenticated');
    if (!isAuthenticated) {
      router.push('/auth');
    }
  }, [router]);

  const handleConfigChange = (key: keyof GameConfig, value: number | string | boolean) => {
    setConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleBoardSizeChange = (index: number, value: number) => {
    const newBoardSize = [...(config.board_size || [4, 4])] as [number, number];
    newBoardSize[index] = value;
    setConfig(prev => ({
      ...prev,
      board_size: newBoardSize
    }));
  };

  const handleStartGame = () => {
    // Store custom config in sessionStorage
    sessionStorage.setItem('py2048_custom_config', JSON.stringify(config));
    router.push('/game?mode=custom');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Customize Your Game</h1>
            <p className="text-gray-600">Configure your 2048 experience</p>
          </div>

          <div className="space-y-6">
            {/* Board Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Board Size</label>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-600">Width:</label>
                  <input
                    type="number"
                    min="3"
                    max="8"
                    value={config.board_size?.[0] || 4}
                    onChange={(e) => handleBoardSizeChange(0, parseInt(e.target.value))}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-center focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-600">Height:</label>
                  <input
                    type="number"
                    min="3"
                    max="8"
                    value={config.board_size?.[1] || 4}
                    onChange={(e) => handleBoardSizeChange(1, parseInt(e.target.value))}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-center focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Recommended: 3-6 for optimal experience</p>
            </div>

            {/* Win Target */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Win Target</label>
              <select
                value={config.win_target}
                onChange={(e) => handleConfigChange('win_target', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value={1024}>1024 (Easy)</option>
                <option value={2048}>2048 (Standard)</option>
                <option value={4096}>4096 (Hard)</option>
                <option value={8192}>8192 (Expert)</option>
              </select>
            </div>

            {/* Merge Strategy */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Merge Strategy</label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="merge_strategy"
                    value="standard"
                    checked={config.merge_strategy === 'standard'}
                    onChange={(e) => handleConfigChange('merge_strategy', e.target.value)}
                    className="mr-2 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm">Standard (merge towards direction first)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="merge_strategy"
                    value="reverse"
                    checked={config.merge_strategy === 'reverse'}
                    onChange={(e) => handleConfigChange('merge_strategy', e.target.value)}
                    className="mr-2 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm">Reverse (merge away from direction first)</span>
                </label>
              </div>
            </div>

            {/* Streak System */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Streak Bonus</label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.streak_enabled}
                    onChange={(e) => handleConfigChange('streak_enabled', e.target.checked)}
                    className="mr-2 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-gray-600">Enable</span>
                </label>
              </div>
              {config.streak_enabled && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Multiplier:</label>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    step="0.1"
                    value={config.streak_multiplier}
                    onChange={(e) => handleConfigChange('streak_multiplier', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1.0x</span>
                    <span>{config.streak_multiplier}x</span>
                    <span>3.0x</span>
                  </div>
                </div>
              )}
            </div>

            {/* Redo Limit */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Undo Limit</label>
              <input
                type="number"
                min="0"
                max="10"
                value={config.redo_limit}
                onChange={(e) => handleConfigChange('redo_limit', parseInt(e.target.value))}
                className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="text-xs text-gray-500 mt-1">Number of undos allowed (0 = unlimited)</p>
            </div>
          </div>

          <div className="flex justify-between items-center pt-8 border-t border-gray-200 mt-8">
            <button
              onClick={() => router.back()}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
            >
              ← Back
            </button>
            
            <button
              onClick={handleStartGame}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors font-medium"
            >
              Start Custom Game →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
