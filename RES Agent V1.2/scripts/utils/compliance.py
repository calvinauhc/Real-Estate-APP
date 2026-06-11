# compliance.py
class ComplianceEngine:
    def __init__(self):
        # Load your regulatory data/configs here
        pass

    def is_eligible(self, client_profile, property_data):
        # Centralize all your gates here
        if not self._check_mop(property_data):
            return False, "MOP not met"
        if not self._check_eip(client_profile, property_data):
            return False, "EIP/SPR quota full"
        return True, "Eligible"