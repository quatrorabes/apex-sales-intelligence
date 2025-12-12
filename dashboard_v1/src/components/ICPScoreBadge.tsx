#!/usr/bin/env python3

import React from 'react';
import { Target, TrendingUp, AlertCircle } from 'lucide-react';

interface ICPScoreBadgeProps {
	score: number;
	matchLevel?: string;
}

export function ICPScoreBadge({ score, matchLevel }: ICPScoreBadgeProps): JSX.Element {
	// Determine color based on score
	const getScoreColor = () => {
		if (score >= 80) return 'emerald';
		if (score >= 60) return 'sky';
		if (score >= 40) return 'amber';
		return 'slate';
	};
	
	const color = getScoreColor();
	const level = matchLevel || (score >= 80 ? 'Perfect' : score >= 60 ? 'Good' : score >= 40 ? 'Okay' : 'Poor');
	
	const colorClasses = {
		emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
		sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
		amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
		slate: 'bg-slate-500/10 text-slate-400 border-slate-500/30'
	};
	
	return (
		<div className="flex items-center gap-3">
			<div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${colorClasses[color]}`}>
				<Target className="h-5 w-5" />
				<div className="flex items-baseline gap-2">
					<span className="text-2xl font-bold">{score}</span>
					<span className="text-sm opacity-70">/ 100</span>
				</div>
			</div>
			<div className="text-sm">
				<div className="font-semibold text-slate-200">{level} Match</div>
				<div className="text-slate-400">ICP Fit Score</div>
			</div>
		</div>
	);
}
