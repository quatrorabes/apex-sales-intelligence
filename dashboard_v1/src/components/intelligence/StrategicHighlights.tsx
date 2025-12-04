import { Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { OpportunityBadge } from './OpportunityBadge';

interface StrategicHighlightsProps {
  opening_line?: string;
  opportunity_level?: string;
  top_reasons?: string;
}

export function StrategicHighlights({ 
  opening_line, 
  opportunity_level,
  top_reasons 
}: StrategicHighlightsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (opening_line) {
      await navigator.clipboard.writeText(opening_line);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Parse top reasons
  const reasons = top_reasons
    ?.split('\n')
    .filter(line => line.trim().match(/^[\d.]/))
    .map(line => line.replace(/^[\d.\s]+/, '').trim())
    .filter(r => r.length > 10) || [];

  return (
    <div className="bg-gradient-to-br from-gold/10 via-midnight-900 to-midnight-900 border border-gold/30 rounded-xl p-6 space-y-6">
      {/* Opportunity Level */}
      {opportunity_level && (
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-text-primary">Opportunity Assessment</h3>
          <OpportunityBadge level={opportunity_level} size="lg" />
        </div>
      )}

      {/* Opening Line */}
      {opening_line && (
        <div className="bg-midnight-900 rounded-lg p-4 border border-midnight-700">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h4 className="text-sm font-semibold text-gold">💬 Recommended Opening Line</h4>
            <button
              onClick={handleCopy}
              className="p-1.5 hover:bg-midnight-800 rounded transition-all flex-shrink-0"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-text-secondary" />
              )}
            </button>
          </div>
          <p className="text-text-secondary italic leading-relaxed">
            "{opening_line}"
          </p>
        </div>
      )}

      {/* Top Reasons */}
      {reasons.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gold mb-3">🎯 Top Reasons to Engage</h4>
          <div className="space-y-2">
            {reasons.map((reason, index) => (
              <div key={index} className="flex items-start gap-3">
                <span className="text-gold font-bold flex-shrink-0 w-6 h-6 flex items-center justify-center bg-gold/20 rounded-full text-sm">
                  {index + 1}
                </span>
                <p className="text-text-secondary text-sm leading-relaxed flex-1">{reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}