import { 
  enrichContact, 
  getEnrichmentStatus, 
  type ContactId 
} from "../api";

export async function startEnrichment(contactId: ContactId) {
  return enrichContact(contactId, true);
}

export async function pollEnrichment(contactId: ContactId) {
  return getEnrichmentStatus(contactId);
}
