import sys
import os

# Go up two levels to reach the project root (RES Agent V1.2/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_property_scorer_ranking():
    client_profile = {
        "monthly_income": 10000,
        "preferred_estate": "Tampines",
        "preferred_type": "HDB"
    }
    scorer = PropertyScorer(client_profile)
    
    # Property A: Ideal match
    prop_a = {"estate": "Tampines", "type": "HDB"}
    score_a = scorer.calculate_score(prop_a, monthly_repayment=2000)
    
    # Property B: Poor match
    prop_b = {"estate": "Jurong", "type": "Condo"}
    score_b = scorer.calculate_score(prop_b, monthly_repayment=5000)
    
    assert score_a > score_b

def test_affordability_weighting():
    client_profile = {"monthly_income": 10000, "preferred_estate": "Tampines", "preferred_type": "HDB"}
    scorer = PropertyScorer(client_profile)
    prop_same = {"estate": "Tampines", "type": "HDB"}
    
    score_cheap = scorer.calculate_score(prop_same, monthly_repayment=2000)
    score_expensive = scorer.calculate_score(prop_same, monthly_repayment=5000)
    
    assert score_cheap > score_expensive

class PropertyScorer:
    def __init__(self, client_profile):
        self.client_profile = client_profile

    def calculate_score(self, property_data, monthly_repayment):
        score = 0
        
        # 1. Location match
        if property_data['estate'] == self.client_profile['preferred_estate']:
            score += 50
            
        # 2. Type match
        if property_data['type'] == self.client_profile['preferred_type']:
            score += 30
            
        # 3. Affordability match (lower repayment = higher score)
        # Assuming monthly income is 10k, a 2k payment is very affordable
        if monthly_repayment < (self.client_profile['monthly_income'] * 0.3):
            score += 20
            
        return score