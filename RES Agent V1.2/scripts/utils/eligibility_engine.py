# scripts/utils/eligibility_engine.py
import json

def calculate_hdb_eligibility(client_profile, hdb_constraints):
    """
    Compares client profile against hdb_eligibility_matrix.
    Returns a score and list of failure reasons.
    """
    score = 100
    blockers = []
    
    # 1. MOP Check
    if not client_profile.get('mop_met', True):
        score -= 50
        blockers.append("MOP_NOT_MET")
        
    # 2. Citizenship & SPR Quota Check
    if client_profile.get('citizenship') == 'SPR':
        if not client_profile.get('spr_quota_available', True):
            score -= 50
            blockers.append("SPR_QUOTA_REACHED")
            
    # 3. Family Nucleus Check
    if hdb_constraints['eligibility_flags']['family_nucleus_required']:
        if not client_profile.get('has_family_nucleus', False):
            score -= 30
            blockers.append("MISSING_FAMILY_NUCLEUS")

    return {
        "eligibility_score": max(0, score),
        "is_eligible": score >= 100,
        "blockers": blockers
    }