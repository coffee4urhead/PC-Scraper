"""
Cross-platform build script for PC-Scraper
Run: python build.py [windows|linux|macos|all|clean|console]
"""

import os
import sys
import shutil
import subprocess
import platform
import glob

def clean_build():
    for d in ["build", "dist", "PC-Scraper.AppDir"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Removed {d}")
    for f in glob.glob("*.spec"):
        os.remove(f)
        print(f"Removed {f}")
    print("Clean complete.\n")

def find_and_bundle_playwright_browsers():
    """Find Playwright browsers and copy to local directory for bundling"""
    import shutil
    import os
    
    print("[INFO] Looking for Playwright browsers to bundle...")
    
    browser_locations = [
        os.path.expanduser("~/.cache/ms-playwright"),  
        os.path.expanduser("~/Library/Caches/ms-playwright"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ms-playwright'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'ms-playwright'),  
    ]
    
    for location in browser_locations:
        if os.path.exists(location):
            print(f"[FOUND] Playwright cache at: {location}")
            
            for item in os.listdir(location):
                if 'chromium' in item.lower():
                    src_path = os.path.join(location, item)
                    dst_path = os.path.join(os.getcwd(), '.local-browsers', item)
                    
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    if os.path.isdir(src_path):
                        print(f"[COPYING] Bundling {item}...")
                        try:
                            shutil.copytree(src_path, dst_path, dirs_exist_ok=True, ignore_errors=True)
                            print(f"[SUCCESS] Bundled {item}")
                            return True
                        except Exception as e:
                            print(f"[ERROR] Failed to copy {item}: {e}")
                            return False
    
    print("[WARNING] No Playwright browsers found to bundle")
    return False

def get_playwright_path():
    local_path = ".local-browsers"
    cache_path = os.path.expanduser("~/.cache/ms-playwright")
    if os.path.exists(local_path):
        return local_path
    elif os.path.exists(cache_path):
        return cache_path
    return None

def pyinstaller_cmd(name, entry_script, console=True, extra_data=None):
    cmd = ["pyinstaller","--onefile","--name",name]
    if not console:
        cmd.insert(2,"--windowed")
    pw_path = get_playwright_path()
    if pw_path:
        cmd.extend(["--add-data", f"{pw_path}{os.pathsep}.local-browsers"])
    if extra_data:
        for src,dest in extra_data:
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
    
    hidden_imports = get_scraper_modules() + [
        "scrapers.all_store_bg_scraper",
        "scrapers.amazon_co_uk_scraper",
        "scrapers.amazon_com_scraper",
        "scrapers.amazon_de_scraper",
        "scrapers.ardes_scraper",
        "scrapers.base_scraper",
        "scrapers.cpu_memory_manager",
        "scrapers.cyber_trade_scraper",
        "scrapers.desktop_bg_scraper",
        "scrapers.ezona_bg_scraper",
        "scrapers.gt_computers",
        "scrapers.hits_bg_scraper",
        "scrapers.jar_computers_scraper",
        "scrapers.optimal_computers_scraper",
        "scrapers.pc_tech_scraper",
        "scrapers.pic_bg_scraper",
        "scrapers.plasico_scraper",
        "scrapers.pro_bg_scraper",
        "scrapers.scraper_container_class",
        "scrapers.scraper_utils",
        "scrapers.senetic_scraper",
        "scrapers.techno_mall_scraper",
        "scrapers.tehnik_store_scraper",
        "scrapers.thnx_bg_scraper",
        "scrapers.tova_bg_scraper",
        "scrapers.xtreme_bg_scraper",
        
        "playwright",
        "playwright.async_api",
        "playwright.sync_api",
        "playwright._impl._driver",
        "playwright._impl._connection",
        "playwright._impl._page",
        "playwright._impl._browser",
        "playwright._impl._browser_context",
        
        "customtkinter",
        "PIL",
        "PIL._tkinter_finder",
        "pygame",
        "yfinance",
        "pillow",
        "pyinstaller",
        "python-dotenv",
        "requests",
        "scipy",
        "selenium",
        "urllib3",
        "xlsxwriter",
        "currency_converter",
        "matplotlib",
        "aiohttp",
        "pandas",
        "numpy",
        "dotenv",
    ]

    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])

    collect_all = ["customtkinter", "pygame", "playwright", "scrapers", "PIL", "matplotlib"]
    for pkg in collect_all:
        cmd.extend(["--collect-all", pkg])

    icon = "images/scraper-icon.ico" if platform.system()=="Windows" else "images/scraper-icon.jpeg"
    if os.path.exists(icon):
        cmd.extend(["--icon",icon])
    
    cmd.append(entry_script)
    return cmd

def get_scraper_modules():
    """Automatically discover all scraper modules"""
    scrapers = []
    scrapers_dir = 'scrapers'
    if os.path.exists(scrapers_dir):
        for file in os.listdir(scrapers_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = f"scrapers.{file[:-3]}"
                scrapers.append(module_name)
    return scrapers

def build_windows(console=False):
    find_and_bundle_playwright_browsers()
    name="PC-Scraper-Console" if console else "PC-Scraper"
    cmd=pyinstaller_cmd(name,"pc-scraper-gui.py",console=console,extra_data=[("images","images"),("Music","Music")])
    subprocess.run(cmd,check=True)
    if not console:
        os.makedirs("dist",exist_ok=True)
        bat='''@echo off
PC-Scraper-Console.exe
pause
'''
        with open("dist/run-debug.bat","w") as f:
            f.write(bat)
        ps='''Start-Process "PC-Scraper-Console.exe" -NoNewWindow -Wait
'''
        with open("dist/run-debug.ps1","w") as f:
            f.write(ps)

def build_linux():
    find_and_bundle_playwright_browsers()
    cmd=pyinstaller_cmd("pc-scraper","pc-scraper-gui.py",console=True,extra_data=[("images","images"),("Music","Music")])
    subprocess.run(cmd,check=True)
    icon_dir="dist/icons/hicolor"
    os.makedirs(f"{icon_dir}/256x256/apps",exist_ok=True)
    icon_src="images/scraper-icon.jpeg"
    if os.path.exists(icon_src):
        shutil.copy(icon_src,f"{icon_dir}/256x256/apps/pc-scraper.png")
    desktop_content=f"""[Desktop Entry]
Name=PC-Scraper
Comment=PC Parts Scraper Application
Exec={os.path.abspath('dist/pc-scraper')}
Icon=pc-scraper
Terminal=true
Type=Application
Categories=Utility;Application;
StartupWMClass=pc-scraper
"""
    with open("dist/pc-scraper.desktop","w") as f:
        f.write(desktop_content)

def build_macos():
    cmd=pyinstaller_cmd("PC-Scraper","pc-scraper-gui.py",console=False,extra_data=[("images","images"),("Music","Music")])
    subprocess.run(cmd,check=True)

def main():
    if len(sys.argv)<2:
        print("Usage: python build.py [windows|linux|macos|all|clean|console]")
        sys.exit(1)
    cmd=sys.argv[1].lower()
    if cmd=="clean":
        clean_build()
    elif cmd=="windows":
        build_windows(console=False)
    elif cmd=="console":
        build_windows(console=True)
    elif cmd=="linux":
        build_linux()
    elif cmd=="macos":
        build_macos()
    elif cmd=="all":
        clean_build()
        os_system=platform.system()
        if os_system=="Windows":
            build_windows(console=False)
            build_windows(console=True)
        elif os_system=="Linux":
            build_linux()
            if shutil.which("wine"):
                build_windows(console=False)
                build_windows(console=True)
        elif os_system=="Darwin":
            build_macos()
    else:
        print("Unknown command:",cmd)
        sys.exit(1)

if __name__=="__main__":
    main()