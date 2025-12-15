import React from 'react';

interface PersonaBadgeProps {
  persona?: string;
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
}

const PERSONA_CONFIG: Record<string, { color: string; icon: string; label: string }> = {
  banker: { color: 'bg-blue-100 text-blue-800 border-blue-300', icon: '🏦', label: 'Banker' },
  sba_banker: { color: 'bg-cyan-100 text-cyan-800 border-cyan-300', icon: '📊', label: 'SBA Banker' },
  loan_broker: { color: 'bg-purple-100 text-purple-800 border-purple-300', icon: '🤝', label: 'Loan Broker' },
  sales_broker: { color: 'bg-amber-100 text-amber-800 border-amber-300', icon: '🏢', label: 'Sales Broker' },
  referral_network_other: { color: 'bg-green-100 text-green-800 border-green-300', icon: '🌐', label: 'Referral Network' },
  internal: { color: 'bg-red-100 text-red-800 border-red-300', icon: '⚙️', label: 'Internal' },
  borrower: { color: 'bg-indigo-100 text-indigo-800 border-indigo-300', icon: '👔', label: 'Borrower' },
  past_borrower: { color: 'bg-gray-100 text-gray-800 border-gray-300', icon: '👵', label: 'Past Borrower' },
  unclassified: { color: 'bg-slate-100 text-slate-800 border-slate-300', icon: '❓', label: 'Unclassified' },
};

export const PersonaBadge: React.FC<PersonaBadgeProps> = ({ 
  persona = 'unclassified', 
  confidence = 0,
  size = 'md' 
}) => {
  const config = PERSONA_CONFIG[persona] || PERSONA_CONFIG.unclassified;
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span 
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${config.color} ${sizeClasses[size]}`}
      title={`${config.label} (${Math.round(confidence)}% confidence)`}
    >
      <span>{config.icon}</span>
      <span>{config.label}</span>
      {confidence > 0 && size !== 'sm' && (
        <span className="opacity-75 ml-1">({Math.round(confidence)}%)</span>
      )}
    </span>
  );
};
