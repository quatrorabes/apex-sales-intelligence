/**
 * APEX KPICard Component
 * Animated metric cards with spring physics
 */
import React from 'react';
import { motion } from 'framer-motion';
import { cardClasses } from '../styles/componentClasses';

interface KPICardProps {
  label: string;
  value: string | number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  delay?: number;
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  trend,
  icon,
  delay = 0,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 24,
        delay,
      }}
      className={`${cardClasses.base} p-6`}
    >
      {/* Icon */}
      {icon && (
        <div className="text-gold mb-3 opacity-80">
          {icon}
        </div>
      )}
      
      {/* Label */}
      <p className="text-text-tertiary text-sm uppercase tracking-wide mb-2">
        {label}
      </p>
      
      {/* Value */}
      <motion.p
        className="text-text-primary text-4xl font-bold mb-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.2 }}
      >
        {value}
      </motion.p>
      
      {/* Trend */}
      {trend && (
        <div className={`
          flex items-center gap-2 text-sm font-semibold
          ${trend.isPositive ? 'text-lime' : 'text-coral'}
        `}>
          <span>{trend.isPositive ? '↑' : '↓'}</span>
          <span>{Math.abs(trend.value)}%</span>
        </div>
      )}
    </motion.div>
  );
};