def _ensure_playwright_browsers(self):
        """Ensure Playwright browsers are installed"""
        import subprocess
        import sys
        import os
        
        try:
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as p:
                    p.chromium.launch().close()
                    p.firefox.launch().close()
                    p.webkit.launch().close()
                print("✅ Playwright browsers already installed")
                return True
            except Exception as e:
                print(f"⚠️ Playwright browsers not found or broken: {e}")
                print("📦 Installing Playwright browsers...")
                
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                browser_path = os.path.join(base_path, '.playwright_browsers')
                os.makedirs(browser_path, exist_ok=True)
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path
                
                try:
                    subprocess.run(
                        [sys.executable, '-m', 'playwright', 'install'],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(f"✅ Playwright browsers installed successfully to {browser_path}")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install Playwright browsers: {e.stderr}")
                    
                    try:
                        subprocess.run(
                            [sys.executable, '-m', 'playwright', 'install', '--force'],
                            check=True
                        )
                        print("✅ Playwright browsers installed with --force")
                        return True
                    except:
                        print("❌ Critical: Cannot install Playwright browsers")
                        return False
        except ImportError:
            print("⚠️ Playwright not installed, installing...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'playwright'],
                    check=True
                )
                print("✅ Playwright installed")
                return self._ensure_playwright_browsers()
            except:
                print("❌ Failed to install Playwright")
                return False