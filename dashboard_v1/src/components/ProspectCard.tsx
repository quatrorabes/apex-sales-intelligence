/**
 * APEX ProspectCard Component
 * Warm Midnight Theme with accent borders & glow effects
 */
import React from 'react';
import { motion } from 'framer-motion';
import { cardClasses, getScoreClass, getAccentBorder } from '../styles/componentClasses';

interface ProspectCardProps {
  name: string;
  company?: string;
  score: number;
  aiReason?: string;
  tags?: string[];
  onClick?: () => void;
}

export const ProspectCard: React.FC<ProspectCardProps> = ({
  name,
  company,
  score,
  aiReason,
  tags = [],
  onClick,
}) => {
  const isHot = score >= 85;
  const hasAI = !!aiReason;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={`
        ${cardClasses.interactive}
        ${getAccentBorder(score, hasAI)}
        p-6 relative
      `}
      onClick={onClick}
    >
      {/* Header Row */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-text-primary text-lg font-semibold mb-1">
            {name}
          </h3>
          {company && (
            <p className="text-text-secondary text-sm">
              {company}
            </p>
          )}
        </div>
        
        {/* Score Badge */}
        <motion.div
          className={`
            ${getScoreClass(score)}
            text-3xl
            ml-4
          `}
          animate={isHot ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {score}
        </motion.div>
      </div>
      
      {/* AI Reason */}
      {aiReason && (
        <div className="
          bg-violet-muted 
          border-l-2 border-violet 
          px-4 py-3 
          rounded-lg 
          mb-4
        ">
          <p className="text-violet text-sm italic leading-relaxed">
            {aiReason}
          </p>
        </div>
      )}
      
      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, idx) => (
            <span
              key={idx}
              className="
                bg-midnight-800 
                text-text-secondary 
                px-3 py-1 
                rounded-full 
                text-xs
                border border-midnight-600
              "
            >
              {tag}
            </span>
          ))}
        </div>
      )}
      
      {/* Hot Glow Effect */}
      {isHot && (
        <div className="
          absolute inset-0 
          rounded-card 
          shadow-gold-glow 
          pointer-events-none
        " />
      )}
    </motion.div>
  );
};