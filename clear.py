import os
import shutil
from pathlib import Path

def clear_environment():
    print("Czyszczenie środowiska...")
    
    # Lista elementów do usunięcia
    to_remove = [
        "deno",
        "node",
        "node_modules",
        "__pycache__",
        "mega.esm.js",
        "package-lock.json",
        "mega.exe" if os.name == "nt" else "mega"
    ]
    
    for item in to_remove:
        path = Path(item)
        if path.exists():
            print(f"Usuwanie: {item}")
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        else:
            print(f"Nie znaleziono: {item}")
    
    print("\nŚrodowisko zostało wyczyszczone!")
    print("Aby przywrócić środowisko:")
    print("1. Uruchom 'python setup.py [windows|linux]'")
    print("2. Uruchom 'python build.py'")

if __name__ == "__main__":
    clear_environment()
