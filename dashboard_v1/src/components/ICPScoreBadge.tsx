import React from 'react';
import { Target } from 'lucide-react';

interface ICPScoreBadgeProps {
  score: number;
  matchLevel?: string;
}

export function ICPScoreBadge({ score, matchLevel }: ICPScoreBadgeProps): JSX.Element {
  const getScoreColor = () => {
    if (score >= 80) return 'emerald';
    if (score >= 60) return 'sky';
    if (score >= 40) return 'amber';
    return 'slate';
  };

  const color = getScoreColor();
  const level = matchLevel || (score >= 80 ? 'Perfect' : score >= 60 ? 'Good' : score >= 40 ? 'Okay' : 'Poor');

  const colorClasses: Record<string, string> = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    slate: 'bg-slate-500/10 text-slate-400 border-slate-500/30'
  };

  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg border ${colorClasses[color]}`}>
      <Target className="w-3.5 h-3.5" />
      <span className="text-xs font-semibold">{score}</span>
      <span className="text-xs opacity-70">• {level}</span>
    </div>
  );
}

export default ICPScoreBadge;
