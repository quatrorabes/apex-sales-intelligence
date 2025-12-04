/**
 * Enrichment Status Badge Component
 */
import React from 'react';
import { motion } from 'framer-motion';

interface EnrichmentBadgeProps {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'none';
  lastEnriched?: string;
}

export const EnrichmentBadge: React.FC<EnrichmentBadgeProps> = ({ status, lastEnriched }) => {
  const configs = {
    processing: {
      bg: 'bg-blue-muted',
      text: 'text-blue',
      border: 'border-blue',
      icon: '⚡',
      label: 'AI Processing',
      animate: true,
    },
    completed: {
      bg: 'bg-lime bg-opacity-10',
      text: 'text-lime',
      border: 'border-lime border-opacity-50',
      icon: '✓',
      label: 'Enriched',
      animate: false,
    },
    failed: {
      bg: 'bg-red bg-opacity-10',
      text: 'text-red',
      border: 'border-red border-opacity-50',
      icon: '⚠',
      label: 'Failed',
      animate: false,
    },
    pending: {
      bg: 'bg-coral bg-opacity-10',
      text: 'text-coral',
      border: 'border-coral border-opacity-50',
      icon: '⏳',
      label: 'Queued',
      animate: false,
    },
    none: {
      bg: 'bg-midnight-800',
      text: 'text-text-tertiary',
      border: 'border-midnight-600',
      icon: '○',
      label: 'Not Enriched',
      animate: false,
    },
  };

  const config = configs[status];

  return (
    <motion.div
      className={`
        inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold
        ${config.bg} ${config.text} border ${config.border}
      `}
      animate={config.animate ? { opacity: [0.6, 1, 0.6] } : {}}
      transition={{ duration: 2, repeat: Infinity }}
    >
      <span>{config.icon}</span>
      <span>{config.label}</span>
      {lastEnriched && status === 'completed' && (
        <span className="text-text-tertiary">• {new Date(lastEnriched).toLocaleDateString()}</span>
      )}
    </motion.div>
  );
};