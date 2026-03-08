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

# ----------------------------
# Utility functions
# ----------------------------
def clean_build():
    """Clean previous build artifacts"""
    for d in ["build", "dist", "PC-Scraper.AppDir"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Removed {d}")
    for f in glob.glob("*.spec"):
        os.remove(f)
        print(f"Removed {f}")
    print("Clean complete.\n")

def get_playwright_path():
    """Return Playwright browsers path to bundle"""
    local_path = "ms-playwright"
    cache_path = os.path.expanduser("~/.cache/ms-playwright")

    if os.path.exists(local_path):
        print("Found Playwright browsers in local project")
        return local_path
    elif os.path.exists(cache_path):
        print("Found Playwright browsers in cache")
        return cache_path
    return None

def pyinstaller_cmd(name, entry_script, console=True, extra_data=None):
    """Build a pyinstaller command list"""
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", name
    ]

    if not console:
        cmd.insert(2, "--windowed")

    # Add Playwright browsers
    pw_path = get_playwright_path()
    if pw_path:
        cmd.extend(["--add-data", f"{pw_path}{os.pathsep}ms-playwright"])

    # Add extra data
    if extra_data:
        for src, dest in extra_data:
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

    # Hidden imports
    cmd.extend([
        "--hidden-import", "pygame",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "customtkinter",
        "--collect-all", "customtkinter",
        "--collect-all", "pygame",
        "--collect-all", "playwright",
        entry_script
    ])

    # Icon
    icon = "images/scraper-icon.ico" if platform.system() == "Windows" else "images/scraper-icon.jpeg"
    if os.path.exists(icon):
        cmd.extend(["--icon", icon])

    return cmd

# ----------------------------
# Build functions
# ----------------------------
def build_windows(console=False):
    """Build Windows executable"""
    print(f"Building Windows ({'console' if console else 'windowed'})...")
    name = "PC-Scraper-Console" if console else "PC-Scraper"
    cmd = pyinstaller_cmd(name, "pc-scraper-gui.py", console=console,
                          extra_data=[("images", "images"), ("Music", "Music")])
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("Windows build complete!\n")

    if not console:
        create_windows_debug_scripts()

def create_windows_debug_scripts():
    """Create run-debug.bat and run-debug.ps1"""
    os.makedirs("dist", exist_ok=True)
    bat = """@echo off
echo ========================================
echo PC-Scraper Debug Console
echo ========================================
PC-Scraper-Console.exe
pause
"""
    with open("dist/run-debug.bat", "w") as f:
        f.write(bat)

    ps = """Write-Host "========================================"
Write-Host "PC-Scraper Debug Console"
Start-Process "PC-Scraper-Console.exe" -NoNewWindow -Wait
"""
    with open("dist/run-debug.ps1", "w") as f:
        f.write(ps)
    print("Debug scripts created\n")

def build_linux():
    """Build Linux executable"""
    print("Building Linux...")
    cmd = pyinstaller_cmd("pc-scraper", "pc-scraper-gui.py",
                          console=True,
                          extra_data=[("images", "images"), ("Music", "Music")])
    subprocess.run(cmd, check=True)
    print("Linux build complete!\n")
    create_linux_desktop_files()

def create_linux_desktop_files():
    """Create .desktop file and icon folder"""
    icon_dir = "dist/icons/hicolor"
    os.makedirs(f"{icon_dir}/256x256/apps", exist_ok=True)

    # Copy icon
    icon_src = "images/scraper-icon.jpeg"
    if os.path.exists(icon_src):
        shutil.copy(icon_src, f"{icon_dir}/256x256/apps/pc-scraper.png")

    desktop_content = f"""[Desktop Entry]
Name=PC-Scraper
Comment=PC Parts Scraper Application
Exec={os.path.abspath('dist/pc-scraper')}
Icon=pc-scraper
Terminal=true
Type=Application
Categories=Utility;Application;
StartupWMClass=pc-scraper
"""
    with open("dist/pc-scraper.desktop", "w") as f:
        f.write(desktop_content)
    print(".desktop file created\n")

def build_macos():
    """Build macOS executable"""
    print("Building macOS...")
    cmd = pyinstaller_cmd("PC-Scraper", "pc-scraper-gui.py", console=False,
                          extra_data=[("images", "images"), ("Music", "Music")])
    subprocess.run(cmd, check=True)
    print("macOS build complete!\n")

# ----------------------------
# Main function
# ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py [windows|linux|macos|all|clean|console]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "clean":
        clean_build()
    elif cmd == "windows":
        build_windows(console=False)
    elif cmd == "console":
        build_windows(console=True)
    elif cmd == "linux":
        build_linux()
    elif cmd == "macos":
        build_macos()
    elif cmd == "all":
        clean_build()
        os_system = platform.system()
        if os_system == "Windows":
            build_windows(console=False)
            build_windows(console=True)
        elif os_system == "Linux":
            build_linux()
            if shutil.which("wine"):
                build_windows(console=False)
                build_windows(console=True)
        elif os_system == "Darwin":
            build_macos()
    else:
        print("Unknown command:", cmd)
        sys.exit(1)

if __name__ == "__main__":
    main()