// Example: PersonTable.tsx
import React from 'react';
import { ApexPerson } from '../apex-intelligence/types';

interface PersonTableProps {
  persons: ApexPerson[];
  onPersonSelect: (p: ApexPerson) => void;
}

export function PersonTable({ persons, onPersonSelect }: PersonTableProps) {
  return (
    <div>
      {persons.map((p) => (
        <div
          key={p.apexPersonId}
          onClick={() => onPersonSelect(p)}
          style={{ cursor: 'pointer', padding: '8px 12px' }}
        >
          <div style={{ fontWeight: 600 }}>{p.fullName}</div>
          <div style={{ fontSize: 12, opacity: 0.7 }}>
            {p.jobTitle} • {p.companyDomain}
          </div>
          <div style={{ fontSize: 12, color: '#818cf8' }}>
            Intelligence {p.intelligenceScore.toFixed(0)} / 100 • {p.engagementStage}
          </div>
        </div>
      ))}
    </div>
  );
}
