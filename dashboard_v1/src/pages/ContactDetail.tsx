#!/bin/bash

// dashboard_v1/src/pages/ContactDetail.tsx
// VERSION: Apex-v1.0-ExactLayout | Dec 15, 2025
// Layout matches ContactDetailPage-copy-2.tsx reference file

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
	ArrowLeft, Briefcase, Building2, Mail, Phone, Linkedin, MapPin,
	TrendingUp, GraduationCap, User, MessageSquare, Brain,
	FileText, Layers, Target, Zap, Loader2, Download
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

// ============================================================================
// TYPES
// ============================================================================

interface Contact {
	id: string;
	first_name: string;
	lastname: string;
	email: string;
	phone: string;
	company: string;
	title: string;
	enrichment_status: string;
	enrichment?: any;
	enrichment_data?: string | any;
	profile_content?: string;
	linkedin_url?: string;
	last_enriched?: string;
}

// ============================================================================
// PARSING HELPERS
// ============================================================================

function getSectionsFromEnrichment(contact: Contact): any | null {
	const enrichment = contact.enrichment || contact.enrichment_data;
	
	if (!enrichment) {
		const raw = contact.profile_content || '';
		if (raw && raw.length > 100) {
			return parseRawProfileLegacy(raw);
		}
		return null;
	}
	
	// If enrichment is string, parse it
	if (typeof enrichment === 'string') {
		try {
			const parsed = JSON.parse(enrichment);
			if (parsed.sections && Object.keys(parsed.sections).length > 0) {
				return parsed.sections;
			}
			return parseRawProfileLegacy(enrichment);
		} catch {
			return parseRawProfileLegacy(enrichment);
		}
	}
	
	// If enrichment is object
	if (enrichment.sections && Object.keys(enrichment.sections).length > 0) {
		return enrichment.sections;
	}
	
	const raw = enrichment.raw_profile || contact.profile_content || '';
	if (raw && raw.length > 100) {
		return parseRawProfileLegacy(raw);
	}
	
	return null;
}

function parseRawProfileLegacy(raw: string): any {
	const sections: any = {};
	sections.person_research = extractSection(raw, 'person');
	sections.company_research = extractSection(raw, 'company');
	sections.sales_intelligence = extractSection(raw, 'sales');
	sections.personality_analysis = extractSection(raw, 'personality');
	return sections;
}

function extractSection(content: string, type: 'person' | 'company' | 'sales' | 'personality'): string {
	if (!content) return '';
	
	const markdownPatterns: Record<string, RegExp[]> = {
		person: [
			/###?\s*(?:Professional|Person|Executive)[\s\S]*?(?=###?\s|$)/i,
		],
		company: [
			/###?\s*(?:Company|Organization)[\s\S]*?(?=###?\s|$)/i,
		],
		sales: [
			/###?\s*(?:Sales|Opportunities)[\s\S]*?(?=###?\s|$)/i,
		],
		personality: [
			/###?\s*(?:Personality|Personal)[\s\S]*?(?=###?\s|$)/i,
		]
	};
	
	for (const pattern of markdownPatterns[type]) {
		const match = content.match(pattern);
		if (match) return match[0];
	}
	
	return '';
}

function parseStarSections(text: string): string[] {
	if (!text) return [];
	const matches = text.match(/\*\*[^*]+\*\*:?[^\n]+/g);
	return matches || [];
}

function parseNumberedSections(text: string): string[] {
	if (!text) return [];
	const matches = text.match(/\d+\.\s*\*\*[^*]+\*\*[^\n]+/g);
	return matches || [];
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function ContactDetail() {
	const { id } = useParams<{ id: string }>();
	const navigate = useNavigate();
	
	const [contact, setContact] = useState<Contact | null>(null);
	const [loading, setLoading] = useState(true);
	const [enriching, setEnriching] = useState(false);
	const [mainTab, setMainTab] = useState<'profile' | 'intelligence' | 'outreach'>('profile');
	
	useEffect(() => {
		if (!id) return;
		fetchContact();
	}, [id]);
	
	async function fetchContact() {
		try {
			setLoading(true);
			const res = await fetch(`${API_BASE}/api/contacts/${id}`);
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const data = await res.json();
			setContact(data);
		} catch (err: any) {
			console.error('Failed to load contact:', err);
		} finally {
			setLoading(false);
		}
	}
	
	async function handleEnrich() {
		if (!id) return;
		try {
			setEnriching(true);
			const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
			if (!res.ok) throw new Error(`Enrichment failed: ${res.status}`);
			await fetchContact();
		} catch (err: any) {
			alert(err.message || 'Enrichment error');
		} finally {
			setEnriching(false);
		}
	}
	
	if (loading) {
		return (
			<div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
				<Loader2 className="animate-spin text-blue-500" size={32} />
			</div>
		);
	}
	
	if (!contact) {
		return (
			<div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-[#8b919a]">
				Contact not found
			</div>
		);
	}
	
	// Parse enrichment data
	const sections = getSectionsFromEnrichment(contact);
	const rawText = contact.enrichment?.raw_profile || contact.profile_content || '';
	const isEnriched = contact.enrichment_status === 'completed' && !!sections;
	
	const personSection =
		sections?.person_overview ||
		sections?.person_profile ||
		sections?.person_research ||
		'';
	
	const companySection =
		sections?.company_overview ||
		sections?.company_intelligence ||
		sections?.company_research ||
		'';
	
	const salesSection =
		sections?.sales_opportunities ||
		sections?.sales_intelligence ||
		'';
	
	const personalitySection =
		sections?.personality_analysis ||
		'';
	
	const personCards = parseStarSections(personSection);
	const companyCards = parseNumberedSections(companySection);
	const salesCards = parseStarSections(salesSection);
	
	return (
		<div className="min-h-screen bg-[#0d1117] text-white">
			{/* HEADER */}
			<div className="bg-[#161b22] border-b border-[#30363d] px-6 py-4">
				<div className="max-w-6xl mx-auto">
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-4">
							<button
								onClick={() => navigate('/contacts')}
								className="text-[#8b919a] hover:text-white transition"
							>
								<ArrowLeft size={20} />
							</button>
							<div>
								<h1 className="text-2xl font-bold text-white">
									{contact.first_name} {contact.lastname}
								</h1>
								<p className="text-[#8b919a] text-sm">
									{contact.title} • {contact.company}
								</p>
							</div>
						</div>
						<div className="flex gap-3">
							<button
								onClick={handleEnrich}
								disabled={enriching}
								className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition disabled:opacity-50"
							>
								{enriching ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
								{enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich'}
							</button>
						</div>
					</div>
				</div>
			</div>
		
			{/* CONTACT INFO */}
			<div className="max-w-6xl mx-auto px-6 py-6">
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
					<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
						<div className="flex items-center gap-3 text-[#8b919a] mb-2">
							<Mail size={16} />
							<span className="text-xs uppercase">Email</span>
						</div>
						<p className="text-white">{contact.email || 'N/A'}</p>
					</div>
					<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
						<div className="flex items-center gap-3 text-[#8b919a] mb-2">
							<Phone size={16} />
							<span className="text-xs uppercase">Phone</span>
						</div>
						<p className="text-white">{contact.phone || 'N/A'}</p>
					</div>
					<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
						<div className="flex items-center gap-3 text-[#8b919a] mb-2">
							<Linkedin size={16} />
							<span className="text-xs uppercase">LinkedIn</span>
						</div>
						<p className="text-white">
							{contact.linkedin_url ? (
								<a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
									View Profile
								</a>
							) : (
								'N/A'
							)}
						</p>
					</div>
				</div>
		
				{/* TABS */}
				<div className="flex gap-2 mb-6 border-b border-[#30363d]">
					<button
						onClick={() => setMainTab('profile')}
						className={`px-4 py-2 flex items-center gap-2 ${
							mainTab === 'profile'
								? 'text-white border-b-2 border-blue-500'
								: 'text-[#8b919a] hover:text-white'
						}`}
					>
						<User size={18} />
						Profile
					</button>
					<button
						onClick={() => setMainTab('intelligence')}
						className={`px-4 py-2 flex items-center gap-2 ${
							mainTab === 'intelligence'
								? 'text-white border-b-2 border-blue-500'
								: 'text-[#8b919a] hover:text-white'
						}`}
					>
						<Brain size={18} />
						Intelligence
					</button>
					<button
						onClick={() => setMainTab('outreach')}
						className={`px-4 py-2 flex items-center gap-2 ${
							mainTab === 'outreach'
								? 'text-white border-b-2 border-blue-500'
								: 'text-[#8b919a] hover:text-white'
						}`}
					>
						<MessageSquare size={18} />
						Outreach
					</button>
				</div>
		
				{/* PROFILE TAB */}
				{mainTab === 'profile' && (
					<div className="space-y-6">
						{!isEnriched && (
							<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8 text-center">
								<p className="text-[#8b919a] mb-4">
									Click "Enrich" to generate professional intelligence
								</p>
							</div>
						)}
					
						{isEnriched && (
							<>
								{/* Person Research */}
								{personSection && (
									<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
										<h2 className="text-xl font-bold mb-4 flex items-center gap-2">
											<User className="text-blue-400" />
											Professional Profile
										</h2>
										<div className="space-y-2 text-sm text-[#c9d1d9]">
											{personCards.map((card, i) => (
												<div key={i} className="py-2">
													{card}
												</div>
											))}
										</div>
									</div>
								)}
							
								{/* Company Research */}
								{companySection && (
									<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
										<h2 className="text-xl font-bold mb-4 flex items-center gap-2">
											<Building2 className="text-green-400" />
											Company Intelligence
										</h2>
										<div className="space-y-2 text-sm text-[#c9d1d9]">
											{companyCards.map((card, i) => (
												<div key={i} className="py-2">
													{card}
												</div>
											))}
										</div>
									</div>
								)}
							
								{/* Personality Analysis */}
								{personalitySection && (
									<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
										<h2 className="text-xl font-bold mb-4 flex items-center gap-2">
											<Brain className="text-purple-400" />
											Personality Analysis
										</h2>
										<div className="text-sm text-[#c9d1d9] whitespace-pre-wrap">
											{personalitySection.substring(0, 500)}...
										</div>
									</div>
								)}
							
								{/* Raw Data */}
								{rawText && (
									<details className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
										<summary className="cursor-pointer text-[#8b919a] hover:text-white">
											View Raw Data
										</summary>
										<pre className="mt-4 text-xs text-[#8b919a] overflow-auto max-h-96">
											{rawText || 'No raw data available'}
										</pre>
									</details>
								)}
							</>
						)}
					</div>
				)}
		
				{/* INTELLIGENCE TAB */}
				{mainTab === 'intelligence' && (
					<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8 text-center">
						<Target className="w-16 h-16 mx-auto mb-4 text-[#8b919a]" />
						<p className="text-[#8b919a]">
							Coming soon: Pain points, buying triggers, and engagement strategy
						</p>
					</div>
				)}
		
				{/* OUTREACH TAB */}
				{mainTab === 'outreach' && (
					<div className="bg-[#161b22] border border-[#30363d] rounded-lg p-8 text-center">
						<MessageSquare className="w-16 h-16 mx-auto mb-4 text-[#8b919a]" />
						<p className="text-[#8b919a]">
							Coming soon: Email drafts, LinkedIn messages, and call scripts
						</p>
					</div>
				)}
			</div>
		</div>
	);
}