import { useEffect, useState } from 'react';
import api from '../services/api';

interface Contact {
  id: number;
  name: string;
  company: string;
  email: string;
  title: string;
  urgency_tier?: string;
  urgency_label?: string;
  why_now?: string;
  contact_type?: string;
  mdcp_score?: number;
  priority_score?: number;
}

interface BoardData {
  success: boolean;
  date: string;
  time: string;
  total_actions: number;
  recommendation: string;
  relationships: {
    total: number;
    urgent_count: number;
    warm_count: number;
    nurture_count: number;
    stable_count: number;
    tiers: {
      urgent: Contact[];
      warm: Contact[];
      nurture: Contact[];
      stable: Contact[];
    };
  };
  new_prospects: {
    total: number;
    hot_count: number;
    qualified_count: number;
    potential_count: number;
    tiers: {
      hot: Contact[];
      qualified: Contact[];
      potential: Contact[];
    };
  };
}

export default function TodaysBoard() {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBoard = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/api/todays-board');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Today\'s Board API Response:', data);
      setBoard(data);
    } catch (err) {
      console.error('Failed to fetch Today\'s Board:', err);
      setError(err instanceof Error ? err.message : 'Failed to load board');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoard();
    const interval = setInterval(fetchBoard, 300000); // Refresh every 5 min
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Today's Board...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold mb-2">⚠️ Error Loading Board</h3>
          <p className="text-red-600 text-sm">{error}</p>
          <p className="text-red-500 text-xs mt-2">Make sure the backend is running on http://localhost:8000</p>
          <button
            onClick={fetchBoard}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!board) return null;

  // Extract contacts from the new API structure
  const urgentContacts = board.relationships?.tiers?.urgent || [];
  const warmContacts = board.relationships?.tiers?.warm || [];
  const nurtureContacts = board.relationships?.tiers?.nurture || [];
  const stableContacts = board.relationships?.tiers?.stable || [];
  
  const hotProspects = board.new_prospects?.tiers?.hot || [];
  const qualifiedProspects = board.new_prospects?.tiers?.qualified || [];
  const potentialProspects = board.new_prospects?.tiers?.potential || [];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📋 Today's Board</h1>
        <p className="text-gray-600">{board.date} • {board.time}</p>
        <p className="text-lg font-semibold text-indigo-600 mt-2">{board.recommendation}</p>
      </div>

      {/* Urgent Relationships */}
      {urgentContacts.length > 0 && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-500 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-800 mb-4">
            🔥 URGENT - {urgentContacts.length} Relationship{urgentContacts.length !== 1 ? 's' : ''} Going Cold
          </h2>
          <div className="space-y-3">
            {urgentContacts.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Hot Prospects */}
      {hotProspects.length > 0 && (
        <div className="mb-6 bg-green-50 border-l-4 border-green-500 rounded-lg p-6">
          <h2 className="text-xl font-bold text-green-800 mb-4">
            🎯 HOT PROSPECTS - {hotProspects.length} Ready to Call
          </h2>
          <div className="space-y-3">
            {hotProspects.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Warm Relationships */}
      {warmContacts.length > 0 && (
        <div className="mb-6 bg-orange-50 border-l-4 border-orange-500 rounded-lg p-6">
          <h2 className="text-xl font-bold text-orange-800 mb-4">
            ⏰ THIS WEEK - {warmContacts.length} Warm Relationship{warmContacts.length !== 1 ? 's' : ''}
          </h2>
          <div className="space-y-3">
            {warmContacts.slice(0, 5).map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Qualified Prospects */}
      {qualifiedProspects.length > 0 && (
        <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6">
          <h2 className="text-xl font-bold text-blue-800 mb-4">
            ✅ QUALIFIED - {qualifiedProspects.length} Prospect{qualifiedProspects.length !== 1 ? 's' : ''}
          </h2>
          <div className="space-y-3">
            {qualifiedProspects.slice(0, 5).map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {board.total_actions === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 text-lg">No actions for today</p>
          <p className="text-gray-400 text-sm mt-2">Enrich and score contacts to populate your board</p>
        </div>
      )}
    </div>
  );
}

function ContactCard({ contact }: { contact: Contact }) {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{contact.name}</h3>
          <p className="text-sm text-gray-600">{contact.title} at {contact.company}</p>
          {contact.why_now && (
            <p className="text-sm text-gray-500 mt-1 italic">{contact.why_now}</p>
          )}
        </div>
        <div className="text-right ml-4">
          {contact.urgency_label && (
            <span className="text-sm font-semibold">{contact.urgency_label}</span>
          )}
          {contact.mdcp_score && (
            <p className="text-xs text-gray-500 mt-1">Score: {contact.mdcp_score}</p>
          )}
        </div>
      </div>
      <div className="mt-3 flex gap-2">
        <a
          href={`mailto:${contact.email}`}
          onClick={(e) => e.stopPropagation()}
          className="text-xs px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
        >
          Email
        </a>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            window.location.href = `/contacts/${contact.id}`;
          }}
          className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          View Profile
        </button>
      </div>
    </div>
  );
}
