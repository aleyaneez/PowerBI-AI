import React from 'react';

interface ButtonProps {
  text: string;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  title?: string;
}

const Button: React.FC<ButtonProps> = ({ 
  text, 
  onClick, 
  className = "", 
  disabled = false, 
  icon,
  title
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`${className} flex items-center justify-center cursor-pointer bg-primary text-white rounded-[8px]`}
    >
      {icon && <span>{icon}</span>}
      <span>{text}</span>
    </button>
  );
};

export default Button;