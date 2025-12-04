/**
 * APEX ProspectCard Component
 * Warm Midnight Theme with enrichment controls
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { cardClasses, getScoreClass, getAccentBorder } from '../styles/componentClasses';
import { EnrichmentBadge } from './EnrichmentBadge';
import enrichmentService from '../services/enrichmentService';

interface ProspectCardProps {
  id?: number;
  name: string;
  company?: string;
  email?: string;
  score: number;
  aiReason?: string;
  tags?: string[];
  enrichmentStatus?: 'pending' | 'processing' | 'completed' | 'failed' | 'none';
  lastEnriched?: string;
  onClick?: () => void;
  onEnrichComplete?: () => void;
}

export const ProspectCard: React.FC<ProspectCardProps> = ({
  id,
  name,
  company,
  email,
  score,
  aiReason,
  tags = [],
  enrichmentStatus = 'none',
  lastEnriched,
  onClick,
  onEnrichComplete,
}) => {
  const [isEnriching, setIsEnriching] = useState(false);
  const [localStatus, setLocalStatus] = useState(enrichmentStatus);
  const [error, setError] = useState<string | null>(null);
  
  const isHot = score >= 85;
  const hasAI = !!aiReason;
  const needsEnrichment = !aiReason && localStatus !== 'processing' && localStatus !== 'pending';

  const handleEnrich = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!id || isEnriching) return;

    try {
      setIsEnriching(true);
      setError(null);
      setLocalStatus('processing');

      const response = await enrichmentService.enrichContact(id);
      
      if (response.success) {
        // Poll for completion
        await enrichmentService.waitForEnrichment(id, (status) => {
          setLocalStatus(status.status);
        });

        if (onEnrichComplete) {
          onEnrichComplete();
        }
      } else {
        setError('Enrichment failed');
        setLocalStatus('failed');
      }
    } catch (err) {
      console.error('Enrichment error:', err);
      setError(err instanceof Error ? err.message : 'Failed to enrich');
      setLocalStatus('failed');
    } finally {
      setIsEnriching(false);
    }
  };
  
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
            <p className="text-text-secondary text-sm mb-2">
              {company}
            </p>
          )}
          <EnrichmentBadge status={localStatus} lastEnriched={lastEnriched} />
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
          bg-blue-muted 
          border-l-2 border-blue 
          px-4 py-3 
          rounded-lg 
          mb-4
        ">
          <p className="text-blue text-xs font-semibold mb-1 flex items-center gap-2">
            <span>✨</span> AI Intelligence
          </p>
          <p className="text-text-secondary text-sm italic leading-relaxed">
            {aiReason}
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red bg-opacity-10 border border-red rounded-lg px-4 py-2 mb-4">
          <p className="text-red text-sm">{error}</p>
        </div>
      )}
      
      {/* Actions Row */}
      <div className="flex items-center gap-2 mb-4">
        {email && (
          <a
            href={`mailto:${email}`}
            onClick={(e) => e.stopPropagation()}
            className="
              bg-midnight-800 text-text-secondary px-4 py-2 rounded-lg text-sm
              hover:bg-gold-muted hover:text-gold transition-all
            "
          >
            Email
          </a>
        )}
        
        {needsEnrichment && id && (
          <button
            onClick={handleEnrich}
            disabled={isEnriching}
            className="
              bg-blue-muted text-blue px-4 py-2 rounded-lg text-sm font-semibold
              hover:bg-blue hover:text-midnight-950 transition-all
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {isEnriching ? '⚡ Enriching...' : '⚡ Enrich Now'}
          </button>
        )}
      </div>

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