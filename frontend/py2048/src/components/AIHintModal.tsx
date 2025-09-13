import React from 'react';
import Modal from './Modal';

interface AIHintModalProps {
  isOpen: boolean;
  isLoading: boolean;
  hintMessage: string;
  fullHint?: {
    suggestion?: string;
    reasoning: string;
    strategy?: string;
    confidence?: number;
    alternatives?: string[];
  } | null;
  onClose: () => void;  
}

const AIHintModal: React.FC<AIHintModalProps> = ({
  isOpen,
  isLoading,
  hintMessage,
  fullHint,
  onClose,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="AI Assistant">
      <div className="space-y-4">
        {/* AI Assistant Header */}
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Game Assistant</h3>
          <p className="text-sm text-gray-600">Get strategic advice for your next move</p>
        </div>

        {/* Hint Display Area */}
        <div className="bg-blue-50 rounded-lg p-4 min-h-[200px]">
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
              <span className="text-blue-600">Analyzing your board...</span>
            </div>
          ) : fullHint ? (
            <div className="space-y-4">
              {/* Suggestion */}
              {fullHint.suggestion && (
                <div className="bg-white rounded-lg p-3 border-l-4 border-green-500">
                  <div className="flex items-center mb-2">
                    <span className="text-2xl mr-2">🎯</span>
                    <span className="font-bold text-green-700">Recommended Move</span>
                  </div>
                  <p className="text-lg font-semibold text-green-800">{fullHint.suggestion}</p>
                </div>
              )}

              {/* Reasoning */}
              {fullHint.reasoning && (
                <div className="bg-white rounded-lg p-3 border-l-4 border-blue-500">
                  <div className="flex items-start mb-2">
                    <span className="text-xl mr-2">🧠</span>
                    <span className="font-bold text-blue-700">Analysis</span>
                  </div>
                  <p className="text-blue-800 leading-relaxed">{fullHint.reasoning}</p>
                </div>
              )}

              {/* Strategy */}
              {fullHint.strategy && (
                <div className="bg-white rounded-lg p-3 border-l-4 border-purple-500">
                  <div className="flex items-start mb-2">
                    <span className="text-xl mr-2">📋</span>
                    <span className="font-bold text-purple-700">Strategy</span>
                  </div>
                  <p className="text-purple-800 leading-relaxed">{fullHint.strategy}</p>
                </div>
              )}

              {/* Alternative Moves */}
              {fullHint.alternatives && fullHint.alternatives.length > 0 && (
                <div className="bg-white rounded-lg p-3 border-l-4 border-orange-500">
                  <div className="flex items-center mb-2">
                    <span className="text-xl mr-2">🔄</span>
                    <span className="font-bold text-orange-700">Alternative Moves</span>
                  </div>
                  <div className="flex gap-2">
                    {fullHint.alternatives.map((move, index) => (
                      <span key={index} className="px-2 py-1 bg-orange-100 text-orange-800 rounded-md text-sm font-medium">
                        {move.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Confidence */}
              {fullHint.confidence && (
                <div className="text-center text-sm text-gray-600">
                  <span>Confidence: </span>
                  <span className="font-medium">{Math.round(fullHint.confidence * 100)}%</span>
                </div>
              )}
            </div>
          ) : hintMessage ? (
            <div>
              <div className="flex items-start mb-2">
                <span className="text-blue-500 mr-2">🤖</span>
                <span className="font-medium text-blue-800">AI Suggestion:</span>
              </div>
              <p className="text-blue-700 leading-relaxed">{hintMessage}</p>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <p>Click Get AI Hint to receive strategic advice for your current board position.</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between space-x-3">        
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            {isLoading ? 'Thinking...' : 'Close'}
          </button>
        </div>

        {/* Usage Info */}
        <div className="text-xs text-gray-500 text-center">
          <p>The AI analyzes your board and suggests the best strategic moves.</p>
        </div>
      </div>
    </Modal>
  );
};

export default AIHintModal;