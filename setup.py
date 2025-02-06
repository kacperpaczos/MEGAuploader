import os
import platform
import subprocess
import sys
import shutil
import venv
from pathlib import Path

def run_command(command, cwd=None):
    print(f"Wykonuję: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Błąd: {result.stderr}")
        sys.exit(1)
    return result.stdout

def setup_python_env():
    print("\nKonfiguracja środowiska Python...")
    venv_dir = Path("venv")
    
    if not venv_dir.exists():
        print("Tworzenie wirtualnego środowiska Python...")
        venv.create("venv", with_pip=True)
        
        # Określenie ścieżki do pip
        pip_cmd = str(venv_dir / "Scripts" / "pip.exe") if platform.system() == "Windows" else str(venv_dir / "bin" / "pip")
        
        # Instalacja zależności z requirements.txt
        print("Instalacja zależności z requirements.txt...")
        run_command(f'"{pip_cmd}" install -r requirements.txt')
    else:
        print("Środowisko Python już istnieje.")

def setup_node_env(platform_type):
    print("\nKonfiguracja środowiska Node.js...")
    node_dir = Path("node")
    
    if node_dir.exists():
        print("Środowisko Node.js już istnieje.")
        return
        
    node_dir.mkdir(exist_ok=True)
    node_version = "20.17.0"
    
    if platform_type == 'windows':
        node_url = f"https://nodejs.org/dist/v{node_version}/node-v{node_version}-win-x64.zip"
        archive_name = "node.zip"
        
        # Download and extract Node.js
        run_command(f"curl -L {node_url} -o {archive_name}")
        run_command(f"powershell Expand-Archive {archive_name} -DestinationPath .")
        
        # Move contents and preserve npm files
        extracted_dir = f"node-v{node_version}-win-x64"
        for item in os.listdir(extracted_dir):
            source = os.path.join(extracted_dir, item)
            target = os.path.join("node", item)
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
            if os.path.isdir(source):
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        
        # Cleanup
        shutil.rmtree(extracted_dir)
        os.remove(archive_name)
        
        # Initialize npm and install dependencies
        run_command("node\\npm.cmd install npm@latest -g")
        run_command("node\\npm.cmd install megajs")
    else:
        node_url = f"https://nodejs.org/dist/v{node_version}/node-v{node_version}-linux-x64.tar.gz"
        archive_name = "node.tar.gz"
        
        run_command(f"curl -L {node_url} -o {archive_name}")
        run_command(f"tar xzf {archive_name}")
        run_command(f"mv node-v{node_version}-linux-x64/* node/")
        
        # Czyszczenie
        shutil.rmtree(f"node-v{node_version}-linux-x64")
        os.remove(archive_name)
        
        # Instalacja zależności
        run_command("./node/bin/npm install megajs")

def setup_deno_env(platform_type):
    print("\nKonfiguracja środowiska Deno...")
    deno_dir = Path("deno")
    
    if deno_dir.exists():
        print("Środowisko Deno już istnieje.")
        return
        
    deno_dir.mkdir(exist_ok=True)
    
    if platform_type == 'windows':
        deno_url = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"
        archive_name = "deno.zip"
        run_command(f"curl -L {deno_url} -o {archive_name}")
        run_command(f"powershell Expand-Archive {archive_name} -DestinationPath deno")
        os.remove(archive_name)
    else:
        deno_url = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip"
        archive_name = "deno.zip"
        run_command(f"curl -L {deno_url} -o {archive_name}")
        run_command(f"unzip {archive_name} -d deno")
        os.remove(archive_name)
        run_command("chmod +x deno/deno")

def check_python_version():
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"Wymagana wersja Python >= {min_version[0]}.{min_version[1]}")
        print(f"Aktualna wersja: {current_version[0]}.{current_version[1]}")
        sys.exit(1)

def setup_runtime_env(platform_type):
    print("\nSprawdzanie dostępności środowisk wykonawczych...")
    
    # Instalacja Node.js
    print("Instaluję lokalne Node.js...")
    setup_node_env(platform_type)
    
    # Instalacja Deno
    print("Instaluję lokalne Deno...")
    setup_deno_env(platform_type)
    
    return "local_environments"

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['windows', 'linux']:
        print("Użycie: python setup.py [windows|linux]")
        sys.exit(1)
    
    platform_type = sys.argv[1]
    
    # Sprawdzenie wersji Pythona
    check_python_version()
    
    # Konfiguracja środowiska Python
    setup_python_env()
    
    # Konfiguracja środowisk Node.js i Deno
    setup_runtime_env(platform_type)
    
    print("\nKonfiguracja zakończona pomyślnie!")
    print("Możesz teraz:")
    print("1. Zbudować program: python build.py")
    print("2. Uruchomić testy: python test.py")
    print("3. Uruchomić program:")
    if platform_type == 'windows':
        print("   python run.py windows [folder_docelowy] [ścieżka_do_pliku]")
    else:
        print("   python run.py linux [folder_docelowy] [ścieżka_do_pliku]")

if __name__ == "__main__":
    main() 