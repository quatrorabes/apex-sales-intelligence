export function mapContactToApexPerson(contact: RawContact): ApexPerson {
  const phone =
    (contact.phonemobile && contact.phonemobile.trim()) ||
    (contact.phone && contact.phone.trim()) ||
    '';

  const linkedin =
    (contact.linkedin_url && contact.linkedin_url.trim()) ||
    (contact.linkedinurl && contact.linkedinurl.trim()) ||
    '';

  const score =
    typeof contact.priorityscore === 'number'
      ? contact.priorityscore
      : typeof contact.mdcpscore === 'number'
      ? contact.mdcpscore
      : 0;

  const companyDomain = (contact.company || '').trim();

  const signals: string[] = [];
  if (contact.persona) {
    signals.push(`Persona: ${contact.persona}`);
  }
  if (contact.enrichmentstatus) {
    signals.push(`Enrichment: ${contact.enrichmentstatus}`);
  }
  if (contact.urgencylevel) {
    signals.push(`Urgency: ${contact.urgencylevel}`);
  }

  return {
    apexPersonId: String(contact.id),
    fullName: contact.name || 'Unknown',
    emailAddress: contact.email || '',
    jobTitle: contact.title || '',
    companyDomain,
    phoneNumber: phone,
    linkedinProfile: linkedin,
    intelligenceScore: Math.max(0, Math.min(100, score || 0)),
    engagementStage: mapEngagementStage(contact),
    lastActivityDate: contact.lastcontactdate || '',
    apexSignals: signals,
  };
}
