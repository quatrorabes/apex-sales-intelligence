# apps/backend/intelligence/apex_scoring_engine.py
"""
Apex Intelligence - Main Scoring Engine
Adaptive MDCP + RSS scoring with lifecycle tracking for commercial real estate lending
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import json

from .lead_types import LeadTypeProfile, LeadLifecycleStage
from .utils import safe_divide, normalize_score, calculate_days_between


class ApexScoringEngine:
    """
    Main scoring engine for Apex Intelligence
    Calculates MDCP, RSS, and Priority scores based on lead type and lifecycle stage
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, db_path: str = 'apex.db'):
        """
        Initialize scoring engine with database connection
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    # ========================================
    # MAIN SCORING INTERFACE
    # ========================================
    
    def score_contact(self, contact_id: int, save_to_db: bool = True) -> Dict:
        """
        Complete scoring for a single contact
        
        Args:
            contact_id: Database ID of contact
            save_to_db: Whether to save scores to database
            
        Returns:
            Dictionary with all scores and recommendations
        """
        
        # Fetch contact data
        contact = self._fetch_contact_data(contact_id)
        
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        # Convert Row to dict
        contact = dict(contact)
        
        # Determine lifecycle stage
        lifecycle_stage = self._determine_lifecycle_stage(contact)
        
        # Update lifecycle stage if changed
        if lifecycle_stage != contact.get('lifecycle_stage'):
            self._update_lifecycle_stage(contact_id, lifecycle_stage)
            contact['lifecycle_stage'] = lifecycle_stage
        
        # Get lead type
        lead_type = contact.get('lead_type', 'BORROWER')
        
        # Calculate MDCP score
        mdcp_result = self.calculate_mdcp_score(contact, lead_type, lifecycle_stage)
        
        # Calculate RSS score (if applicable)
        rss_result = self.calculate_rss_score(contact, lifecycle_stage)
        
        # Calculate combined priority
        priority_result = self.calculate_priority_score(
            mdcp_result['total'],
            rss_result['total'] if rss_result['total'] else 0,
            lifecycle_stage,
            lead_type
        )
        
        # Build result
        result = {
            'contact_id': contact_id,
            'contact_name': f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
            'company': contact.get('company', ''),
            'lead_type': lead_type,
            'lifecycle_stage': lifecycle_stage,
            
            # MDCP
            'mdcp_score': mdcp_result['total'],
            'mdcp_tier': mdcp_result['tier'],
            'mdcp_breakdown': mdcp_result,
            
            # RSS
            'rss_score': rss_result['total'],
            'rss_tier': rss_result['tier'],
            'rss_breakdown': rss_result,
            
            # Priority
            'priority_score': priority_result['score'],
            'urgency_level': priority_result['urgency'],
            'recommended_action': priority_result['action'],
            
            # Metadata
            'calculated_at': datetime.now().isoformat(),
            'calculation_version': self.VERSION
        }
        
        # Save to database
        if save_to_db:
            self._save_scores_to_db(result)
        
        return result
    
    def score_all_contacts(self, lead_type: Optional[str] = None) -> List[Dict]:
        """
        Score all contacts (optionally filtered by lead type)
        
        Args:
            lead_type: Filter by lead type (BANKER, CDC, BROKER, PRIVATE_LENDER, BORROWER)
            
        Returns:
            List of score dictionaries, sorted by priority
        """
        
        # Get all contact IDs
        query = "SELECT id FROM contacts WHERE lead_type IS NOT NULL"
        params = []
        
        if lead_type:
            query += " AND lead_type = ?"
            params.append(lead_type.upper())
        
        self.cursor.execute(query, params)
        contact_ids = [row[0] for row in self.cursor.fetchall()]
        
        print(f"[APEX] Scoring {len(contact_ids)} contacts...")
        
        # Score each contact
        results = []
        for i, contact_id in enumerate(contact_ids):
            try:
                result = self.score_contact(contact_id, save_to_db=True)
                results.append(result)
                if (i + 1) % 10 == 0:
                    print(f"  → Scored {i + 1}/{len(contact_ids)} contacts")
            except Exception as e:
                print(f"  ⚠ Error scoring contact {contact_id}: {e}")
                continue
        
        # Sort by priority score descending
        results.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Update metadata
        self._update_metadata('last_calculation', datetime.now().isoformat())
        self._update_metadata('total_contacts_scored', str(len(results)))
        
        print(f"[APEX] ✓ Scoring complete: {len(results)} contacts scored")
        
        return results
    
    # ========================================
    # MDCP SCORING
    # ========================================
    
    def calculate_mdcp_score(self, contact: Dict, lead_type: str, lifecycle_stage: str) -> Dict:
        """
        Calculate MDCP score with type-specific weights
        
        Returns:
            Dict with total score, component scores, weights, and tier
        """
        
        # Get type profile and weights
        profile = LeadTypeProfile.get_profile(lead_type)
        if not profile:
            profile = LeadTypeProfile.get_profile('BORROWER')
        
        weights = profile['mdcp_weights']
        
        # Calculate each component (0-100)
        money_score = self._score_money(contact, lead_type)
        decision_score = self._score_decision(contact, lead_type)
        credibility_score = self._score_credibility(contact, lead_type, lifecycle_stage)
        pain_score = self._score_pain(contact, lead_type)
        
        # Apply weights
        total = (
            money_score * weights['Money'] +
            decision_score * weights['Decision'] +
            credibility_score * weights['Credibility'] +
            pain_score * weights['Pain']
        )
        
        # Determine tier
        tier = self._classify_mdcp_tier(total)
        
        return {
            'total': round(total, 2),
            'Money': round(money_score, 2),
            'Decision': round(decision_score, 2),
            'Credibility': round(credibility_score, 2),
            'Pain': round(pain_score, 2),
            'weights': weights,
            'tier': tier,
            'lead_type': lead_type
        }
    
    def _score_money(self, contact: Dict, lead_type: str) -> float:
        """Score Money component based on lead type"""
        
        loan_amount = contact.get('loan_amount') or 0
        equity_percent = contact.get('equity_percent') or 0
        
        if lead_type == 'BANKER':
            assets = contact.get('institution_assets') or 0
            if assets >= 1_000_000_000:
                return 90.0
            elif assets >= 500_000_000:
                return 75.0
            elif assets >= 100_000_000:
                return 60.0
            elif assets >= 50_000_000:
                return 45.0
            else:
                return 30.0
        
        elif lead_type == 'CDC':
            volume = contact.get('annual_loan_volume') or 0
            if volume >= 50_000_000:
                return 85.0
            elif volume >= 25_000_000:
                return 70.0
            elif volume >= 10_000_000:
                return 55.0
            elif volume >= 5_000_000:
                return 40.0
            else:
                return 25.0
        
        elif lead_type == 'BROKER':
            if loan_amount >= 5_000_000:
                return 95.0
            elif loan_amount >= 3_000_000:
                return 85.0
            elif loan_amount >= 2_000_000:
                return 70.0
            elif loan_amount >= 1_000_000:
                return 55.0
            elif loan_amount >= 500_000:
                return 40.0
            else:
                return 25.0
        
        elif lead_type == 'PRIVATE_LENDER':
            capital = contact.get('available_capital') or 0
            if capital >= 50_000_000:
                return 90.0
            elif capital >= 20_000_000:
                return 75.0
            elif capital >= 10_000_000:
                return 60.0
            elif capital >= 5_000_000:
                return 45.0
            else:
                return 30.0
        
        else:  # BORROWER
            if equity_percent >= 35:
                return 95.0
            elif equity_percent >= 30:
                return 90.0
            elif equity_percent >= 25:
                return 80.0
            elif equity_percent >= 20:
                return 70.0
            elif equity_percent >= 15:
                return 55.0
            elif equity_percent >= 10:
                return 40.0
            elif equity_percent >= 5:
                return 25.0
            else:
                return 10.0
    
    def _score_decision(self, contact: Dict, lead_type: str) -> float:
        """Score Decision authority based on lead type"""
        
        job_title = (contact.get('jobtitle') or '').lower()
        
        # Title keywords scoring
        if any(word in job_title for word in ['ceo', 'president', 'owner', 'founder', 'principal']):
            base_score = 95.0
        elif any(word in job_title for word in ['cfo', 'chief', 'partner']):
            base_score = 90.0
        elif any(word in job_title for word in ['vp', 'vice president', 'director']):
            base_score = 75.0
        elif any(word in job_title for word in ['manager', 'head of']):
            base_score = 60.0
        elif any(word in job_title for word in ['senior', 'lead']):
            base_score = 50.0
        else:
            base_score = 40.0
        
        # Type-specific adjustments
        if lead_type == 'BANKER':
            base_score *= 0.85  # Committee decisions reduce individual authority
        elif lead_type == 'BROKER':
            base_score = min(100, base_score * 1.1)  # Brokers have high autonomy
        elif lead_type == 'BORROWER':
            base_score = min(100, base_score * 1.05)  # Borrowers are their own decision maker
        
        return min(100, base_score)
    
    def _score_credibility(self, contact: Dict, lead_type: str, lifecycle_stage: str) -> float:
        """Score Credibility based on lead type and lifecycle"""
        
        base_score = 50.0
        
        if lead_type == 'BANKER':
            years = contact.get('years_in_business') or 0
            if years >= 50:
                base_score = 90.0
            elif years >= 20:
                base_score = 75.0
            elif years >= 10:
                base_score = 60.0
            elif years >= 5:
                base_score = 45.0
            else:
                base_score = 30.0
        
        elif lead_type == 'CDC':
            sba_deals = contact.get('sba_loans_closed') or 0
            if sba_deals >= 100:
                base_score = 85.0
            elif sba_deals >= 50:
                base_score = 70.0
            elif sba_deals >= 20:
                base_score = 55.0
            elif sba_deals >= 10:
                base_score = 40.0
            else:
                base_score = 25.0
        
        elif lead_type == 'BROKER':
            deals = contact.get('lifetime_deals_closed') or 0
            if deals >= 50:
                base_score = 80.0
            elif deals >= 20:
                base_score = 65.0
            elif deals >= 10:
                base_score = 50.0
            elif deals >= 5:
                base_score = 35.0
            else:
                base_score = 20.0
        
        elif lead_type == 'PRIVATE_LENDER':
            exits = contact.get('successful_exits') or 0
            if exits >= 20:
                base_score = 85.0
            elif exits >= 10:
                base_score = 70.0
            elif exits >= 5:
                base_score = 55.0
            elif exits >= 2:
                base_score = 40.0
            else:
                base_score = 25.0
        
        else:  # BORROWER
            properties = contact.get('properties_owned') or 0
            years_biz = contact.get('years_in_business') or 0
            
            property_score = min(40, properties * 8)
            experience_score = min(30, years_biz * 3)
            base_score = property_score + experience_score + 20
        
        # Lifecycle bonus
        deals_with_you = contact.get('total_deals_closed') or 0
        
        if lifecycle_stage == 'ESTABLISHED':
            if deals_with_you >= 5:
                base_score = min(100, base_score + 20)
            elif deals_with_you >= 2:
                base_score = min(100, base_score + 10)
        elif lifecycle_stage == 'ACTIVE':
            if deals_with_you >= 1:
                base_score = min(100, base_score + 5)
        
        return min(100, base_score)
    
    def _score_pain(self, contact: Dict, lead_type: str) -> float:
        """Score Pain/Urgency based on lead type"""
        
        days_to_close = contact.get('days_to_close') or 999
        under_contract = contact.get('under_contract') or 0
        
        # Base urgency from timeline
        if days_to_close <= 15:
            urgency = 95.0
        elif days_to_close <= 30:
            urgency = 85.0
        elif days_to_close <= 45:
            urgency = 70.0
        elif days_to_close <= 60:
            urgency = 55.0
        elif days_to_close <= 90:
            urgency = 40.0
        else:
            urgency = 25.0
        
        # Under contract bonus
        if under_contract:
            urgency = min(100, urgency + 15)
        
        # Type-specific adjustments
        if lead_type == 'BANKER':
            urgency *= 0.75  # Bankers rarely urgent
        elif lead_type == 'BROKER':
            urgency = min(100, urgency * 1.25)  # Brokers live on urgency
        elif lead_type == 'PRIVATE_LENDER':
            urgency = min(100, urgency * 1.15)  # Opportunity cost drives urgency
        
        return min(100, urgency)
    
    def _classify_mdcp_tier(self, score: float) -> str:
        """Classify MDCP score into tier"""
        if score >= 85:
            return 'PLATINUM'
        elif score >= 70:
            return 'HOT'
        elif score >= 55:
            return 'WARM'
        elif score >= 40:
            return 'QUALIFIED'
        else:
            return 'COLD'
    
    # ========================================
    # RSS SCORING
    # ========================================
    
    def calculate_rss_score(self, contact: Dict, lifecycle_stage: str) -> Dict:
        """
        Calculate Relationship Strength Score
        Only applicable for WARMING, ACTIVE, ESTABLISHED stages
        """
        
        contact_id = contact['id']
        
        if lifecycle_stage == 'NEW':
            return {
                'total': 0,
                'familiarity': 0,
                'engagement': 0,
                'productivity': 0,
                'tier': 'N/A',
                'note': 'Too new for relationship scoring'
            }
        
        elif lifecycle_stage == 'COLD':
            return {
                'total': 15.0,
                'familiarity': 20.0,
                'engagement': 10.0,
                'productivity': 0,
                'tier': 'PROSPECT',
                'note': 'Cold lead - minimal relationship'
            }
        
        # Calculate components
        familiarity = self._calculate_familiarity(contact)
        engagement = self._calculate_engagement(contact, contact_id)
        productivity = self._calculate_productivity(contact)
        
        # Weight based on lifecycle
        if lifecycle_stage == 'WARMING':
            total = (familiarity * 0.40 + engagement * 0.60)
        else:  # ACTIVE or ESTABLISHED
            total = (
                familiarity * 0.30 +
                engagement * 0.30 +
                productivity * 0.40
            )
        
        tier = self._classify_rss_tier(total)
        
        return {
            'total': round(total, 2),
            'familiarity': round(familiarity, 2),
            'engagement': round(engagement, 2),
            'productivity': round(productivity, 2),
            'tier': tier,
            'note': f'RSS calculation for {lifecycle_stage} stage'
        }
    
    def _calculate_familiarity(self, contact: Dict) -> float:
        """Calculate Familiarity score"""
        
        rel_type = contact.get('relationship_type', 'PROFESSIONAL')
        type_scores = {
            'PERSONAL': 90.0,
            'TRUSTED': 75.0,
            'PROFESSIONAL': 60.0,
            'ACQUAINTANCE': 40.0,
            'TRANSACTIONAL': 20.0,
            'UNKNOWN': 10.0
        }
        base_score = type_scores.get(rel_type, 50.0)
        
        # Tenure bonus
        created_date = contact.get('createdate')
        tenure_bonus = 0
        
        if created_date:
            try:
                if isinstance(created_date, str):
                    created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                
                days_known = (datetime.now(created_date.tzinfo) - created_date).days
                years_known = days_known / 365
                
                if years_known >= 5:
                    tenure_bonus = 10
                elif years_known >= 3:
                    tenure_bonus = 7
                elif years_known >= 1:
                    tenure_bonus = 5
                elif years_known >= 0.5:
                    tenure_bonus = 3
            except:
                pass
        
        # Deal history bonus
        deals_closed = contact.get('total_deals_closed') or 0
        if deals_closed >= 10:
            deals_bonus = 10
        elif deals_closed >= 5:
            deals_bonus = 7
        elif deals_closed >= 2:
            deals_bonus = 4
        else:
            deals_bonus = 0
        
        total = base_score + tenure_bonus + deals_bonus
        return min(100, total)
    
    def _calculate_engagement(self, contact: Dict, contact_id: int) -> float:
        """Calculate Engagement score from touchpoints"""
        
        try:
            self.cursor.execute("""
                SELECT touchpoint_type, COUNT(*) as count
                FROM touchpoints
                WHERE contact_id = ?
                AND touchpoint_date >= date('now', '-365 days')
                GROUP BY touchpoint_type
            """, (contact_id,))
            
            touchpoint_counts = dict(self.cursor.fetchall())
        except:
            touchpoint_counts = {}
        
        # Weight touchpoints
        weights = {
            'happy_hour': 5,
            'lunch_dinner': 4,
            'phone_call': 2,
            'zoom_meeting': 2,
            'email': 1,
            'text': 1
        }
        
        engagement_points = sum(
            touchpoint_counts.get(tp_type, 0) * weight
            for tp_type, weight in weights.items()
        )
        
        # Normalize to 0-100
        if engagement_points >= 80:
            score = 95.0
        elif engagement_points >= 50:
            score = 85.0
        elif engagement_points >= 30:
            score = 70.0
        elif engagement_points >= 15:
            score = 55.0
        elif engagement_points >= 5:
            score = 35.0
        else:
            score = 15.0
        
        # Consistency bonus
        if self._is_engagement_consistent(contact_id):
            score = min(100, score + 5)
        
        return score
    
    def _is_engagement_consistent(self, contact_id: int) -> bool:
        """Check if engagement is consistent over time"""
        
        try:
            self.cursor.execute("""
                SELECT 
                    strftime('%Y-%m', touchpoint_date) as month,
                    COUNT(*) as count
                FROM touchpoints
                WHERE contact_id = ?
                AND touchpoint_date >= date('now', '-365 days')
                GROUP BY month
                ORDER BY month
            """, (contact_id,))
            
            monthly_counts = [row[1] for row in self.cursor.fetchall()]
            
            if len(monthly_counts) < 3:
                return False
            
            mean = statistics.mean(monthly_counts)
            if mean == 0:
                return False
            
            stdev = statistics.stdev(monthly_counts)
            cv = stdev / mean
            
            return cv < 0.5
        except:
            return False
    
    def _calculate_productivity(self, contact: Dict) -> float:
        """Calculate Productivity score from deal history"""
        
        total_deals = contact.get('total_deals_closed') or 0
        total_referred = contact.get('total_deals_referred') or 0
        total_funded = contact.get('total_deals_funded_amount') or 0
        
        # Volume score (25 points)
        if total_deals >= 15:
            volume_score = 25.0
        elif total_deals >= 8:
            volume_score = 20.0
        elif total_deals >= 3:
            volume_score = 15.0
        elif total_deals >= 1:
            volume_score = 10.0
        else:
            volume_score = 0.0
        
        # Close rate score (25 points)
        if total_referred > 0:
            close_rate = total_deals / total_referred
            if close_rate >= 0.80:
                rate_score = 25.0
            elif close_rate >= 0.70:
                rate_score = 20.0
            elif close_rate >= 0.60:
                rate_score = 15.0
            elif close_rate >= 0.50:
                rate_score = 10.0
            else:
                rate_score = 5.0
        else:
            rate_score = 0.0
        
        # Frequency score (25 points)
        created_date = contact.get('createdate')
        frequency_score = 0.0
        
        if created_date and total_deals > 0:
            try:
                if isinstance(created_date, str):
                    created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                
                years_active = max(1, (datetime.now(created_date.tzinfo) - created_date).days / 365)
                deals_per_year = total_deals / years_active
                
                if deals_per_year >= 5:
                    frequency_score = 25.0
                elif deals_per_year >= 2:
                    frequency_score = 20.0
                elif deals_per_year >= 1:
                    frequency_score = 15.0
                elif deals_per_year >= 0.5:
                    frequency_score = 10.0
                else:
                    frequency_score = 5.0
            except:
                frequency_score = 0.0
        
        # Revenue score (25 points)
        if total_deals > 0:
            avg_deal_size = total_funded / total_deals
            if avg_deal_size >= 3_000_000:
                revenue_score = 25.0
            elif avg_deal_size >= 2_000_000:
                revenue_score = 20.0
            elif avg_deal_size >= 1_000_000:
                revenue_score = 15.0
            elif avg_deal_size >= 500_000:
                revenue_score = 10.0
            else:
                revenue_score = 5.0
        else:
            revenue_score = 0.0
        
        total = volume_score + rate_score + frequency_score + revenue_score
        return total
    
    def _classify_rss_tier(self, score: float) -> str:
        """Classify RSS score into tier"""
        if score >= 80:
            return 'PLATINUM'
        elif score >= 65:
            return 'GOLD'
        elif score >= 50:
            return 'SILVER'
        elif score >= 35:
            return 'BRONZE'
        else:
            return 'PROSPECT'
    
    # ========================================
    # PRIORITY SCORING
    # ========================================
    
    def calculate_priority_score(
        self,
        mdcp_score: float,
        rss_score: float,
        lifecycle_stage: str,
        lead_type: str
    ) -> Dict:
        """
        Calculate combined priority score and recommended action
        """
        
        # Weight based on lifecycle
        if lifecycle_stage in ['NEW', 'COLD']:
            priority = mdcp_score
        elif lifecycle_stage == 'WARMING':
            priority = (mdcp_score * 0.80) + (rss_score * 0.20)
        else:  # ACTIVE or ESTABLISHED
            priority = (mdcp_score * 0.60) + (rss_score * 0.40)
        
        # Determine urgency level
        if priority >= 80:
            urgency = 'IMMEDIATE'
        elif priority >= 65:
            urgency = 'HIGH'
        elif priority >= 50:
            urgency = 'MEDIUM'
        else:
            urgency = 'LOW'
        
        # Recommended action
        action = self._get_recommended_action(
            priority, mdcp_score, rss_score, lifecycle_stage, lead_type, urgency
        )
        
        return {
            'score': round(priority, 2),
            'urgency': urgency,
            'action': action
        }
    
    def _get_recommended_action(
        self,
        priority: float,
        mdcp: float,
        rss: float,
        lifecycle: str,
        lead_type: str,
        urgency: str
    ) -> str:
        """Generate actionable recommendation"""
        
        if priority >= 85:
            if lifecycle == 'NEW':
                return f"🔥 HOT NEW {lead_type} - Immediate outreach within 1 hour. Fast-track qualification."
            elif lifecycle == 'ESTABLISHED':
                return f"⭐ STRATEGIC {lead_type} PARTNER - VIP treatment. Expedite approval process."
            else:
                return f"🎯 HIGH PRIORITY {lead_type} - Respond within 4 hours. Strong conversion potential."
        
        elif priority >= 70:
            if lifecycle in ['NEW', 'COLD']:
                return f"📋 QUALIFIED {lead_type} LEAD - Standard outreach within 24 hours. Good fit."
            else:
                return f"✅ GOOD {lead_type} OPPORTUNITY - Respond same day. Nurture relationship."
        
        elif priority >= 55:
            if lifecycle == 'COLD':
                return f"❄️ RE-ENGAGEMENT NEEDED - Warm up {lead_type} contact before pursuing deal."
            else:
                return f"📊 MONITOR {lead_type} - Long-term nurture. Monthly check-ins."
        
        elif priority >= 40:
            return f"⏸️ BORDERLINE {lead_type} - Educate and build relationship. May develop over time."
        
        else:
            if lifecycle in ['NEW', 'COLD']:
                return f"🚫 LOW PRIORITY {lead_type} - Polite decline or minimal effort."
            else:
                return f"🔄 RELATIONSHIP RECOVERY - Focus on engagement before next deal opportunity."
    
    # ========================================
    # LIFECYCLE STAGE DETERMINATION
    # ========================================
    
    def _determine_lifecycle_stage(self, contact: Dict) -> str:
        """
        Determine lifecycle stage based on contact data
        """
        
        created_date = contact.get('createdate')
        if not created_date:
            return 'NEW'
        
        if isinstance(created_date, str):
            try:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            except:
                return 'NEW'
        
        try:
            days_since_created = (datetime.now(created_date.tzinfo) - created_date).days
        except:
            days_since_created = (datetime.now() - created_date).days
        
        # Get activity indicators
        total_deals = contact.get('total_deals_referred') or 0
        closed_deals = contact.get('total_deals_closed') or 0
        touchpoints_count = contact.get('touchpoints_count') or 0
        last_contact_days = contact.get('days_since_last_contact') or 999
        
        # Staging logic
        if days_since_created < 30:
            return 'NEW'
        
        elif days_since_created < 90:
            if touchpoints_count == 0 or last_contact_days > 60:
                return 'COLD'
            else:
                return 'WARMING'
        
        elif days_since_created < 180:
            if touchpoints_count < 3 or last_contact_days > 90:
                return 'COLD'
            elif closed_deals > 0 or total_deals > 0:
                return 'ACTIVE'
            else:
                return 'WARMING'
        
        elif days_since_created < 365:
            if closed_deals > 0:
                return 'ACTIVE'
            elif touchpoints_count >= 5:
                return 'ACTIVE'
            elif last_contact_days > 120:
                return 'COLD'
            else:
                return 'WARMING'
        
        else:  # 365+ days
            if closed_deals >= 2:
                return 'ESTABLISHED'
            elif closed_deals == 1 and touchpoints_count >= 10:
                return 'ACTIVE'
            elif last_contact_days > 180:
                return 'COLD'
            else:
                return 'ACTIVE'
    
    # ========================================
    # DATABASE OPERATIONS
    # ========================================
    
    def _fetch_contact_data(self, contact_id: int) -> Optional[Dict]:
        """Fetch complete contact data"""
        
        self.cursor.execute("""
            SELECT * FROM contacts WHERE id = ?
        """, (contact_id,))
        
        return self.cursor.fetchone()
    
    def _update_lifecycle_stage(self, contact_id: int, new_stage: str):
        """Update lifecycle stage for contact"""
        
        self.cursor.execute("""
            UPDATE contacts
            SET lifecycle_stage = ?,
                stage_changed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_stage, contact_id))
        
        self.db.commit()
    
    def _save_scores_to_db(self, result: Dict):
        """Save all scores to database"""
        
        contact_id = result['contact_id']
        
        try:
            # Save MDCP score
            self.cursor.execute("""
                INSERT INTO mdcp_scores (
                    contact_id, lead_type, lifecycle_stage,
                    mdcp_total, money_score, decision_score, credibility_score, pain_score,
                    money_weight, decision_weight, credibility_weight, pain_weight,
                    mdcp_tier, calculation_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                result['lead_type'],
                result['lifecycle_stage'],
                result['mdcp_score'],
                result['mdcp_breakdown']['Money'],
                result['mdcp_breakdown']['Decision'],
                result['mdcp_breakdown']['Credibility'],
                result['mdcp_breakdown']['Pain'],
                result['mdcp_breakdown']['weights']['Money'],
                result['mdcp_breakdown']['weights']['Decision'],
                result['mdcp_breakdown']['weights']['Credibility'],
                result['mdcp_breakdown']['weights']['Pain'],
                result['mdcp_tier'],
                self.VERSION
            ))
            
            # Save RSS score (if applicable)
            if result['rss_score'] is not None:
                self.cursor.execute("""
                    INSERT INTO rss_scores (
                        contact_id, rss_total, familiarity_score, engagement_score, productivity_score,
                        rss_tier, lifecycle_stage, can_calculate_full_rss, calculation_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact_id,
                    result['rss_score'],
                    result['rss_breakdown']['familiarity'],
                    result['rss_breakdown']['engagement'],
                    result['rss_breakdown']['productivity'],
                    result['rss_tier'],
                    result['lifecycle_stage'],
                    1 if result['lifecycle_stage'] not in ['NEW', 'COLD'] else 0,
                    self.VERSION
                ))
            
            # Save priority score
            self.cursor.execute("""
                INSERT INTO priority_scores (
                    contact_id, mdcp_score, rss_score, priority_score,
                    lead_type, lifecycle_stage, recommended_action, urgency_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                result['mdcp_score'],
                result['rss_score'],
                result['priority_score'],
                result['lead_type'],
                result['lifecycle_stage'],
                result['recommended_action'],
                result['urgency_level']
            ))
            
            self.db.commit()
        except Exception as e:
            print(f"Error saving scores: {e}")
            self.db.rollback()
    
    def _update_metadata(self, key: str, value: str):
        """Update metadata table"""
        
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO apex_metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            
            self.db.commit()
        except Exception as e:
            print(f"Error updating metadata: {e}")


# Convenience functions
def score_contact(contact_id: int, db_path: str = 'apex.db') -> Dict:
    """Quick function to score a single contact"""
    engine = ApexScoringEngine(db_path)
    return engine.score_contact(contact_id)


def score_all_contacts(lead_type: Optional[str] = None, db_path: str = 'apex.db') -> List[Dict]:
    """Quick function to score all contacts"""
    engine = ApexScoringEngine(db_path)
    return engine.score_all_contacts(lead_type)


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'apex.db'
    
    print("[APEX INTELLIGENCE] Starting scoring engine...")
    print(f"  → Database: {db_path}")
    
    engine = ApexScoringEngine(db_path)
    results = engine.score_all_contacts()
    
    print(f"\n[APEX INTELLIGENCE] Scoring complete!")
    print(f"  → Total contacts scored: {len(results)}")
    
    if results:
        print("\n[TOP 10 PRIORITY CONTACTS]")
        print("=" * 100)
        for i, contact in enumerate(results[:10], 1):
            print(f"\n{i}. {contact['contact_name']} ({contact['company']})")
            print(f"   Lead Type: {contact['lead_type']} | Lifecycle: {contact['lifecycle_stage']}")
            print(f"   MDCP: {contact['mdcp_score']}/100 ({contact['mdcp_tier']}) | RSS: {contact['rss_score'] or 'N/A'}")
            print(f"   Priority: {contact['priority_score']}/100 ({contact['urgency_level']})")
            print(f"   Action: {contact['recommended_action']}")
