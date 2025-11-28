// ============================================================
// APP.TSX UPDATES - Add these to your existing App.tsx
// ============================================================

// 1. ADD THESE IMPORTS at the top:
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

// 2. ADD THESE STATE VARIABLES in your main component:
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(true);
const [loadingMore, setLoadingMore] = useState(false);
const [totalContacts, setTotalContacts] = useState(0);
const CONTACTS_PER_PAGE = 50;

// 3. UPDATE YOUR fetchContacts FUNCTION:
const fetchContacts = async (pageNum = 1, append = false) => {
  try {
    if (pageNum === 1) setLoading(true);
    else setLoadingMore(true);

    const offset = (pageNum - 1) * CONTACTS_PER_PAGE;
    const res = await fetch(
      `http://localhost:8000/api/contacts?limit=${CONTACTS_PER_PAGE}&offset=${offset}`
    );
    const data = await res.json();

    if (append) {
      setContacts(prev => [...prev, ...data]);
    } else {
      setContacts(data);
    }

    setHasMore(data.length === CONTACTS_PER_PAGE);
    setPage(pageNum);
  } catch (err) {
    console.error('Failed to fetch contacts:', err);
  } finally {
    setLoading(false);
    setLoadingMore(false);
  }
};

// 4. ADD LOAD MORE HANDLER:
const handleLoadMore = () => {
  if (!loadingMore && hasMore) {
    fetchContacts(page + 1, true);
  }
};

// 5. ADD THIS STATUS BADGE COMPONENT (put with other helper components):
function ContactStatusBadge({ contact }: { contact: Contact }) {
  // Determine status based on what's been done
  if (contact.call_script_1 || contact.email_1_body || contact.linkedin_connect) {
    return (
      <span style={{ 
        display: 'inline-flex', 
        alignItems: 'center',
        marginLeft: 8,
        padding: '2px 8px',
        borderRadius: 12,
        background: 'rgba(16,185,129,0.15)',
        color: '#10b981',
        fontSize: 11,
        fontWeight: 600
      }}>
        ✍️ Ready
      </span>
    );
  }

  if (contact.priority_score) {
    return (
      <span style={{ 
        display: 'inline-flex', 
        alignItems: 'center',
        marginLeft: 8,
        padding: '2px 8px',
        borderRadius: 12,
        background: 'rgba(59,130,246,0.15)',
        color: '#3b82f6',
        fontSize: 11,
        fontWeight: 600
      }}>
        🎯 Scored
      </span>
    );
  }

  if (contact.enrichment_status === 'completed') {
    return (
      <span style={{ 
        display: 'inline-flex', 
        alignItems: 'center',
        marginLeft: 8,
        padding: '2px 8px',
        borderRadius: 12,
        background: 'rgba(139,92,246,0.15)',
        color: '#8b5cf6',
        fontSize: 11,
        fontWeight: 600
      }}>
        ✨ Enriched
      </span>
    );
  }

  return (
    <span style={{ 
      display: 'inline-flex', 
      alignItems: 'center',
      marginLeft: 8,
      opacity: 0.4,
      fontSize: 11
    }}>
      ○
    </span>
  );
}

// 6. UPDATE YOUR CONTACT TABLE ROW to include the badge:
// In your contact list/table, update the name cell:
<td style={{ padding: '12px 16px' }}>
  <div style={{ display: 'flex', alignItems: 'center' }}>
    <span style={{ fontWeight: 500, color: '#e5e7eb' }}>{contact.name}</span>
    <ContactStatusBadge contact={contact} />
  </div>
  <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
    {contact.email}
  </div>
</td>

// 7. ADD PAGINATION CONTROLS after your contact table:
{/* Pagination / Load More */}
<div style={{ 
  display: 'flex', 
  justifyContent: 'center', 
  alignItems: 'center',
  padding: '20px',
  borderTop: '1px solid rgba(148,163,184,0.1)'
}}>
  {hasMore ? (
    <button
      onClick={handleLoadMore}
      disabled={loadingMore}
      style={{
        padding: '12px 32px',
        background: loadingMore ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        border: 'none',
        borderRadius: 8,
        color: '#fff',
        fontSize: 14,
        fontWeight: 600,
        cursor: loadingMore ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: 8
      }}
    >
      {loadingMore ? (
        <>
          <Loader2 size={16} className="animate-spin" />
          Loading...
        </>
      ) : (
        <>
          Load More Contacts
          <ChevronRight size={16} />
        </>
      )}
    </button>
  ) : contacts.length > CONTACTS_PER_PAGE && (
    <span style={{ color: '#64748b', fontSize: 13 }}>
      All {contacts.length} contacts loaded
    </span>
  )}
</div>

// 8. ALTERNATIVE: Page-based pagination (if you prefer pages over infinite scroll)
{/* Page-based Pagination */}
<div style={{ 
  display: 'flex', 
  justifyContent: 'center', 
  alignItems: 'center',
  gap: 16,
  padding: '20px',
  borderTop: '1px solid rgba(148,163,184,0.1)'
}}>
  <button
    onClick={() => fetchContacts(page - 1)}
    disabled={page === 1 || loading}
    style={{
      padding: '10px 16px',
      background: page === 1 ? 'rgba(148,163,184,0.1)' : 'rgba(99,102,241,0.2)',
      border: 'none',
      borderRadius: 8,
      color: page === 1 ? '#64748b' : '#e5e7eb',
      cursor: page === 1 ? 'not-allowed' : 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: 6
    }}
  >
    <ChevronLeft size={16} /> Previous
  </button>

  <span style={{ color: '#94a3b8', fontSize: 14 }}>
    Page {page}
  </span>

  <button
    onClick={() => fetchContacts(page + 1)}
    disabled={!hasMore || loading}
    style={{
      padding: '10px 16px',
      background: !hasMore ? 'rgba(148,163,184,0.1)' : 'rgba(99,102,241,0.2)',
      border: 'none',
      borderRadius: 8,
      color: !hasMore ? '#64748b' : '#e5e7eb',
      cursor: !hasMore ? 'not-allowed' : 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: 6
    }}
  >
    Next <ChevronRight size={16} />
  </button>
</div>
