def _ensure_playwright_browsers(self):
    import subprocess
    import sys
    import os
    import platform
    import threading
    
    print("\n" + "=" * 60)
    print("🔍 PLAYWRIGHT BROWSER CHECK")
    print("=" * 60)
    
    try:
        is_frozen = getattr(sys, 'frozen', False)
        print(f"📦 Running from: {'executable' if is_frozen else 'development'}")
        
        is_windows = sys.platform.startswith('win') or 'windows' in platform.system().lower()
        is_wine = 'wine' in sys.executable.lower() if hasattr(sys, 'executable') else False
        
        print(f"💻 Platform: sys.platform={sys.platform}, is_windows={is_windows}, is_wine={is_wine}")
        
        if is_frozen:
            if is_windows or is_wine:
                base_path = os.path.join(
                    os.environ.get('APPDATA', os.path.expanduser('~')),
                    'PC-Scraper', 'browsers'
                )
            else:
                base_path = os.path.join(
                    os.path.expanduser('~'),
                    '.cache', 'pc-scraper', 'browsers'
                )
        else:
            base_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '.playwright_browsers'
            )

        os.makedirs(base_path, exist_ok=True)
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = base_path
        print(f"📁 Browser path: {base_path}")
        
        browsers_exist = False
        chromium_found = False
        
        for root, dirs, files in os.walk(base_path):
            if 'chromium' in root.lower() and any('chrome' in f.lower() for f in files):
                chromium_found = True
                browsers_exist = True
                print(f"✅ Found Chromium at: {root}")
                break
        
        if browsers_exist:
            print("✅ Playwright browsers found in cache")
            
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    exec_path = p.chromium.executable_path
                    if os.path.exists(exec_path):
                        print(f"✅ Browser executable verified: {exec_path}")
                    else:
                        print(f"⚠️ Browser executable not found at: {exec_path}")
                        browsers_exist = False
            except:
                pass
                
            if browsers_exist:
                return True
        
        print("⚠️ Playwright browsers not found or broken")
        
        if is_frozen:
            print("\n" + "!" * 60)
            print("PLAYWRIGHT BROWSERS NEED TO BE INSTALLED")
            print("!" * 60)
            print("\nSince you're running the packaged application, you need to:")
            print("1. Open a terminal/command prompt")
            print("2. Run this command to install browsers:")
            print(f"\n   {sys.executable} -m playwright install chromium\n")
            print("3. Or if that doesn't work, run:")
            print(f"\n   python -m playwright install chromium\n")
            print("\nThe browsers will be installed to:")
            print(f"   {base_path}")
            print("\n" + "!" * 60)
            
            return False
        else:
            print("📦 Attempting to install Playwright browsers (development mode)...")
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                    capture_output=True,
                    text=True,
                    timeout=300 
                )
                if result.returncode == 0:
                    print("✅ Chromium installed successfully")
                    return True
                else:
                    print(f"❌ Installation failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Installation error: {e}")
                return False
                
    except ImportError:
        print("⚠️ Playwright not installed")
        if is_frozen:
            print("\n" + "!" * 60)
            print("PLAYWRIGHT NOT INSTALLED")
            print("!" * 60)
            print("\nPlease install Playwright manually:")
            print("1. Open a terminal/command prompt")
            print("2. Run: pip install playwright")
            print("3. Run: playwright install chromium")
            print("!" * 60)
            return False
        else:
            print("📦 Installing Playwright...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
                return self._ensure_playwright_browsers()
            except:
                return False