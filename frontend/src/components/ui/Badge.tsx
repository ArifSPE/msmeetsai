import React from 'react';
import { cn, getStatusColor } from '../../utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'status' | 'priority';
  size?: 'sm' | 'md';
  className?: string;
  status?: string;
}

const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  className,
  status,
}) => {
  const baseClasses = 'inline-flex items-center font-medium rounded-full';
  
  const sizes = {
    sm: 'px-2.5 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };
  
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    status: status ? getStatusColor(status) : 'bg-gray-100 text-gray-800',
    priority: 'bg-blue-100 text-blue-800',
  };
  
  return (
    <span
      className={cn(
        baseClasses,
        sizes[size],
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;