# test_compliance.py
from modules.compliance import check_access # Assuming you built this

def test_security_gate():
    # Test a pending agent
    if not check_access("pending_agent_license"):
        print("✅ SUCCESS: Pending agent is blocked.")
    else:
        print("❌ FAIL: Pending agent was allowed.")

    # Test an active agent
    if check_access("active_agent_license"):
        print("✅ SUCCESS: Active agent is allowed.")
    else:
        print("❌ FAIL: Active agent was blocked.")

if __name__ == "__main__":
    test_security_gate()