# FIX FOR BOTH ENRICHMENT ISSUES
# Issue 1: Wrong contact being enriched
# Issue 2: Data not displaying

## ISSUE 1 FIX: Ensure correct contact ID is passed

The Dashboard needs to verify it's sending the right contact_id.

### Check ContactDetailModal.tsx or ContactEnrichmentView.tsx

Look for the enrichment button click handler. It should look like:

```typescript
const handleEnrichContact = async () => {
  setIsEnriching(true);
  try {
    // ✅ CORRECT - Uses contact.id from props
    const response = await apiClient.enrichContact(contact.id);

    // ❌ WRONG - Uses hardcoded or wrong ID
    // const response = await apiClient.enrichContact(someOtherId);

    if (response.success) {
      // Poll for completion
      await pollEnrichmentStatus(contact.id);
    }
  } catch (error) {
    console.error("Enrichment failed:", error);
  } finally {
    setIsEnriching(false);
  }
};
```

## ISSUE 2 FIX: Display enrichment data

The Dashboard expects enrichment_data in this format:

```json
{
  "sections": {
    "professional_background": "...",
    "company_info": "...",
    "sales_intelligence": "..."
  },
  "metadata": {
    "format_detected": "structured",
    "character_count": 3419
  }
}
```

But the backend might be saving it as:

```json
{
  "sections": {
    "raw_text": "... all the text ..."
  },
  "metadata": {
    "format_detected": "raw",
    "character_count": 3419
  }
}
```

### Frontend Fix: Handle both formats

Update `EnrichmentDisplay.tsx` to handle raw_text:

```typescript
interface EnrichmentDisplayProps {
  enrichmentData: any;
}

export const EnrichmentDisplay: React.FC<EnrichmentDisplayProps> = ({ enrichmentData }) => {
  if (!enrichmentData || !enrichmentData.sections) {
    return <div>No enrichment data available</div>;
  }

  const sections = enrichmentData.sections;

  // Handle raw_text format
  if (sections.raw_text) {
    return (
      <div className="prose prose-sm max-w-none">
        <pre className="whitespace-pre-wrap text-sm">
          {sections.raw_text}
        </pre>
      </div>
    );
  }

  // Handle structured format
  return (
    <div className="space-y-4">
      {Object.entries(sections).map(([key, value]) => (
        <div key={key} className="border-l-4 border-blue-500 pl-4">
          <h3 className="font-semibold text-lg capitalize mb-2">
            {key.replace(/_/g, ' ')}
          </h3>
          <p className="text-gray-700 whitespace-pre-wrap">
            {String(value)}
          </p>
        </div>
      ))}
    </div>
  );
};
```

### Backend Fix: Ensure data is saved correctly

The enrichment route should already be saving correctly, but verify:

```python
# In apps/backend/api/routes/enrichment.py
# Around line 120-130

enrichment_object = {
    "sections": {"raw_text": raw_profile},
    "metadata": {"format_detected": "raw", "character_count": len(raw_profile)}
}

enrichment_json = json.dumps(enrichment_object)

with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET enrichment_status = %s, enriched_at = NOW(), enrichment_data = %s WHERE id = %s",
        ('completed', enrichment_json, contact_id)
    )
    conn.commit()
```

## QUICK TEST

1. Open Dashboard
2. Click contact f6e4e0f2-0597-47a2-b4f5-869fa94b6a12
3. Check if enrichment data shows
4. If not, open browser console (F12) and look for:
   - "enrichmentData" object
   - Any parsing errors
   - API response from GET /api/contacts/{id}

## NUCLEAR OPTION: Force re-fetch

If data exists but not showing, the Dashboard might be caching old data.

Add this to ContactDetailModal or wherever the contact detail is shown:

```typescript
useEffect(() => {
  // Force refresh when modal opens
  const fetchContact = async () => {
    try {
      const fresh = await apiClient.getContact(contact.id);
      setContactData(fresh);
    } catch (error) {
      console.error("Failed to fetch fresh contact:", error);
    }
  };

  fetchContact();
}, [contact.id]);
```
