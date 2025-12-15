export interface Contact {
	id: number;
	name: string;
	title: string;
	company: string;
	email?: string;
	phone?: string;
	phone_mobile?: string;
	linkedin_url?: string;
	profile_content?: string;
	enrichment_status: 'pending' | 'completed' | 'failed';
	enrichment_date?: string;
	persona?: string;
	personaconfidence?: number;
	mdcp_score?: number;
	priority_score?: number;
	rss_score?: number;
	mdcp_tier?: string;
	urgency_level?: string;
	created_at: string;
	updated_at: string;
	last_contact_date?: string;
}

export interface TodaysBoardData {
	date: string;
	recommendation: string;
	relationships: {
		urgent: Contact[];
		warm: Contact[];
		nurture: Contact[];
		stable: Contact[];
	};
	newprospects: {
		tiers: {
			hot: Contact[];
			qualified: Contact[];
			potential: Contact[];
		};
	};
}

export interface TodaysBoardContact extends Contact {
	board_reason?: string;
	recommended_action?: string;
}

export interface ScoreBreakdown {
	mdcp_score: number;
	mdcp_tier: string;
	priority_score: number;
	urgency_level: string;
	rss_score: number;
	rss_tier: string;
	recommended_action: string;
}

export interface ApiResponse<T> {
	success: boolean;
	data?: T;
	error?: string;
	message?: string;
}
