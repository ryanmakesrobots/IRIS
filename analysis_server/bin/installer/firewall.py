import elevate

def setFirewallRules(port):
    elevate.elevate()
    import pyufw
    ufw.add(f"allow {port}")