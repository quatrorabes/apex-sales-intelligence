#!/usr/bin/env python3
import React from 'react';
import { Briefcase, TrendingUp, Award, Users } from 'lucide-react';

interface EnrichmentData {
	profile_text: string;
	sections?: {
		overview: string;
		background: string;
		company_info: string;
		sales_opportunities: string;
	};
	character_count?: number;
	enriched_at?: string;
}

interface EnrichmentDisplayProps {
	data: EnrichmentData;
}

export function EnrichmentDisplay({ data }: EnrichmentDisplayProps) {
	const { sections } = data;
	
	if (!sections) {
		return (
			<div className="bg-white rounded-lg shadow p-6">
				<div className="prose max-w-none">
					<div className="whitespace-pre-wrap">{data.profile_text}</div>
				</div>
			</div>
		);
	}
	
	return (
		<div className="space-y-6">
			{/* Overview Section */}
			{sections.overview && (
				<div className="bg-blue-50 rounded-lg p-6">
					<div className="flex items-center gap-2 mb-4">
						<Users className="w-5 h-5 text-blue-600" />
						<h3 className="text-lg font-semibold text-gray-900">Professional Overview</h3>
					</div>
					<div className="prose max-w-none text-gray-700">
						<div className="whitespace-pre-wrap">{sections.overview}</div>
					</div>
				</div>
			)}
		
			{/* Background Section */}
			{sections.background && sections.background.trim() && (
				<div className="bg-green-50 rounded-lg p-6">
					<div className="flex items-center gap-2 mb-4">
						<Award className="w-5 h-5 text-green-600" />
						<h3 className="text-lg font-semibold text-gray-900">Background & Experience</h3>
					</div>
					<div className="prose max-w-none text-gray-700">
						<div className="whitespace-pre-wrap">{sections.background}</div>
					</div>
				</div>
			)}
		
			{/* Company Info Section */}
			{sections.company_info && sections.company_info.trim() && (
				<div className="bg-purple-50 rounded-lg p-6">
					<div className="flex items-center gap-2 mb-4">
						<Briefcase className="w-5 h-5 text-purple-600" />
						<h3 className="text-lg font-semibold text-gray-900">Company Intelligence</h3>
					</div>
					<div className="prose max-w-none text-gray-700">
						<div className="whitespace-pre-wrap">{sections.company_info}</div>
					</div>
				</div>
			)}
		
			{/* Sales Opportunities Section */}
			{sections.sales_opportunities && sections.sales_opportunities.trim() && (
				<div className="bg-amber-50 rounded-lg p-6">
					<div className="flex items-center gap-2 mb-4">
						<TrendingUp className="w-5 h-5 text-amber-600" />
						<h3 className="text-lg font-semibold text-gray-900">Sales Opportunities</h3>
					</div>
					<div className="prose max-w-none text-gray-700">
						<div className="whitespace-pre-wrap">{sections.sales_opportunities}</div>
					</div>
				</div>
			)}
		
			{/* Metadata Footer */}
			<div className="text-sm text-gray-500 text-center pt-4 border-t">
				Profile enriched • {data.character_count?.toLocaleString()} characters
				{data.enriched_at && ` • ${new Date(data.enriched_at).toLocaleDateString()}`}
			</div>
		</div>
	);
}