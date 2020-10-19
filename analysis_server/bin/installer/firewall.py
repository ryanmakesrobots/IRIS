import elevate

def setFirewallRules(port):
    elevate.evelate()
    import pyufw
    ufw.add(f"allow {port}")