#!/usr/bin/env python3
"""
METHOD REFERENCE GUIDE
Shows you exactly what methods are available in each class
And what they do

Use this to know what to call from your endpoint functions
"""

METHOD_REFERENCE = """

╔═══════════════════════════════════════════════════════════════════════════════╗
║                  LINKEDIN CLASSES & METHODS REFERENCE                        ║
║                       What to call from your endpoints                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝


CLASS: LinkedInMonitoringEngine
FILE: linkedin_monitoring_integration.py
────────────────────────────────────────────────────────────────────────────────

METHOD 1: add_prospect()
──────────────────────
  Purpose: Add a prospect to real-time monitoring
  Called from: POST /api/premium/linkedin/monitoring/add-prospect
  
  Parameters:
    - contact_id: int (required)
    - linkedin_url: str (required)
    - profile_data: dict (optional)
  
  Returns:
    {
      'success': bool,
      'prospect_id': int
    }
  
  In your endpoint:
    result = linkedin_monitor.add_prospect(contact_id, linkedin_url, profile_data)
    return result


METHOD 2: get_unread_notifications()
────────────────────────────────────
  Purpose: Get list of unread notifications for a contact
  Called from: GET /api/premium/linkedin/notifications/{contact_id}
  
  Parameters:
    - contact_id: int (required)
    - limit: int (optional, default 10)
  
  Returns:
    [
      {
        'id': int,
        'prospect_id': int,
        'prospect_name': str,
        'notification_type': str,
        'title': str,
        'message': str,
        'action_url': str,
        'created_at': str
      },
      ...
    ]
  
  In your endpoint:
    notifications = linkedin_monitor.get_unread_notifications(contact_id, limit)
    return {'notifications': notifications, 'count': len(notifications)}


METHOD 3: mark_notification_read()
──────────────────────────────────
  Purpose: Mark a single notification as read
  Called from: POST /api/premium/linkedin/notifications/{notification_id}/read
  
  Parameters:
    - notification_id: int (required)
  
  Returns:
    bool (True if successful)
  
  In your endpoint:
    success = linkedin_monitor.mark_notification_read(notification_id)
    return {'success': success}


METHOD 4: get_prospect_engagement_timeline()
─────────────────────────────────────────────
  Purpose: Get chronological engagement history for a prospect
  Called from: GET /api/premium/linkedin/timeline/{prospect_id}
  
  Parameters:
    - prospect_id: int (required)
  
  Returns:
    [
      {
        'activity_type': str,
        'description': str,
        'timestamp': str,
        'engagement_value': int
      },
      ...
    ]
  
  In your endpoint:
    timeline = linkedin_monitor.get_prospect_engagement_timeline(prospect_id)
    return {'timeline': timeline}


METHOD 5: get_real_time_events()
────────────────────────────────
  Purpose: Get queued real-time events (and clear queue)
  Called from: GET /api/premium/linkedin/events or WebSocket
  
  Parameters: None
  
  Returns:
    [
      {
        'type': str,
        'prospect_id': int,
        'activity_type': str,
        'engagement_value': int,
        'timestamp': str,
        'prospect_name': str
      },
      ...
    ]
  
  In your endpoint:
    events = linkedin_monitor.get_real_time_events()
    return {'events': events}


METHOD 6: log_activity()
────────────────────────
  Purpose: Log a prospect activity (for internal use)
  
  Parameters:
    - prospect_id: int
    - activity_type: str (profile_view, message_received, etc)
    - description: str (optional)
    - metadata: dict (optional)
    - engagement_value: int (optional)
    - email_id: int (optional)
    - call_id: int (optional)
  
  Returns: bool (success)
  
  Note: Called automatically when activities happen


METHOD 7: create_notification()
───────────────────────────────
  Purpose: Create a new notification (for internal use)
  
  Parameters:
    - prospect_id: int
    - contact_id: int
    - notification_type: str
    - title: str
    - message: str
    - action_url: str (optional)
  
  Returns: int (notification_id)
  
  Note: Called automatically by other methods


═════════════════════════════════════════════════════════════════════════════

CLASS: SalesNavPremiumEngine
FILE: linkedin_monitoring_integration.py
────────────────────────────────────────────────────────────────────────────────

METHOD 1: import_salesnav_lead()
────────────────────────────────
  Purpose: Import a lead from SalesNav with auto-insights
  Called from: POST /api/premium/salesnav/import-lead
  
  Parameters:
    - contact_id: int
    - lead_data: dict with keys:
      {
        'id': str,
        'name': str,
        'title': str,
        'company': str,
        'linkedin_url': str,
        'tenure_months': int,
        'company_employee_growth': int,
        'shared_connections': int,
        'accepts_inmails': bool
      }
  
  Returns:
    {
      'success': bool,
      'salesnav_lead_id': str,
      'linkedin_prospect_id': int,
      'insights': {
        'job_change_signal': bool,
        'company_growth_signal': bool,
        'talking_points': [str, ...],
        'best_outreach_channel': str,
        'estimated_response_rate': float
      }
    }
  
  In your endpoint:
    result = salesnav_premium.import_salesnav_lead(contact_id, lead_data)
    return result


METHOD 2: get_smart_recommendations()
──────────────────────────────────────
  Purpose: Get AI-powered recommendations for a prospect
  Called from: GET /api/premium/salesnav/recommendations/{prospect_id}
  
  Parameters:
    - prospect_id: int
  
  Returns:
    [
      {
        'type': str,
        'text': str,
        'confidence': float (0-1),
        'estimated_roi': float
      },
      ...
    ]
  
  In your endpoint:
    recommendations = salesnav_premium.get_smart_recommendations(prospect_id)
    return {'recommendations': recommendations}


METHOD 3: get_campaign_analytics()
──────────────────────────────────
  Purpose: Get comprehensive campaign analytics
  Called from: GET /api/premium/salesnav/analytics/{contact_id}
  
  Parameters:
    - contact_id: int
  
  Returns:
    {
      'total_leads_imported': int,
      'job_change_signals': int,
      'company_growth_signals': int,
      'average_reachability': float,
      'active_campaigns': int,
      'connections_accepted': int,
      'responses_received': int,
      'estimated_pipeline_value': float
    }
  
  In your endpoint:
    analytics = salesnav_premium.get_campaign_analytics(contact_id)
    return analytics


═════════════════════════════════════════════════════════════════════════════

CLASS: LinkedInAutomation
FILE: linkedin_automation.py
────────────────────────────────────────────────────────────────────────────────

COMMON METHODS (for reference - you don't need to wire these if not using):

  send_connection_request(prospect_id)
  send_message(prospect_id, message)
  view_profile(prospect_id)
  accept_connection(request_id)
  send_inmail(prospect_id, subject, message)
  
These handle safe, compliant LinkedIn automation


═════════════════════════════════════════════════════════════════════════════

CLASS: SalesNavigatorIntegration
FILE: linkedin_sales_nav.py
────────────────────────────────────────────────────────────────────────────────

COMMON METHODS (for reference - internal use):

  get_saved_leads()
  get_lead_insights(lead_id)
  save_lead_to_list(lead_id, list_name)
  update_lead_status(lead_id, status)


═════════════════════════════════════════════════════════════════════════════

QUICK REFERENCE: Method Calls in Your Endpoints

Endpoint                                  Method to Call
────────────────────────────────────────────────────────────────────────────
POST /api/premium/linkedin/...            linkedin_monitor.add_prospect(...)
GET /api/premium/linkedin/notifications   linkedin_monitor.get_unread_notifications(...)
POST /api/premium/linkedin/.../read       linkedin_monitor.mark_notification_read(...)
GET /api/premium/linkedin/timeline        linkedin_monitor.get_prospect_engagement_timeline(...)
GET /api/premium/linkedin/events          linkedin_monitor.get_real_time_events()
POST /api/premium/salesnav/import-lead    salesnav_premium.import_salesnav_lead(...)
GET /api/premium/salesnav/recommendations salesnav_premium.get_smart_recommendations(...)
GET /api/premium/salesnav/analytics       salesnav_premium.get_campaign_analytics(...)
WebSocket /ws/premium/linkedin            linkedin_monitor.get_real_time_events() in loop

═════════════════════════════════════════════════════════════════════════════

EXAMPLE ENDPOINT USING THIS REFERENCE:

@app.post("/api/premium/linkedin/monitoring/add-prospect")
async def add_linkedin_prospect(contact_id: int, linkedin_url: str, 
                               profile_data: dict = None):
    '''
    From Method Reference:
    - Use: linkedin_monitor.add_prospect()
    - Parameters: contact_id, linkedin_url, profile_data
    - Returns: {success, prospect_id}
    '''
    result = linkedin_monitor.add_prospect(contact_id, linkedin_url, profile_data)
    return result


ANOTHER EXAMPLE:

@app.get("/api/premium/salesnav/analytics/{contact_id}")
async def get_salesnav_analytics(contact_id: int):
    '''
    From Method Reference:
    - Use: salesnav_premium.get_campaign_analytics()
    - Parameters: contact_id
    - Returns: analytics dict
    '''
    analytics = salesnav_premium.get_campaign_analytics(contact_id)
    return analytics

═════════════════════════════════════════════════════════════════════════════
"""

if __name__ == '__main__':
    print(METHOD_REFERENCE)
    print("\n💡 Use this guide when you're writing each endpoint")
    print("   Look up the method, see what it takes, what it returns")
    print("   Then write the endpoint to match\n")
