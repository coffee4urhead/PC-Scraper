"""
Cross-platform build script for PC-Scraper
Run: python build.py [windows|linux|macos|all]
"""

import os
import sys
import shutil
import subprocess
import platform

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}")
    
    for file_pattern in files_to_clean:
        for file in os.glob(file_pattern):
            os.remove(file)
            print(f"Removed {file}")

def build_windows():
    """Build Windows executable"""
    print("Building for Windows...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'PC-Scraper',
        '--icon', 'images/icon.ico',
        '--add-data', f'images:images',
        '--add-data', f'Music:Music',
        '--hidden-import', 'pygame',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--collect-all', 'customtkinter',
        '--collect-all', 'pygame',
        '--version-file', 'version.txt',
        'pc-scraper-gui.py'
    ]
    
    if platform.system() != 'Windows':
        print("Warning: Building Windows executable on non-Windows system")
        cmd.extend(['--target-arch', 'win64'])
    
    subprocess.run(cmd)
    print("Windows build complete!")

def build_linux():
    """Build Linux executable"""
    print("Building for Linux...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'pc-scraper',
        '--add-data', f'images:images',
        '--add-data', f'Music:Music',
        '--hidden-import', 'pygame',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--collect-all', 'customtkinter',
        '--collect-all', 'pygame',
        'pc-scraper-gui.py'
    ]
    
    subprocess.run(cmd)
    
    if shutil.which('appimagetool'):
        create_appimage()
    
    print("Linux build complete!")

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
Categories=Utility;
""")
    
    if os.path.exists('images/icon.png'):
        shutil.copy('images/icon.png', f'{appdir}/pc-scraper.png')
    
    with open(f'{appdir}/AppRun', 'w') as f:
        f.write("""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
exec "pc-scraper" "$@"
""")
    
    os.chmod(f'{appdir}/AppRun', 0o755)
    
    subprocess.run(['appimagetool', appdir])
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
        print("Usage: python build.py [windows|linux|macos|all|clean]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'clean':
        clean_build()
    elif command == 'windows':
        build_windows()
    elif command == 'linux':
        build_linux()
    elif command == 'macos':
        build_macos()
    elif command == 'all':
        clean_build()
        if platform.system() == 'Windows':
            build_windows()
        elif platform.system() == 'Linux':
            build_linux()
            if shutil.which('wine'):
                print("Attempting cross-compile for Windows...")
                build_windows()
        elif platform.system() == 'Darwin':
            build_macos()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()