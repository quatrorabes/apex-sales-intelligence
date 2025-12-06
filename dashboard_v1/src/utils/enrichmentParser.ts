/**
 * APEX Enrichment Parser v2
 * Handles: === SECTION === and **SubSection:** formats
 */

// Main section markers (with optional name after colon)
const SECTION_PATTERNS: Record<string, RegExp[]> = {
  person: [
    /===\s*PERSON RESEARCH[^=]*===/i,
    /###\s*PERSON RESEARCH/i,
    /PERSON RESEARCH:/i
  ],
  company: [
    /===\s*COMPANY RESEARCH[^=]*===/i,
    /###\s*COMPANY RESEARCH/i,
    /COMPANY RESEARCH:/i
  ],
  sales: [
    /===\s*SALES INTELLIGENCE[^=]*===/i,
    /###\s*SALES INTELLIGENCE/i,
    /SALES INTELLIGENCE:/i
  ],
  personality: [
    /===\s*PERSONALITY ANALYSIS[^=]*===/i,
    /###\s*PERSONALITY ANALYSIS/i,
    /PERSONALITY ANALYSIS:/i
  ]
};

export function extractSection(content: string | null, sectionType: string): string {
  if (!content) return '';
  
  const patterns = SECTION_PATTERNS[sectionType] || [];
  let startIdx = -1;
  let matchLength = 0;
  
  // Find the section start
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match && match.index !== undefined) {
      startIdx = match.index;
      matchLength = match[0].length;
      break;
    }
  }
  
  if (startIdx === -1) return '';
  
  // Extract from after the marker
  const afterMarker = content.substring(startIdx + matchLength);
  
  // Find next main section (any === marker)
  const nextSection = afterMarker.match(/===\s*(PERSON|COMPANY|SALES|PERSONALITY)/i);
  if (nextSection && nextSection.index !== undefined) {
    return afterMarker.substring(0, nextSection.index).trim();
  }
  
  return afterMarker.trim();
}

interface ParsedSection {
  title: string;
  content: string[];
}

// Parse **Section:** format
export function parseNumberedSections(text: string): ParsedSection[] {
  if (!text) return [];
  
  const sections: ParsedSection[] = [];
  
  // Match **Title:** or **Title** patterns
  const regex = /\*\*([^*:]+):?\*\*\s*([\s\S]*?)(?=\*\*[^*]+:?\*\*|$)/gi;
  
  let match;
  while ((match = regex.exec(text)) !== null) {
    const title = match[1].trim();
    const body = match[2] || '';
    
    // Parse bullet points
    const lines = body
      .split('\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\[\d+\]/g, '').trim())
      .filter(l => l.length > 3 && !l.match(/^-+$/) && !l.startsWith('**'));
    
    if (title && lines.length > 0) {
      sections.push({ title, content: lines });
    }
  }
  
  // If no ** sections found, try numbered format (1. Title)
  if (sections.length === 0) {
    const numRegex = /(\d+)\.\s*([^\n:]+):?\s*([\s\S]*?)(?=\d+\.\s*[A-Z]|$)/gi;
    while ((match = numRegex.exec(text)) !== null) {
      const title = match[2].replace(/\*\*/g, '').trim();
      const body = match[3] || '';
      const lines = body
        .split('\n')
        .map(l => l.replace(/^[-•*]\s*/, '').trim())
        .filter(l => l.length > 3);
      
      if (title && lines.length > 0) {
        sections.push({ title, content: lines });
      }
    }
  }
  
  return sections;
}

export function parseMBTI(text: string) {
  if (!text) return { type: 'N/A', confidence: 'N/A', dimensions: [] };
  
  const typeMatch = text.match(/Inferred Type[:\s]*([A-Z]{4})/i) || 
                    text.match(/MBTI[:\s]*([A-Z]{4})/i) ||
                    text.match(/Type[:\s]*([A-Z]{4})/i);
  const confMatch = text.match(/Confidence[:\s]*(Low|Medium|High)/i);
  
  const dimensions: { dim: string; pref: string; evidence: string }[] = [];
  
  // Table format: | Energy | E - Extraversion | evidence |
  const tableRegex = /\|\s*(Energy|Information|Decisions|Structure)\s*\|\s*([EINSTFJPeinstfjp])\s*[-–]\s*(\w+)\s*\|\s*([^|]+)\|/gi;
  let m;
  while ((m = tableRegex.exec(text)) !== null) {
    dimensions.push({ dim: m[1], pref: `${m[2].toUpperCase()} - ${m[3]}`, evidence: m[4].trim() });
  }
  
  // Line format: Energy: E - Extraversion (evidence)
  if (dimensions.length === 0) {
    const lineRegex = /(Energy|Information|Decisions|Structure)[:\s]*([EINSTFJPeinstfjp])\s*[-–]\s*([^\n(]+)/gi;
    while ((m = lineRegex.exec(text)) !== null) {
      dimensions.push({ dim: m[1], pref: `${m[2].toUpperCase()} - ${m[3].trim()}`, evidence: '' });
    }
  }
  
  return { type: typeMatch?.[1] || 'N/A', confidence: confMatch?.[1] || 'Medium', dimensions };
}

export function parseDISC(text: string) {
  if (!text) return { primary: 'N/A', secondary: 'N/A', styles: [] };
  
  const primMatch = text.match(/Primary[:\s]*([DISC])\s*[-–]\s*(\w+)/i);
  const secMatch = text.match(/Secondary[:\s]*([DISC])\s*[-–]\s*(\w+)/i);
  
  return {
    primary: primMatch ? `${primMatch[1].toUpperCase()} - ${primMatch[2]}` : 'N/A',
    secondary: secMatch ? `${secMatch[1].toUpperCase()} - ${secMatch[2]}` : 'N/A',
    styles: []
  };
}

export function parseCommPlaybook(text: string) {
  const dos: string[] = [];
  const donts: string[] = [];
  let opening = '';
  
  // Match DO section
  const doMatch = text.match(/\*?\*?DO\*?\*?[:\s]*(?:How to Engage)?([\s\S]*?)(?=\*?\*?DON'?T|$)/i);
  if (doMatch) {
    doMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•✓]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DO$/i)) dos.push(cleaned);
    });
  }
  
  // Match DON'T section
  const dontMatch = text.match(/\*?\*?DON'?T\*?\*?[:\s]*(?:What to Avoid)?([\s\S]*?)(?=Best Opening|Opening Approach|$)/i);
  if (dontMatch) {
    dontMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•✗]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DON/i)) donts.push(cleaned);
    });
  }
  
  // Match Opening Approach
  const openMatch = text.match(/(?:Best )?Opening(?: Approach)?[:\s]*([\s\S]*?)(?=\n\n|$)/i);
  if (openMatch) opening = openMatch[1].replace(/\*\*/g, '').trim();
  
  return { dos: dos.slice(0, 5), donts: donts.slice(0, 5), opening };
}
