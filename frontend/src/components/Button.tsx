import React from 'react';

type ButtonVariant = "primary" | "destructive" | "outline";

interface ButtonProps {
  text: string;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  title?: string;
  variant?: ButtonVariant;
}

const Button: React.FC<ButtonProps> = ({ 
  text, 
  onClick, 
  className = "", 
  disabled = false, 
  icon,
  title,
  variant = "primary"
}) => {

  // Clases base
  const baseStyles = "flex items-center justify-center cursor-pointer rounded-[8px]";

  // Clases por variante
  const variantStyles: Record<ButtonVariant, string> = {
    primary:    "bg-primary text-white hover:opacity-95",
    destructive:"bg-red-700 text-white hover:bg-red-800", 
    outline:    "bg-secondary border border-slate-400 text-slate-700 hover:bg-slate-100",
  };

  // Combinar la variante seleccionada + clases extra
  const classes = `${baseStyles} ${variantStyles[variant]} ${className}`;

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={classes}
    >
      {icon && <span>{icon}</span>}
      <span>{text}</span>
    </button>
  );
};

export default Button;