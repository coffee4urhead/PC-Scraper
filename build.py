"""
Cross-platform build script for PC-Scraper
Run: python build.py [windows|linux|macos|all]
"""

import os
import sys
import shutil
import subprocess
import platform
import glob 

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}")
    
    for file_pattern in files_to_clean:
        for file in glob.glob(file_pattern):
            os.remove(file)
            print(f"Removed {file}")

def build_windows(console=True):
    """Build Windows executable"""
    print("Building for Windows...")
    print(f"Building for Windows with console={'yes' if console else 'no'}...")
    
    icon_path = 'images/scraper-icon.ico'
    if not os.path.exists(icon_path):
        print(f"Warning: {icon_path} not found!")
        if os.path.exists('images/icon.ico'):
            icon_path = 'images/icon.ico'
        elif os.path.exists('images/scraper-icon.jpeg'):
            try:
                from PIL import Image
                img = Image.open('images/scraper-icon.jpeg')
                img.save('images/scraper-icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128)])
                print("Created scraper-icon.ico from JPEG")
                icon_path = 'images/scraper-icon.ico'
            except:
                print("Could not create ICO file")
                icon_path = None

    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'PC-Scraper' + ('-Console' if console else ''),
    ]
    playwright_browsers = None

    try:
        import playwright
        playwright_path = os.path.dirname(playwright.__file__)
        browsers_path = os.path.join(playwright_path, 'driver', 'package', '.local-browsers')
        if os.path.exists(browsers_path):
            playwright_browsers = browsers_path
            print(f"Found Playwright browsers at: {browsers_path}")
    except:
        print("Playwright not found in current environment")
    
    if playwright_browsers:
        cmd.extend(['--add-data', f'{playwright_browsers}{os.pathsep}playwright/.local-browsers'])
        print("Added Playwright browsers to build")

    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
    else:
        print("Warning: Building without icon")
    
    if os.path.exists('version.txt'):
        cmd.extend(['--version-file', 'version.txt'])
    
    cmd.extend([
        '--add-data', f'images{os.pathsep}images',
        '--add-data', f'Music{os.pathsep}Music',
        '--hidden-import', 'pygame',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--collect-all', 'customtkinter',
        '--collect-all', 'pygame',
        'pc-scraper-gui.py'
    ])

    if not console:
        cmd.insert(2, '--windowed')

    if platform.system() != 'Windows':
        print("Warning: Building Windows executable on non-Windows system")
        cmd.extend(['--target-arch', 'win64'])
        os.environ['PYINSTALLER_PLATFORM'] = 'windows'
        cmd.extend(['--add-data', f'images/scraper-icon.ico{os.pathsep}.'])

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("Windows build completed successfully!")
        
        if not console:
            print("Creating debug version with console...")
            debug_cmd = cmd.copy()
            debug_cmd[cmd.index('--name') + 1] = 'PC-Scraper-Debug'
            if '--windowed' in debug_cmd:
                debug_cmd.remove('--windowed')
            subprocess.run(debug_cmd)
        
        create_windows_batch_file()
        
        if shutil.which('wine') and os.path.exists('dist/PC-Scraper.exe'):
            add_windows_resources()
    else:
        print("Windows build failed!")

    print("Windows build complete!")

def create_windows_batch_file():
    """Create a batch file to run the console version"""
    batch_content = """@echo off
echo ========================================
echo PC-Scraper Debug Console
echo ========================================
echo.
echo Starting PC-Scraper with console output...
echo Press Ctrl+C to stop
echo.
PC-Scraper-Console.exe
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)
"""
    with open('dist/run-debug.bat', 'w') as f:
        f.write(batch_content)
    
    ps_content = """Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PC-Scraper Debug Console" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting PC-Scraper with console output..." -ForegroundColor Yellow
Write-Host ""

$process = Start-Process -FilePath "PC-Scraper-Console.exe" -NoNewWindow -PassThru -Wait

if ($process.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "Application exited with error code: $($process.ExitCode)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
"""
    with open('dist/run-debug.ps1', 'w') as f:
        f.write(ps_content)
    
    print("Created debug scripts in dist/ directory")

def add_windows_resources():
    """Add Windows resources using wine and rcedit"""
    try:
        if not os.path.exists('rcedit-x64.exe'):
            print("Downloading rcedit...")
            import urllib.request
            url = "https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe"
            urllib.request.urlretrieve(url, 'rcedit-x64.exe')
        
        exe_path = os.path.abspath('dist/PC-Scraper.exe')
        icon_path = os.path.abspath('images/scraper-icon.ico')
        
        if os.path.exists(icon_path):
            cmd = [
                'wine', 'rcedit-x64.exe', exe_path,
                '--set-icon', icon_path
            ]
            subprocess.run(cmd, capture_output=True)
            print("Added icon to executable using rcedit")
        
        if os.path.exists('version.txt'):
            with open('version.txt', 'r') as f:
                version = f.read().strip()
            
            cmd = [
                'wine', 'rcedit-x64.exe', exe_path,
                '--set-version-string', 'FileDescription', 'PC Scraper Application',
                '--set-version-string', 'ProductName', 'PC-Scraper',
                '--set-version-string', 'CompanyName', 'Your Company',
                '--set-file-version', version,
                '--set-product-version', version
            ]
            subprocess.run(cmd, capture_output=True)
            print("Added version info to executable")
            
    except Exception as e:
        print(f"Could not add Windows resources: {e}")

def build_linux():
    """Build Linux executable"""
    print("Building for Linux...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'pc-scraper',
        '--add-data', f'images{os.pathsep}images',
        '--add-data', f'Music{os.pathsep}Music',
        '--hidden-import', 'pygame',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--collect-all', 'customtkinter',
        '--collect-all', 'pygame',
        'pc-scraper-gui.py'
    ]
    
    subprocess.run(cmd)
    
    create_linux_desktop_files()

    if shutil.which('appimagetool'):
        create_appimage()
    
    print("Linux build complete!")

def create_linux_desktop_files():
    """Create .desktop file and icon for Linux integration"""
    
    icon_dir = 'dist/icons/hicolor'
    os.makedirs(f'{icon_dir}/256x256/apps', exist_ok=True)

    if os.path.exists('images/scraper-icon.jpeg'):
        shutil.copy('images/scraper-icon.jpeg', f'{icon_dir}/256x256/apps/pc-scraper.jpeg')
        
        try:
            from PIL import Image
            img = Image.open('images/scraper-icon.jpeg')
            for size in [16, 32, 48, 64, 128]:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                os.makedirs(f'{icon_dir}/{size}x{size}/apps', exist_ok=True)
                resized.save(f'{icon_dir}/{size}x{size}/apps/pc-scraper.jpeg')
        except:
            print("PIL not available for icon resizing, using only 256x256")
    
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
    
    with open('dist/pc-scraper.desktop', 'w') as f:
        f.write(desktop_content)
    
    print("Created Linux desktop integration files")

def create_appimage():
    """Create AppImage from the executable"""
    appdir = 'PC-Scraper.AppDir'
    if os.path.exists(appdir):
        shutil.rmtree(appdir)
    
    os.makedirs(f'{appdir}/usr/bin')
    os.makedirs(f'{appdir}/usr/share/applications')
    os.makedirs(f'{appdir}/usr/share/icons/hicolor/256x256/apps')
    
    shutil.copy('dist/pc-scraper', f'{appdir}/usr/bin/')
    
    with open(f'{appdir}/pc-scraper.desktop', 'w') as f:
        f.write("""[Desktop Entry]
Name=PC-Scraper
Exec=pc-scraper
Icon=pc-scraper
Type=Application
Categories=Utility
StartupWMClass=pc-scraper
""")
    
    if os.path.exists('images/scraper-icon.jpeg'):
        shutil.copy('images/scraper-icon.jpeg', f'{appdir}/pc-scraper.jpeg')
    
        shutil.copy('images/scraper-icon.jpeg', f'{appdir}/usr/share/icons/hicolor/256x256/apps/pc-scraper.jpeg')
        shutil.copy('images/scraper-icon.jpeg', f'{appdir}/.DirIcon')

        try:
            from PIL import Image
            img = Image.open('images/scraper-icon.jpeg')
            sizes = [16, 32, 48, 64, 128]
            
            for size in sizes:
                size_dir = f'{appdir}/usr/share/icons/hicolor/{size}x{size}/apps'
                os.makedirs(size_dir, exist_ok=True)
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(f'{size_dir}/pc-scraper.jpeg')
        except Exception as e:
            print(f"Icon resizing failed (optional): {e}")

    with open(f'{appdir}/AppRun', 'w') as f:
        f.write("""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
exec "pc-scraper" "$@"
""")
    
    os.chmod(f'{appdir}/AppRun', 0o755)
    
    subprocess.run(['appimagetool', appdir])
    for file in os.listdir('.'):
        if file.endswith('.AppImage'):
            os.rename(file, 'PC-Scraper.AppImage')
            break

    print("AppImage created!")

def build_macos():
    """Build macOS app bundle"""
    print("Building for macOS...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'PC-Scraper',
        '--icon', 'images/icon.icns',
        '--add-data', f'images{os.pathsep}images',
        '--add-data', f'Music{os.pathsep}Music',
        '--hidden-import', 'pygame',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--collect-all', 'customtkinter',
        '--collect-all', 'pygame',
        '--osx-bundle-identifier', 'com.yourname.pc-scraper',
        'pc-scraper-gui.py'
    ]
    
    subprocess.run(cmd)
    print("macOS build complete!")

def main():
    """Main build function"""
    if len(sys.argv) < 2:
        print("Usage: python build.py [windows|linux|macos|all|clean|console]")
        print("  console - Build Windows version with console (debug)")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'clean':
        clean_build()
    elif command == 'windows':
        build_windows(console=False) 
    elif command == 'console':
        build_windows(console=True)   
    elif command == 'linux':
        build_linux()
    elif command == 'macos':
        build_macos()
    elif command == 'all':
        clean_build()
        if platform.system() == 'Windows':
            build_windows(console=False)
            build_windows(console=True)  
        elif platform.system() == 'Linux':
            build_linux()
            if shutil.which('wine'):
                print("Attempting cross-compile for Windows...")
                build_windows(console=False)
                build_windows(console=True)
        elif platform.system() == 'Darwin':
            build_macos()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()