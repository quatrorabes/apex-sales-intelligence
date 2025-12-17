# ContactsView.tsx Update Instructions

## Add Single Contact Enrich Button

### Step 1: Add Handler Function

Inside your ContactsView component, add this function:

```typescript
const handleEnrichContact = async (contactId: number) => {
  try {
    setIsEnriching(true);

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

    await fetchContacts();

    alert(`✅ Contact enriched successfully!

Sections: ${result.sections}
Format: ${result.format}
Characters: ${result.characterCount}

Debug files: ${result.debugFiles}`);
  } catch (error: any) {
    console.error('Enrichment error:', error);
    alert(`❌ Enrichment failed: ${error.message}`);
  } finally {
    setIsEnriching(false);
  }
};
```

### Step 2: Add Button to Contact List Table

In your contacts table, add this button in the Actions column:

```tsx
<button
  onClick={(e) => {
    e.stopPropagation();
    handleEnrichContact(contact.id);
  }}
  disabled={isEnriching || contact.enrichment_status === 'completed'}
  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
    contact.enrichment_status === 'completed'
      ? 'bg-green-100 text-green-700 cursor-not-allowed'
      : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed'
  }`}
  title={
    contact.enrichment_status === 'completed'
      ? 'Already enriched'
      : 'Enrich this contact with AI'
  }
>
  {isEnriching 
    ? '⏳ Enriching...' 
    : contact.enrichment_status === 'completed' 
      ? '✓ Enriched' 
      : '🔍 Enrich'
  }
</button>
```

### Step 3: Optional - Add Status Badge

```tsx
{contact.enrichment_status === 'completed' && (
  <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
    ✓ AI Enriched
  </span>
)}
{contact.enrichment_status === 'enriching' && (
  <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 animate-pulse">
    ⏳ Enriching...
  </span>
)}
{contact.enrichment_status === 'failed' && (
  <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
    ✗ Failed
  </span>
)}
```

### Step 4: Deploy

```bash
git add dashboard_v1/src/components/ContactsView.tsx
git commit -m "feat(ui): add per-contact enrich button"
git push origin main
```

Vercel will auto-deploy in ~1-2 minutes.

### Testing

1. Refresh Dashboard after deployment
2. Find a contact without enrichment
3. Click "🔍 Enrich" button
4. Watch button change to "⏳ Enriching..."
5. Wait ~60-90 seconds (Perplexity + GPT-4 processing)
6. Button changes to "✓ Enriched"
7. Click contact to view enrichment data
8. Check Render logs for debug file paths
