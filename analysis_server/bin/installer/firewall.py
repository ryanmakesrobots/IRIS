import elevate
import pyufw

def setFirewallRules(port):
    elevate.evelate()
    ufw.add(f"allow {port}")