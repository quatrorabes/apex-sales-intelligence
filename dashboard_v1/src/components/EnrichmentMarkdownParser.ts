/**
 * Parse enrichment markdown into sections
 * Pure utility - no dependencies needed
 */

export function parseEnrichmentMarkdown(markdown: string): Record<string, string> {
  const sections: Record<string, string> = {};
  
  if (!markdown || !markdown.trim()) {
    return sections;
  }
  
  // Split by ## headers
  const parts = markdown.split(/^## /m);
  
  for (const part of parts) {
    if (!part.trim()) continue;
    
    const lines = part.split('\n');
    const header = lines[0].trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '');
    
    const content = lines.slice(1).join('\n').trim();
    
    if (header && content) {
      sections[header] = content;
    }
  }
  
  return sections;
}

export interface EnrichmentSections {
  [key: string]: string;
}

export function getPrettyHeaderName(key: string): string {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function formatEnrichmentContent(content: string): string {
  // Format markdown-like content for display
  return content
    .split('\n')
    .filter(line => line.trim())
    .map(line => line.trim())
    .join('\n');
}
