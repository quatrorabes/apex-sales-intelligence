import { apiUrl } from "./config/api";

export type EnrichmentStatus = "pending" | "enriching" | "completed" | "failed";

// Contact IDs are UUID strings, not integers
export type ContactId = string;

export type Contact = {
  id: ContactId;
  name?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  industry?: string | null;
  linkedin_url?: string | null;

  enrichment_status?: EnrichmentStatus | string;
  enrichment?: any;
  enrichment_data?: any;

  apex_score?: number;
  mdcp_score?: number;
  rss_score?: number;
  bant_total_score?: number;
  spice_total_score?: number;
  priority_score?: number;
  match_score?: number;
  match_tier?: string;
};

type ApiErrorShape = { 
  detail?: string; 
  message?: string; 
  status_code?: number 
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    let err: ApiErrorShape | string = await res.text();
    try { 
      err = JSON.parse(err as string); 
    } catch {}
    
    const msg =
      typeof err === "string"
        ? err
        : err.detail || err.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return (await res.json()) as T;
}

/**
 * Primary list endpoint with fallback to todays-board
 */
export async function getContacts(limit = 50, offset = 0) {
  try {
    return await apiFetch<{
      success: boolean;
      contacts: Contact[];
      total: number;
      limit: number;
      offset: number;
    }>(`/api/v2/contacts?limit=${limit}&offset=${offset}`);
  } catch {
    // Fallback: flatten segments from todays-board
    const board = await apiFetch<{
      success: boolean;
      stats?: any;
      segments: { 
        high: Contact[]; 
        medium: Contact[]; 
        low: Contact[] 
      };
    }>(`/api/todays-board`);

    const contacts = [
      ...(board.segments?.high || []), 
      ...(board.segments?.medium || []), 
      ...(board.segments?.low || [])
    ];
    
    return { 
      success: true, 
      contacts, 
      total: contacts.length, 
      limit, 
      offset 
    };
  }
}

export async function getContact(id: ContactId) {
  return await apiFetch<{ 
    success: boolean; 
    contact: Contact 
  }>(`/api/contacts/${id}`);
}

export async function enrichContact(id: ContactId, asyncmode = true) {
  const qs = asyncmode ? "?asyncmode=true" : "";
  return await apiFetch<any>(`/api/contacts/${id}/enrich${qs}`, { 
    method: "POST" 
  });
}

/**
 * REQUIRED: Poll enrichment status for a contact
 * Used by enrichmentService for polling loop
 */
export async function getEnrichmentStatus(id: ContactId) {
  return await apiFetch<{
    contact_id: ContactId;
    status: EnrichmentStatus;
    last_enriched?: string | null;
    sections_count?: number;
    character_count?: number;
  }>(`/api/contacts/${id}/enrichment-status`);
}

export async function scoreContact(id: ContactId) {
  return await apiFetch<any>(`/api/contacts/${id}/score`, { 
    method: "POST" 
  });
}

export async function getTodaysBoard() {
  return await apiFetch<{
    success: boolean;
    date: string;
    time: string;
    stats: any;
    segments: {
      high: Contact[];
      medium: Contact[];
      low: Contact[];
    };
  }>(`/api/todays-board`);
}
