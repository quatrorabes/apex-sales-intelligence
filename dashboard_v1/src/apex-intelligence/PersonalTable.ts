// src/apex-intelligence/PersonalTable.ts
export interface PersonalInsight {
  category: string;
  value: string;
  confidence: number;
}

export interface PersonalProfile {
  mbti?: string;
  disc?: string;
  insights: PersonalInsight[];
}

export const parsePersonalData = (data: string): PersonalProfile => {
  try {
    return JSON.parse(data);
  } catch {
    return { insights: [] };
  }
};
