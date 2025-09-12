import React, { useEffect } from 'react';

interface MessageBubbleProps {
  message: {
    text: string;
    type: 'success' | 'error' | 'info' | 'warning' | 'hint';
    timestamp: number;
  } | null;
  onDismiss: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onDismiss }) => {
  useEffect(() => {
    if (!message) return;

    // Auto-dismiss non-error messages after 5 seconds
    if (message.type !== 'error') {
      const timer = setTimeout(() => {
        onDismiss();
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [message, onDismiss]);

  if (!message) return null;

  const getStyleClasses = () => {
    switch (message.type) {
      case 'error':
        return 'bg-red-100 border-red-400 text-red-700';
      case 'success':
        return 'bg-green-100 border-green-400 text-green-700';
      case 'hint':
        return 'bg-blue-100 border-blue-400 text-blue-700';
      case 'warning':
        return 'bg-yellow-100 border-yellow-400 text-yellow-700';
      default:
        return 'bg-gray-100 border-gray-400 text-gray-700';
    }
  };

  const getIcon = () => {
    switch (message.type) {
      case 'error':
        return '❌';
      case 'success':
        return '✅';
      case 'hint':
        return '💡';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className={`mb-4 px-4 py-3 rounded border ${getStyleClasses()}`}>
      <div className="flex justify-between items-start">
        <div className="flex items-start">
          <span className="mr-2 flex-shrink-0">{getIcon()}</span>
          <span className="flex-1">{message.text}</span>
        </div>
        <button 
          onClick={onDismiss}
          className="ml-2 text-current hover:opacity-70 flex-shrink-0"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default MessageBubble;