import os
import time, subprocess, sys
import bin.config as config

def installModules():
    modules = ['pythonufw']
    for package in modules:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

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
    import pythonufw
    ufw.add(f"allow {config.analysisserverport}")

if __name__ == '__main__':
    print('Welcome to Installation Candidate')
    print('Installing Modules')
    installModules()
    print('Building Image Store')
    buildImageStore()
    print('Setting Firewall Rules')
    buildFirewallRules()
