def _ensure_playwright_browsers(self):
    import subprocess
    import sys
    import os
    import platform
    import shutil
    
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
            executable_dir = os.path.dirname(sys.executable)
            
            bundled_browsers = os.path.join(executable_dir, '.local-browsers')
            
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
            
            if os.path.exists(bundled_browsers):
                print(f"📦 Found bundled browsers at: {bundled_browsers}")
                print(f"📋 Copying to: {base_path}")
                
                os.makedirs(base_path, exist_ok=True)
                
                for item in os.listdir(bundled_browsers):
                    src = os.path.join(bundled_browsers, item)
                    dst = os.path.join(base_path, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        print(f"  ✅ Copied {item}")
                    else:
                        shutil.copy2(src, dst)
                        print(f"  ✅ Copied {item}")
                        
                print("✅ Bundled browsers extracted successfully")
            else:
                print("⚠️ No bundled browsers found in executable directory")
        else:
            base_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '.playwright_browsers'
            )

        os.makedirs(base_path, exist_ok=True)
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = base_path
        print(f"📁 Browser path: {base_path}")
        
        browsers_exist = False
        chromium_executable = None
        chromium_revision = None
        
        for root, dirs, files in os.walk(base_path):
            if 'chromium' in root.lower():
                for file in files:
                    if file.lower() == 'chrome' and 'wrapper' not in file.lower():
                        full_path = os.path.join(root, file)
                        if os.path.exists(full_path):
                            os.chmod(full_path, 0o755)
                            chromium_executable = full_path
                            chromium_revision = os.path.basename(os.path.dirname(root))
                            browsers_exist = True
                            print(f"✅ Found Chromium executable at: {full_path}")
                            break
                
                if not chromium_executable:
                    for sub_root, sub_dirs, sub_files in os.walk(root):
                        for file in sub_files:
                            if file.lower() == 'chrome' and 'wrapper' not in file.lower():
                                full_path = os.path.join(sub_root, file)
                                if os.path.exists(full_path):
                                    os.chmod(full_path, 0o755)
                                    chromium_executable = full_path
                                    chromium_revision = os.path.basename(os.path.dirname(root))
                                    browsers_exist = True
                                    print(f"✅ Found Chromium executable at: {full_path}")
                                    break
                        if chromium_executable:
                            break
                
                if browsers_exist:
                    break
        
        if browsers_exist and chromium_executable:
            print("✅ Playwright browsers found and ready")
            
            os.environ['LD_LIBRARY_PATH'] = os.path.dirname(chromium_executable) + ':' + os.environ.get('LD_LIBRARY_PATH', '')
            
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        executable_path=chromium_executable,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--disable-features=UseOzonePlatform',
                            '--ozone-platform-hint=x11'
                        ]
                    )
                    browser.close()
                    print("✅ Browser launched successfully")
                return True
            except Exception as e:
                print(f"⚠️ Browser verification failed with executable path: {e}")
                
                try:
                    from playwright.sync_api import sync_playwright
                    with sync_playwright() as p:
                        browser = p.chromium.launch(
                            headless=True,
                            args=[
                                '--no-sandbox',
                                '--disable-setuid-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-gpu'
                            ]
                        )
                        browser.close()
                        print("✅ Browser launched successfully (standard method)")
                    return True
                except Exception as e2:
                    print(f"⚠️ Second attempt failed: {e2}")
                    
                    try:
                        system_chrome = shutil.which('google-chrome') or shutil.which('chrome') or shutil.which('chromium')
                        if system_chrome:
                            print(f"📦 Trying system Chrome at: {system_chrome}")
                            from playwright.sync_api import sync_playwright
                            with sync_playwright() as p:
                                browser = p.chromium.launch(
                                    headless=True,
                                    executable_path=system_chrome,
                                    args=['--no-sandbox', '--disable-dev-shm-usage']
                                )
                                browser.close()
                                print("✅ System Chrome launched successfully")
                            return True
                    except:
                        pass
                    
                    return False
        
        print("⚠️ Playwright browsers not found")
        
        if is_frozen:
            print("Attempting to locate browsers in alternate locations...")
            alternate_paths = [
                os.path.join(executable_dir, 'playwright'),
                os.path.join(executable_dir, 'browsers'),
                os.path.join(executable_dir, '_internal', '.local-browsers'),
            ]
            
            for alt_path in alternate_paths:
                if os.path.exists(alt_path):
                    print(f"Found alternate browser location: {alt_path}")
                    shutil.copytree(alt_path, base_path, dirs_exist_ok=True)
                    return self._ensure_playwright_browsers()
            
            print("\n" + "!" * 60)
            print("PLAYWRIGHT BROWSERS NEED TO BE INSTALLED")
            print("!" * 60)
            print("\nPC-Scraper needs to install browser components to function.")
            print("This is a one-time setup that will download approximately 200MB.")
            print(f"\nBrowsers will be installed to: {base_path}")
            
            try:
                response = input("\nInstall now? (y/n): ").lower().strip()
            except:
                response = _show_installation_dialog()
            
            if response == 'y':
                print("\n📦 Installing Playwright and browsers...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], 
                                 check=True, capture_output=True)
                    
                    print("  → Downloading Chromium browser...")
                    result = subprocess.run(
                        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    
                    if result.returncode == 0:
                        print("  ✅ Chromium downloaded successfully")
                        
                        browser_source = None
                        possible_paths = [
                            os.path.expanduser("~/.cache/ms-playwright"),
                            os.path.expanduser("~/.cache/playwright"),
                        ]
                        
                        for path in possible_paths:
                            if os.path.exists(path):
                                browser_source = path
                                break
                        
                        if browser_source:
                            print(f"  📋 Copying browsers to app directory...")
                            for item in os.listdir(browser_source):
                                if 'chromium' in item.lower():
                                    src = os.path.join(browser_source, item)
                                    dst = os.path.join(base_path, item)
                                    if os.path.isdir(src):
                                        shutil.copytree(src, dst, dirs_exist_ok=True)

                                        for froot, fdirs, ffiles in os.walk(dst):
                                            for file in ffiles:
                                                if file == 'chrome':
                                                    os.chmod(os.path.join(froot, file), 0o755)
                                                    print(f"    ✅ Made executable: {os.path.join(froot, file)}")
                        
                        print("\n✅ Installation complete!")
                        return _ensure_playwright_browsers()
                    else:
                        print(f"❌ Installation failed: {result.stderr}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Installation failed: {e}")
                    return False
            else:
                print("\n❌ Installation cancelled.")
                return False
        else:
            print("📦 Attempting to install Playwright browsers (development mode)...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True, capture_output=True)
                result = subprocess.run(
                    [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    print("✅ Chromium installed successfully")
                    return self._ensure_playwright_browsers()
                else:
                    print(f"❌ Installation failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Installation error: {e}")
                return False
                
    except ImportError as e:
        print(f"⚠️ Playwright import error: {e}")
        if is_frozen:
            print("\n" + "!" * 60)
            print("PLAYWRIGHT NOT AVAILABLE")
            print("!" * 60)
            print("\nPlease run: pip install playwright")
            return False
        else:
            print("📦 Installing Playwright...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
                return self._ensure_playwright_browsers()
            except Exception as install_error:
                print(f"❌ Failed to install Playwright: {install_error}")
                return False
    except Exception as e:
        print(f"❌ Unexpected error in browser check: {e}")
        return False

def _show_installation_dialog():
    """Fallback GUI dialog for when console input isn't available"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        response = messagebox.askyesno(
            "PC-Scraper - Browser Installation Required",
            "PC-Scraper needs to install browser components to function.\n\n"
            "This is a one-time setup that will download approximately 200MB.\n"
            "An internet connection is required.\n\n"
            "Install now?",
            icon='question'
        )
        
        root.destroy()
        return 'y' if response else 'n'
    except:
        return 'n'