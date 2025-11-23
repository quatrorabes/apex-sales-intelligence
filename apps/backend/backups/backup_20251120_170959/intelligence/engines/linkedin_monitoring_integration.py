#!/usr/bin/env python3
"""
SALES FOX - LINKEDIN MONITORING + PREMIUM SALESNAV INTEGRATION
Real-time LinkedIn activity tracking with SalesNav power features

Premium Feature Module:
- Real-time prospect activity monitoring
- SalesNav lead import & insights
- Campaign performance tracking
- Smart LinkedIn automation (safe, compliant)
- Dashboard integration with real-time feedback
"""

import os
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from contextlib import contextmanager
import asyncio
import time


class LinkedInMonitoringEngine:
    """
    Real-time LinkedIn activity monitoring with webhooks & polling
    
    Features:
    - Monitor prospect engagement (views, clicks, messages)
    - Track email/call follow-up effectiveness
    - Real-time notifications to dashboard
    - Activity history for each prospect
    """
    
    def __init__(self, db_path: str = 'salesfox.db'):
        self.db_path = db_path
        self.init_tables()
        
        # Real-time event queue for WebSocket push to dashboard
        self.event_queue = []
        
    def init_tables(self):
        """Initialize LinkedIn monitoring tables"""
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            # LinkedIn prospect tracking
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                linkedin_url TEXT UNIQUE NOT NULL,
                profile_name TEXT,
                headline TEXT,
                company TEXT,
                industry TEXT,
                connection_status TEXT DEFAULT 'not_connected',
                connection_request_sent TIMESTAMP,
                connection_accepted TIMESTAMP,
                engagement_score INTEGER DEFAULT 0,
                last_engagement TIMESTAMP,
                last_checked TIMESTAMP,
                profile_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
            """)
            
            # Real-time activity log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                engagement_value INTEGER,
                email_sent_id INTEGER,
                call_script_id INTEGER,
                FOREIGN KEY(prospect_id) REFERENCES linkedin_prospects(id),
                FOREIGN KEY(email_sent_id) REFERENCES outreach_variants(id),
                FOREIGN KEY(call_script_id) REFERENCES call_scripts(id)
            )
            """)
            
            # Campaign performance tracking
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                campaign_name TEXT,
                campaign_type TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                connection_requests_sent INTEGER DEFAULT 0,
                connections_accepted INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                responses_received INTEGER DEFAULT 0,
                meetings_booked INTEGER DEFAULT 0,
                conversion_rate REAL,
                roi_score REAL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
            """)
            
            # Real-time notifications queue
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                contact_id INTEGER,
                notification_type TEXT,
                title TEXT,
                message TEXT,
                action_url TEXT,
                read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(prospect_id) REFERENCES linkedin_prospects(id),
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_db(self):
        """Database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_prospect(self, contact_id: int, linkedin_url: str, profile_data: Dict = None) -> Dict:
        """Add a prospect to LinkedIn monitoring"""
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO linkedin_prospects
                (contact_id, linkedin_url, profile_name, headline, company, industry, profile_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact_id,
                    linkedin_url,
                    profile_data.get('name') if profile_data else None,
                    profile_data.get('headline') if profile_data else None,
                    profile_data.get('company') if profile_data else None,
                    profile_data.get('industry') if profile_data else None,
                    json.dumps(profile_data) if profile_data else None
                ))
                conn.commit()
                prospect_id = cursor.lastrowid
                
                # Create initial notification
                self.create_notification(
                    prospect_id=prospect_id,
                    contact_id=contact_id,
                    notification_type='prospect_added',
                    title='Prospect Added to Monitoring',
                    message=f'Starting to monitor {profile_data.get("name", "prospect")} on LinkedIn',
                    action_url=linkedin_url
                )
                
                return {'success': True, 'prospect_id': prospect_id}
        
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Prospect already in monitoring'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def log_activity(self, prospect_id: int, activity_type: str, 
                    description: str = None, metadata: Dict = None,
                    engagement_value: int = 0, email_id: int = None,
                    call_id: int = None) -> bool:
        """
        Log prospect activity with engagement scoring
        
        Activity types:
        - profile_view
        - connection_request_sent
        - connection_accepted
        - message_sent
        - message_received
        - email_opened
        - link_clicked
        - post_engagement
        """
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                
                # Log activity
                cursor.execute("""
                INSERT INTO linkedin_activities
                (prospect_id, activity_type, activity_description, metadata, engagement_value, email_sent_id, call_script_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    prospect_id,
                    activity_type,
                    description,
                    json.dumps(metadata) if metadata else None,
                    engagement_value,
                    email_id,
                    call_id
                ))
                
                # Update engagement score
                cursor.execute("""
                UPDATE linkedin_prospects SET
                    engagement_score = engagement_score + ?,
                    last_engagement = ?
                WHERE id = ?
                """, (engagement_value, datetime.now().isoformat(), prospect_id))
                
                # Get prospect details for notification
                cursor.execute("""
                SELECT lp.id, lp.profile_name, lp.contact_id, c.name as contact_name
                FROM linkedin_prospects lp
                LEFT JOIN contacts c ON lp.contact_id = c.id
                WHERE lp.id = ?
                """, (prospect_id,))
                prospect = cursor.fetchone()
                
                conn.commit()
                
                # Create real-time notification
                if prospect:
                    self.create_notification(
                        prospect_id=prospect_id,
                        contact_id=prospect['contact_id'],
                        notification_type=activity_type,
                        title=self._get_activity_title(activity_type),
                        message=description or self._get_activity_message(activity_type, prospect['profile_name']),
                        action_url=None
                    )
                    
                    # Add to event queue for real-time push
                    self.event_queue.append({
                        'type': 'activity',
                        'prospect_id': prospect_id,
                        'activity_type': activity_type,
                        'engagement_value': engagement_value,
                        'timestamp': datetime.now().isoformat(),
                        'prospect_name': prospect['profile_name']
                    })
                
                return True
        
        except Exception as e:
            print(f"Error logging activity: {str(e)}")
            return False
    
    def create_notification(self, prospect_id: int, contact_id: int, 
                           notification_type: str, title: str, message: str,
                           action_url: str = None) -> int:
        """Create real-time notification for dashboard"""
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO linkedin_notifications
                (prospect_id, contact_id, notification_type, title, message, action_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (prospect_id, contact_id, notification_type, title, message, action_url))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            return 0
    
    def _get_activity_title(self, activity_type: str) -> str:
        """Get friendly title for activity type"""
        titles = {
            'profile_view': '🔍 Profile Viewed',
            'connection_request_sent': '🤝 Connection Sent',
            'connection_accepted': '✅ Connection Accepted',
            'message_sent': '💬 Message Sent',
            'message_received': '📩 Message Received',
            'email_opened': '📧 Email Opened',
            'link_clicked': '🔗 Link Clicked',
            'post_engagement': '👍 Post Engagement'
        }
        return titles.get(activity_type, activity_type)
    
    def _get_activity_message(self, activity_type: str, prospect_name: str) -> str:
        """Get friendly message for activity"""
        messages = {
            'profile_view': f'{prospect_name} viewed your profile',
            'connection_request_sent': f'Connection request sent to {prospect_name}',
            'connection_accepted': f'{prospect_name} accepted your connection',
            'message_sent': f'Message sent to {prospect_name}',
            'message_received': f'New message from {prospect_name}',
            'email_opened': f'{prospect_name} opened your email',
            'link_clicked': f'{prospect_name} clicked your link',
            'post_engagement': f'{prospect_name} engaged with your post'
        }
        return messages.get(activity_type, f'Activity: {activity_type}')
    
    def get_unread_notifications(self, contact_id: int, limit: int = 10) -> List[Dict]:
        """Get unread notifications for contact (real-time dashboard feed)"""
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT 
                    ln.id, ln.prospect_id, ln.notification_type, ln.title, 
                    ln.message, ln.action_url, ln.created_at,
                    lp.profile_name, lp.linkedin_url
                FROM linkedin_notifications ln
                LEFT JOIN linkedin_prospects lp ON ln.prospect_id = lp.id
                WHERE ln.contact_id = ? AND ln.read = 0
                ORDER BY ln.created_at DESC
                LIMIT ?
                """, (contact_id, limit))
                
                notifications = []
                for row in cursor.fetchall():
                    notifications.append({
                        'id': row['id'],
                        'prospect_id': row['prospect_id'],
                        'prospect_name': row['profile_name'],
                        'notification_type': row['notification_type'],
                        'title': row['title'],
                        'message': row['message'],
                        'action_url': row['action_url'],
                        'created_at': row['created_at']
                    })
                
                return notifications
        
        except Exception as e:
            print(f"Error fetching notifications: {str(e)}")
            return []
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE linkedin_notifications SET read = 1 WHERE id = ?
                """, (notification_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error marking notification: {str(e)}")
            return False
    
    def get_prospect_engagement_timeline(self, prospect_id: int) -> List[Dict]:
        """Get complete engagement timeline for a prospect"""
        
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT 
                    activity_type, activity_description, timestamp, engagement_value
                FROM linkedin_activities
                WHERE prospect_id = ?
                ORDER BY timestamp DESC
                """, (prospect_id,))
                
                timeline = []
                for row in cursor.fetchall():
                    timeline.append({
                        'activity_type': row['activity_type'],
                        'description': row['activity_description'],
                        'timestamp': row['timestamp'],
                        'engagement_value': row['engagement_value']
                    })
                
                return timeline
        
        except Exception as e:
            print(f"Error fetching timeline: {str(e)}")
            return []
    
    def get_real_time_events(self) -> List[Dict]:
        """Get queued real-time events for WebSocket push"""
        
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events


class SalesNavPremiumEngine:
    """
    SalesNav Premium power features with real-time integration
    
    Features:
    - Lead import from SalesNav saved searches
    - Automated insight extraction
    - Smart outreach recommendations
    - Campaign performance analytics
    - Real-time engagement tracking
    """
    
    def __init__(self, db_path: str = 'salesfox.db'):
        self.db_path = db_path
        self.linkedin_monitor = LinkedInMonitoringEngine(db_path)
        self.init_tables()
    
    def init_tables(self):
        """Initialize SalesNav premium tables"""
        
        with self.linkedin_monitor.get_db() as conn:
            cursor = conn.cursor()
            
            # SalesNav leads
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS salesnav_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                linkedin_prospect_id INTEGER,
                salesnav_lead_id TEXT UNIQUE,
                lead_data JSON,
                insights JSON,
                job_change_signal BOOLEAN,
                company_growth_signal BOOLEAN,
                shared_connections INTEGER,
                reachability_score INTEGER,
                last_synced TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id),
                FOREIGN KEY(linkedin_prospect_id) REFERENCES linkedin_prospects(id)
            )
            """)
            
            # SalesNav saved searches
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS salesnav_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_name TEXT UNIQUE NOT NULL,
                search_criteria JSON NOT NULL,
                auto_import BOOLEAN DEFAULT 0,
                last_run TIMESTAMP,
                total_results INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Campaign recommendations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER,
                recommendation_type TEXT,
                recommendation_text TEXT,
                confidence_score REAL,
                estimated_roi REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(prospect_id) REFERENCES linkedin_prospects(id)
            )
            """)
            
            conn.commit()
    
    def import_salesnav_lead(self, contact_id: int, lead_data: Dict) -> Dict:
        """Import a lead from SalesNav with automatic insights"""
        
        try:
            # First, add to LinkedIn monitoring
            linkedin_result = self.linkedin_monitor.add_prospect(
                contact_id=contact_id,
                linkedin_url=lead_data.get('linkedin_url', ''),
                profile_data=lead_data
            )
            
            if not linkedin_result['success']:
                return linkedin_result
            
            linkedin_prospect_id = linkedin_result['prospect_id']
            
            # Extract insights
            insights = self._extract_insights(lead_data)
            
            # Determine signals
            job_change = insights.get('job_change_signal', False)
            company_growth = insights.get('company_growth_signal', False)
            
            with self.linkedin_monitor.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO salesnav_leads
                (contact_id, linkedin_prospect_id, salesnav_lead_id, lead_data, insights, 
                 job_change_signal, company_growth_signal, shared_connections, reachability_score, last_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact_id,
                    linkedin_prospect_id,
                    lead_data.get('id', ''),
                    json.dumps(lead_data),
                    json.dumps(insights),
                    job_change,
                    company_growth,
                    lead_data.get('shared_connections', 0),
                    self._calculate_reachability_score(lead_data, insights),
                    datetime.now().isoformat()
                ))
                conn.commit()
                
                # Log the import as an activity
                self.linkedin_monitor.log_activity(
                    prospect_id=linkedin_prospect_id,
                    activity_type='salesnav_import',
                    description='Lead imported from SalesNav with auto-insights',
                    metadata={
                        'job_change': job_change,
                        'company_growth': company_growth,
                        'insights': insights
                    },
                    engagement_value=10
                )
            
            return {
                'success': True,
                'salesnav_lead_id': lead_data.get('id', ''),
                'linkedin_prospect_id': linkedin_prospect_id,
                'insights': insights
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_insights(self, lead_data: Dict) -> Dict:
        """Extract actionable insights from SalesNav lead data"""
        
        insights = {
            'job_change_signal': False,
            'company_growth_signal': False,
            'recent_activity': False,
            'shared_network': False,
            'high_reachability': False,
            'talking_points': [],
            'best_outreach_channel': 'connection_request',
            'estimated_response_rate': 0.0
        }
        
        # Check for job change (tenure < 6 months)
        if lead_data.get('tenure_months', 0) < 6:
            insights['job_change_signal'] = True
            insights['talking_points'].append('New to role - perfect timing for relationship building')
            insights['estimated_response_rate'] += 0.15
        
        # Check for company growth
        if lead_data.get('company_employee_growth', 0) > 20:
            insights['company_growth_signal'] = True
            insights['talking_points'].append('Company experiencing rapid growth - opportunity for scaling solutions')
            insights['estimated_response_rate'] += 0.12
        
        # Recent activity
        if lead_data.get('recent_posts', 0) > 0:
            insights['recent_activity'] = True
            insights['talking_points'].append('Active on LinkedIn - good opportunity to engage with content')
        
        # Shared network
        if lead_data.get('shared_connections', 0) > 0:
            insights['shared_network'] = True
            insights['talking_points'].append(f"Mutual connections present - leverage warm intro")
            insights['best_outreach_channel'] = 'shared_connection_intro'
            insights['estimated_response_rate'] += 0.25
        
        # Check reachability
        if lead_data.get('accepts_inmails'):
            insights['high_reachability'] = True
            insights['best_outreach_channel'] = 'inmail'
            insights['estimated_response_rate'] += 0.10
        
        return insights
    
    def _calculate_reachability_score(self, lead_data: Dict, insights: Dict) -> int:
        """Calculate reachability score 0-100"""
        
        score = 50  # Base score
        
        if insights.get('high_reachability'):
            score += 20
        
        if insights.get('shared_network'):
            score += 15
        
        if lead_data.get('open_link_enabled'):
            score += 10
        
        if insights.get('job_change_signal'):
            score += 5
        
        return min(100, score)
    
    def get_smart_recommendations(self, prospect_id: int) -> List[Dict]:
        """Get AI-powered campaign recommendations for a prospect"""
        
        try:
            with self.linkedin_monitor.get_db() as conn:
                cursor = conn.cursor()
                
                # Get prospect data
                cursor.execute("""
                SELECT lp.*, sl.insights
                FROM linkedin_prospects lp
                LEFT JOIN salesnav_leads sl ON lp.id = sl.linkedin_prospect_id
                WHERE lp.id = ?
                """, (prospect_id,))
                
                prospect = cursor.fetchone()
                
                if not prospect:
                    return []
                
                # Generate recommendations based on insights
                insights = json.loads(prospect['insights']) if prospect['insights'] else {}
                recommendations = []
                
                # Recommendation 1: Outreach timing
                if insights.get('job_change_signal'):
                    recommendations.append({
                        'type': 'timing',
                        'text': 'Recommend reaching out in next 2-3 days while they\'re still establishing relationships',
                        'confidence': 0.95,
                        'estimated_roi': 0.30
                    })
                
                # Recommendation 2: Channel
                if insights.get('best_outreach_channel') == 'shared_connection_intro':
                    recommendations.append({
                        'type': 'channel',
                        'text': 'Use shared connection for warm introduction (25% higher response rate)',
                        'confidence': 0.88,
                        'estimated_roi': 0.28
                    })
                
                # Recommendation 3: Value prop
                if insights.get('company_growth_signal'):
                    recommendations.append({
                        'type': 'value_prop',
                        'text': 'Lead with growth solutions - company is scaling rapidly',
                        'confidence': 0.85,
                        'estimated_roi': 0.22
                    })
                
                return recommendations
        
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return []
    
    def get_campaign_analytics(self, contact_id: int) -> Dict:
        """Get comprehensive SalesNav campaign analytics"""
        
        try:
            with self.linkedin_monitor.get_db() as conn:
                cursor = conn.cursor()
                
                # Total leads imported
                cursor.execute("""
                SELECT COUNT(*) as total FROM salesnav_leads WHERE contact_id = ?
                """, (contact_id,))
                total_leads = cursor.fetchone()['total']
                
                # Leads with job change signal
                cursor.execute("""
                SELECT COUNT(*) as count FROM salesnav_leads 
                WHERE contact_id = ? AND job_change_signal = 1
                """, (contact_id,))
                job_changes = cursor.fetchone()['count']
                
                # Leads with company growth signal
                cursor.execute("""
                SELECT COUNT(*) as count FROM salesnav_leads 
                WHERE contact_id = ? AND company_growth_signal = 1
                """, (contact_id,))
                growth_signals = cursor.fetchone()['count']
                
                # Average reachability
                cursor.execute("""
                SELECT AVG(reachability_score) as avg_reach FROM salesnav_leads 
                WHERE contact_id = ?
                """, (contact_id,))
                avg_reachability = cursor.fetchone()['avg_reach'] or 0
                
                # Campaign performance
                cursor.execute("""
                SELECT 
                    SUM(connections_accepted) as connections,
                    SUM(responses_received) as responses,
                    COUNT(*) as campaigns
                FROM linkedin_campaigns
                WHERE contact_id = ? AND status = 'active'
                """, (contact_id,))
                
                perf = cursor.fetchone()
                
                return {
                    'total_leads_imported': total_leads,
                    'job_change_signals': job_changes,
                    'company_growth_signals': growth_signals,
                    'average_reachability': round(avg_reachability, 1),
                    'active_campaigns': perf['campaigns'] or 0,
                    'connections_accepted': perf['connections'] or 0,
                    'responses_received': perf['responses'] or 0,
                    'estimated_pipeline_value': (perf['responses'] or 0) * 5000  # $5k per opportunity
                }
        
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
            return {}


# ============================================================================
# FASTAPI INTEGRATION - Add these endpoints to main_integrated_api.py
# ============================================================================

"""
INTEGRATION CODE FOR main_integrated_api.py:

from linkedin_monitoring_integration import LinkedInMonitoringEngine, SalesNavPremiumEngine

# Initialize engines
linkedin_monitor = LinkedInMonitoringEngine()
salesnav_premium = SalesNavPremiumEngine()

# Add these endpoints to your FastAPI app:

@app.post("/api/premium/linkedin/monitoring/add-prospect")
async def add_linkedin_prospect(contact_id: int, linkedin_url: str, profile_data: Dict = None):
    '''Add prospect to real-time LinkedIn monitoring'''
    result = linkedin_monitor.add_prospect(contact_id, linkedin_url, profile_data)
    return result

@app.get("/api/premium/linkedin/notifications/{contact_id}")
async def get_linkedin_notifications(contact_id: int, limit: int = 10):
    '''Get real-time LinkedIn notifications for dashboard'''
    notifications = linkedin_monitor.get_unread_notifications(contact_id, limit)
    return {'notifications': notifications, 'count': len(notifications)}

@app.post("/api/premium/linkedin/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    '''Mark notification as read'''
    success = linkedin_monitor.mark_notification_read(notification_id)
    return {'success': success}

@app.get("/api/premium/linkedin/timeline/{prospect_id}")
async def get_engagement_timeline(prospect_id: int):
    '''Get prospect engagement timeline'''
    timeline = linkedin_monitor.get_prospect_engagement_timeline(prospect_id)
    return {'timeline': timeline}

@app.get("/api/premium/linkedin/events")
async def get_real_time_events():
    '''Get queued real-time events for WebSocket push'''
    events = linkedin_monitor.get_real_time_events()
    return {'events': events}

@app.post("/api/premium/salesnav/import-lead")
async def import_salesnav_lead(contact_id: int, lead_data: Dict):
    '''Import lead from SalesNav with auto-insights'''
    result = salesnav_premium.import_salesnav_lead(contact_id, lead_data)
    return result

@app.get("/api/premium/salesnav/recommendations/{prospect_id}")
async def get_salesnav_recommendations(prospect_id: int):
    '''Get AI-powered recommendations for prospect'''
    recommendations = salesnav_premium.get_smart_recommendations(prospect_id)
    return {'recommendations': recommendations}

@app.get("/api/premium/salesnav/analytics/{contact_id}")
async def get_salesnav_analytics(contact_id: int):
    '''Get comprehensive SalesNav analytics'''
    analytics = salesnav_premium.get_campaign_analytics(contact_id)
    return analytics

# WebSocket for real-time notifications
@app.websocket("/ws/premium/linkedin/{contact_id}")
async def websocket_linkedin_notifications(websocket: WebSocket, contact_id: int):
    '''WebSocket for real-time LinkedIn activity push to dashboard'''
    await websocket.accept()
    try:
        while True:
            events = linkedin_monitor.get_real_time_events()
            if events:
                await websocket.send_json({'events': events})
            await asyncio.sleep(2)  # Poll every 2 seconds
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()
"""
