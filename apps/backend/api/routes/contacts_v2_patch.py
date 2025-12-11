# Add this to your contacts_v2.py after the existing sync endpoint

@router.post("/sync/hubspot")
async def sync_from_hubspot(limit: int = 100, apply_filters: bool = True):
    """
    Sync contacts from HubSpot with filters
    - Must have: email, company, name
    - Exclude: unqualified lead_status, unsubscribe/customer/evangelist lifecycle
    """
    from services.hubspot_sync_v2 import sync_hubspot_contacts
    
    try:
        stats = sync_hubspot_contacts(limit, apply_filters)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
