# scripts/utils/state_manager.py

class AppStateManager:
    def __init__(self):
        # Initializes the session state for the active client
        self.client_profile = {}
        self.affordability_ceiling = 0.0
        self.regulatory_gates = {}  # MOP, EIP, SPR status flags
        self.last_updated = None

    def update_financial_status(self, ceiling, debt_metrics):
        """
        Updates the global ceiling and debt metrics after a 
        financial.py calculation.
        """
        self.affordability_ceiling = ceiling
        self.debt_metrics = debt_metrics
        # Logic to trigger UI refresh across pages
    
    def get_compliance_status(self):
        """Returns the current 'Hard Gate' status for the client."""
        return self.regulatory_gates