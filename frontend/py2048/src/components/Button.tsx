import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'move' | 'ghost';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'primary',
  className = ''
}) => {
  const getVariantStyles = () => {
    const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    switch (variant) {
      case 'primary':
        return `${baseStyles} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500`;
      case 'secondary':
        return `${baseStyles} bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500`;
      case 'move':
        return `${baseStyles} bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 text-sm`;
      case 'ghost':
        return `${baseStyles} bg-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-100 focus:ring-gray-500`;
      default:
        return `${baseStyles} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500`;
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${getVariantStyles()} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
