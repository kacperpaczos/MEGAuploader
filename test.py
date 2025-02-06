import unittest
import os
import subprocess
import shutil
import sys
from pathlib import Path
import time
import platform

class TestMegaUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if len(sys.argv) < 2 or sys.argv[1] not in ['node', 'deno']:
            print("Użycie: python test.py [node|deno]")
            sys.exit(1)
        
        cls.runtime = sys.argv[1]
        print(f"\nUruchamiam testy dla wersji: {cls.runtime}")
        
        # Przygotowanie środowiska
        if cls.runtime == 'node':
            subprocess.run([sys.executable, "build.py", "node"])
        else:
            subprocess.run([sys.executable, "build.py", "deno"])
        
        print("\nPrzygotowywanie środowiska testowego...")
        
        # Usuwanie starych katalogów testowych
        for dir_name in ['toUpload', 'downloaded']:
            if os.path.exists(dir_name):
                print(f"Usuwanie starego katalogu: {dir_name}")
                shutil.rmtree(dir_name)
        
        # Tworzenie struktury katalogów
        cls.upload_dir = Path("toUpload")
        cls.download_dir = Path("downloaded")
        cls.upload_dir.mkdir(exist_ok=True)
        cls.download_dir.mkdir(exist_ok=True)
        
        # Tworzenie plików testowych
        print("Tworzenie plików testowych...")
        (cls.upload_dir / "test1.txt").write_text("test1 content")
        (cls.upload_dir / "test2.txt").write_text("test2 content")
        
        test_subdir = cls.upload_dir / "subdir"
        test_subdir.mkdir(exist_ok=True)
        (test_subdir / "test3.txt").write_text("test3 content")
        print("Utworzono strukturę testową.")

    def run_command(self, args):
        if self.__class__.runtime == 'node':
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
        
        print(f"\nUruchamiam: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"ERROR: {result.stderr}", file=sys.stderr)
            
        return result.returncode, result.stdout, result.stderr

    def test_1_upload_single_file(self):
        print("\n=== Test 1: Upload pojedynczego pliku ===")
        source_file = str(self.upload_dir / "test1.txt")
        returncode, output, error = self.run_command([source_file])  # Zmiana: usunięto drugi argument
        self.assertEqual(returncode, 0, f"Upload failed with error: {error}")
        self.assertIn("Plik został pomyślnie wysłany", output)

    def test_2_download_single_file(self):
        print("\n=== Test 2: Download pojedynczego pliku ===")
        download_path = str(self.download_dir / "downloaded_test1.txt")
        returncode, output, error = self.run_command(["test1.txt", download_path])
        self.assertEqual(returncode, 0, f"Download failed with error: {error}")
        self.assertTrue(os.path.exists(download_path))
        
        print(f"Sprawdzanie zawartości pobranego pliku: {download_path}")
        with open(download_path, 'r') as f:
            content = f.read()
            print(f"Zawartość: {content}")
            self.assertEqual(content, "test1 content")

    def test_3_upload_directory(self):
        print("\n=== Test 3: Upload całego katalogu ===")
        returncode, output, error = self.run_command([str(self.upload_dir)])
        self.assertEqual(returncode, 0, f"Directory upload failed with error: {error}")
        self.assertIn("Plik", output)

    def test_4_download_directory_files(self):
        print("\n=== Test 4: Download plików z katalogu ===")
        # Dodajemy opóźnienie, aby MEGA miało czas na przetworzenie plików
        time.sleep(2)
        
        files_to_check = [
            ("test1.txt", "test1 content"),
            ("test2.txt", "test2 content"),
            ("subdir/test3.txt", "test3 content")
        ]
        
        for remote_path, expected_content in files_to_check:
            download_path = str(self.download_dir / remote_path)
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            
            returncode, output, error = self.run_command([remote_path, download_path])
            self.assertEqual(returncode, 0, f"Download of {remote_path} failed with error: {error}")
            self.assertTrue(os.path.exists(download_path), f"File {download_path} does not exist")
            
            with open(download_path, 'r') as f:
                content = f.read()
                print(f"Zawartość {download_path}: {content}")
                self.assertEqual(content, expected_content)

    @classmethod
    def tearDownClass(cls):
        print("\nCzyszczenie po testach...")
        for dir_path in [cls.upload_dir, cls.download_dir]:
            if dir_path.exists():
                print(f"Czyszczenie katalogu: {dir_path}")
                shutil.rmtree(dir_path)
        print("Testy zakończone.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored']) 