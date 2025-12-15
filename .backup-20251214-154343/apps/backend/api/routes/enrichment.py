# backend/api/routes/enrichment.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
from pathlib import Path
import traceback

# Add intelligence path
BACKEND_DIR = Path(__file__).parent.parent
INTELLIGENCE_PATH = BACKEND_DIR.parent.parent / 'apps' / 'backend' / 'intelligence'
sys.path.insert(0, str(INTELLIGENCE_PATH))

from apex_scoring_engine import ApexScoringEngine
from backend.models.database import Contact, SessionLocal

router = APIRouter()

# Initialize scoring engine
scoring_engine = ApexScoringEngine(db_path='./apex.db')

@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: str):
    """
    Trigger deep enrichment with Apex Intelligence scoring
    Returns immediately after completion (synchronous)
    """
    # Validate contact exists
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Mark as enriching
        contact.enrichment_status = "enriching"
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

    # Perform enrichment synchronously
    try:
        result = await perform_enrichment(contact_id=int(contact_id))
        return {
            "success": True,
            "contact_id": contact_id,
            "status": "completed",
            "message": "Enrichment completed successfully",
            "scores": {
                "mdcp_score": result.get('mdcp_score'),
                "mdcp_tier": result.get('mdcp_tier'),
                "rss_score": result.get('rss_score'),
                "priority_score": result.get('priority_score')
            }
        }
    except Exception as e:
        # Mark as failed in database
        db = SessionLocal()
        try:
            contact = db.query(Contact).filter(Contact.id == int(contact_id)).first()
            if contact:
                contact.enrichment_status = "failed"
                db.commit()
        except:
            db.rollback()
        finally:
            db.close()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Enrichment failed: {str(e)}"
        )

async def perform_enrichment(contact_id: int):
    """
    Background task: Enrich contact with Apex Intelligence scoring
    Returns enrichment result dictionary
    """
    db = SessionLocal()
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()

        if not contact:
            print(f"❌ Contact {contact_id} not found")
            raise ValueError(f"Contact {contact_id} not found")

        print(f"\n{'='*80}")
        print(f"🚀 APEX ENRICHMENT STARTED")
        print(f"   Contact: {contact.first_name} {contact.last_name}")
        print(f"   Company: {contact.company}")
        print(f"{'='*80}\n")

        # ========================================
        # STEP 1: Run Apex Intelligence Scoring
        # ========================================
        print("📊 Running Apex Intelligence scoring...")

        try:
            apex_result = scoring_engine.score_contact(
                contact_id=contact_id,
                save_to_db=True  # This saves to mdcp_scores, rss_scores, priority_scores tables
            )

            print(f"✅ Apex scoring complete!")
            print(f"   MDCP Score: {apex_result['mdcp_score']}/100 ({apex_result['mdcp_tier']})")
            print(f"   RSS Score: {apex_result['rss_score']}/100 ({apex_result['rss_tier']})")
            print(f"   Priority: {apex_result['priority_score']}/100 ({apex_result['urgency_level']})")
            print(f"   Action: {apex_result['recommended_action']}\n")

        except Exception as e:
            print(f"⚠️ Apex scoring error: {e}")
            traceback.print_exc()

            # Fallback to simple scoring
            apex_result = {
                'mdcp_score': 50.0,
                'mdcp_tier': 'QUALIFIED',
                'rss_score': 0,
                'rss_tier': 'N/A',
                'priority_score': 50.0,
                'urgency_level': 'MEDIUM',
                'recommended_action': 'Standard follow-up',
                'lifecycle_stage': 'NEW',
                'lead_type': contact.lead_type or 'BORROWER'
            }

        # ========================================
        # STEP 2: Update Contact Record
        # ========================================
        print("💾 Updating contact record...")

        # Store enrichment data
        contact.enrichment_data = str(apex_result)
        contact.perplexity_data = str({
            'apex_intelligence': apex_result,
            'enriched_at': datetime.utcnow().isoformat()
        })

        # Update scores from Apex
        contact.opportunity_score = apex_result['mdcp_score']
        contact.lead_tier = apex_result['mdcp_tier']

        # Update lifecycle if changed
        if hasattr(contact, 'lifecycle_stage'):
            contact.lifecycle_stage = apex_result.get('lifecycle_stage', 'NEW')

        # Mark as complete
        contact.enrichment_status = "completed"
        contact.enriched_at = datetime.utcnow()

        db.commit()

        print(f"✅ Contact record updated successfully\n")
        print(f"{'='*80}")
        print(f"🎉 ENRICHMENT COMPLETE")
        print(f"   Lead Tier: {contact.lead_tier}")
        print(f"   Opportunity Score: {contact.opportunity_score}/100")
        print(f"{'='*80}\n")
        
        return apex_result

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ENRICHMENT FAILED")
        print(f"   Error: {str(e)}")
        print(f"{'='*80}\n")
        traceback.print_exc()

        # Update status to failed
        try:
            contact.enrichment_status = "failed"
            db.commit()
        except:
            db.rollback()
        
        raise

    finally:
        db.close()
