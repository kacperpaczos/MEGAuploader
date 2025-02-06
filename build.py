import os
import platform
import subprocess
import sys
import json
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    print(f"Wykonuję: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Błąd: {result.stderr}")
        sys.exit(1)
    return result.stdout

def clean_dependencies():
    print("Czyszczenie zależności...")
    if os.path.exists("node_modules"):
        shutil.rmtree("node_modules")
    if os.path.exists("package-lock.json"):
        os.remove("package-lock.json")

def prepare_node_version():
    print("Przygotowywanie wersji Node.js...")
    clean_dependencies()
    print("Wersja Node.js gotowa.")
    print("Aby uruchomić:")
    print("1. python run.py node [argumenty]")
    print("2. python test.py node")

def prepare_deno_version():
    print("Przygotowywanie wersji Deno...")
    clean_dependencies()
    print("Wersja Deno gotowa.")
    print("Aby uruchomić:")
    print("1. python run.py deno [argumenty]")
    print("2. python test.py deno")

def build_executable():
    if len(sys.argv) != 2 or sys.argv[1] not in ['node', 'deno', 'all']:
        print("Użycie: python build.py [node|deno|all]")
        sys.exit(1)
    
    runtime = sys.argv[1]
    print(f"Przygotowuję wersję: {runtime}")
    
    if runtime == 'node' or runtime == 'all':
        prepare_node_version()
    
    if runtime == 'deno' or runtime == 'all':
        prepare_deno_version()

if __name__ == "__main__":
    build_executable()