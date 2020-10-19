import os
import time, subprocess, sys
import bin.config as config

def installModules(pipversion):
    modules = ['pyufw', 'elevate']
    for package in modules:
        subprocess.check_call([sys.executable, "-m", pipversion, "install", package])

def buildImageStore():
    requiredFolders = ['classified', 'unclassified']
    try:
        if not os.path.isdir('./imagestore'):
            os.mkdir('./imagestore')

        for folder in requiredFolders:
            if not os.path.isdir(f'./imagestore/{folder}'):
                os.mkdir(f'./imagestore/{folder}')
    except Exception as e:
        print(f'Failed to create ImageStore folders because: {e}')
        time.sleep(5)

def buildFirewallRules():
    import pyufw
    from elevate import elevate
    elevate()
    ufw.add(f"allow {config.analysisserverport}")

if __name__ == '__main__':
    print('Welcome to Installation Candidate')
    print('Installing Modules')
    pipversion = input("If you use pip & pip3 please enter 'pip3' here, otherwise just enter 'pip': ")
    installModules(pipversion)
    print('Building Image Store')
    buildImageStore()
    print('Setting Firewall Rules')
    buildFirewallRules()
