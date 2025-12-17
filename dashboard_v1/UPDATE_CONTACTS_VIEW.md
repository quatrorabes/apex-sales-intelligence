# Manual Update Required: ContactsView.tsx

Add the following to `dashboard_v1/src/components/ContactsView.tsx`:

## 1. Add enrichment handler function

Inside the ContactsView component, add this function:

const handleEnrichContact = async (contactId: number) => {
try {
setIsEnriching(true);

text
const response = await fetch(`${API_URL}/api/contacts/${contactId}/enrich`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail || 'Enrichment failed');
}

const result = await response.json();
console.log('✅ Enrichment result:', result);

// Refresh contacts list
await fetchContacts();

alert(`✅ Contact enriched!\n\nSections: ${result.sections}\nFormat: ${result.format}\nCharacters: ${result.characterCount}`);
} catch (error: any) {
console.error('Enrichment error:', error);
alert(❌ Enrichment failed: ${error.message});
} finally {
setIsEnriching(false);
}
};

text

## 2. Add "Enrich" button to contact list table

In your contact list table (where you render each contact row), add this button in the Actions column:

<button
onClick={(e) => {
e.stopPropagation(); // Prevent row click
handleEnrichContact(contact.id);
}}
disabled={isEnriching || contact.enrichment_status === 'completed'}
className={px-3 py-1 text-sm rounded transition-colors ${ contact.enrichment_status === 'completed' ? 'bg-green-100 text-green-700 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50' }}
title={
contact.enrichment_status === 'completed'
? 'Already enriched'
: 'Enrich this contact with AI'
}

{isEnriching
? '⏳ Enriching...'
: contact.enrichment_status === 'completed'
? '✓ Enriched'
: '🔍 Enrich'
}
</button>

text

## 3. Add enrichment status badge (optional)

You can also add a status indicator in each row:

{contact.enrichment_status === 'completed' && (
<span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
✓ AI Enriched
</span>
)}
{contact.enrichment_status === 'enriching' && (
<span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
⏳ Enriching...
</span>
)}
{contact.enrichment_status === 'failed' && (
<span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
✗ Failed
</span>
)}

text

## 4. Testing

After adding these changes:

1. Commit and push to trigger Vercel deployment
2. Wait for Vercel to rebuild (~1-2 min)
3. Refresh Dashboard
4. Click the "🔍 Enrich" button on any contact
5. Watch the button change to "⏳ Enriching..." 
6. After ~60-90 seconds, should see "✓ Enriched"
7. Verify enrichment data in contact detail view

