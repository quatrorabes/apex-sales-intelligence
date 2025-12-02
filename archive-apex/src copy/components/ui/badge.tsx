import React from 'react';

export const Badge = ({ 
  children, 
  variant = 'default',
  className = '' 
}: { 
  children: React.ReactNode; 
  variant?: string;
  className?: string 
}) => (
  <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md ${className}`}>
    {children}
  </span>
);
