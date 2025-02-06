import os
import sys
import shutil
import psutil
from pathlib import Path
from datetime import datetime
import platform
import subprocess

def setup_logging():
    # Utworzenie folderu logs jeśli nie istnieje
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Utworzenie nazwy pliku z logami z aktualną datą
    log_file = os.path.join(logs_dir, f"mega_upload_{datetime.now().strftime('%Y-%m-%d')}.log")
    return log_file

def log_message(log_file, message, print_to_console=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Zapis do pliku
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # Wyświetlenie na konsoli
    if print_to_console:
        print(message)

def check_disk_space(path):
    try:
        total, used, free = shutil.disk_usage(path)
        log_message(log_file, f"\nInformacje o dysku dla {path}:")
        log_message(log_file, f"Całkowita przestrzeń: {total // (2**30)} GB")
        log_message(log_file, f"Użyta przestrzeń: {used // (2**30)} GB")
        log_message(log_file, f"Wolna przestrzeń: {free // (2**30)} GB")
        return free > 1_000_000_000  # Minimum 1GB wolnego miejsca
    except Exception as e:
        log_message(log_file, f"Błąd podczas sprawdzania miejsca na dysku: {e}")
        return False

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def create_timestamped_path(base_folder, source_path):
    # Format: YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    source_name = os.path.basename(source_path)
    
    # Tworzymy ścieżkę: base_folder/timestamp/source_name
    return f"{base_folder}/{timestamp}/{source_name}"

def run_command(runtime, args, operation='upload'):
    if runtime == 'node':
        node_cmd = ".\\node\\node.exe" if platform.system() == "Windows" else "./node/bin/node"
        
        # Czyszczenie i instalacja zależności
        if os.path.exists("node_modules"):
            shutil.rmtree("node_modules")
        npm_cmd = ".\\node\\npm.cmd" if platform.system() == "Windows" else "./node/bin/npm"
        subprocess.run([npm_cmd, "install"], capture_output=True)
        
        cmd = [node_cmd, "mega.node.js"]
        cmd.extend(args)
    else:
        deno_cmd = ".\\deno\\deno.exe" if platform.system() == "Windows" else "./deno/deno"
        cmd = [deno_cmd, "run", "--allow-read", "--allow-write", "--allow-net", "--allow-env", 
              "mega.deno.js"]
        cmd.extend(args)
    
    log_message(log_file, f"\nUruchamiam komendę: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)

def main():
    global log_file
    log_file = setup_logging()
    
    if len(sys.argv) < 4:
        log_message(log_file, "Użycie: python run.py [node|deno] [folder_docelowy] [ścieżka_do_pliku]")
        log_message(log_file, "Przykład: python run.py node uploads C:/moj_plik.txt")
        sys.exit(1)

    runtime = sys.argv[1]
    if runtime not in ['node', 'deno']:
        log_message(log_file, "Błąd: Pierwszy argument musi być 'node' lub 'deno'")
        sys.exit(1)

    # Przygotowanie środowiska
    subprocess.run([sys.executable, "build.py", runtime])
    
    base_folder = sys.argv[2]
    source_path = sys.argv[3]
    
    if not os.path.exists(source_path):
        log_message(log_file, f"Ścieżka {source_path} nie istnieje!")
        sys.exit(1)

    if not check_disk_space(os.path.dirname(source_path)):
        log_message(log_file, "Za mało miejsca na dysku!")
        sys.exit(1)

    mega_path = create_timestamped_path(base_folder, source_path)
    log_message(log_file, f"Ścieżka docelowa w MEGA: {mega_path}")
    
    # Najpierw tworzymy strukturę folderów
    folder_path = os.path.dirname(mega_path)
    if folder_path:
        log_message(log_file, f"\nTworzenie struktury folderów w MEGA: {folder_path}")
        result = run_command(runtime, ["--create-folder", folder_path])
        if result.returncode != 0:
            log_message(log_file, "\nBłąd podczas tworzenia folderów!")
            sys.exit(1)

    # Teraz wysyłamy plik
    result = run_command(runtime, [source_path, mega_path])
    
    if result.stdout:
        log_message(log_file, "\nOutput:")
        log_message(log_file, result.stdout)
    if result.stderr:
        log_message(log_file, "\nBłędy:")
        log_message(log_file, result.stderr)
        
    if result.returncode == 0:
        log_message(log_file, f"\nPlik/folder został pomyślnie wysłany do: {mega_path}")
    else:
        log_message(log_file, "\nWystąpił błąd podczas wysyłania!")
        sys.exit(1)

if __name__ == "__main__":
    main()