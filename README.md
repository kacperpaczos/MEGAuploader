# MEGA Narzędzie do Wysyłania/Pobierania Plików - Instrukcje

## Wymagania systemowe
- Python 3.7 lub nowszy
- Dostęp do Internetu
- **Windows**: PowerShell
- **Linux**: tar, curl

## Instalacja
1. Skonfiguruj środowisko (wybierz odpowiednie dla swojego systemu):
   - **Windows**:
     ```sh
     python setup.py windows
     ```
   - **Linux**:
     ```sh
     python setup.py linux
     ```

## Korzystanie z programu
### Wysyłanie pliku lub folderu
- **Windows**:
  ```sh
  python run.py node [mega_folder_docelowy] [ścieżka_do_pliku_lub_folderu]
  ```
- **Linux**:
  ```sh
  python run.py node [mega_folder_docelowy] [ścieżka_do_pliku_lub_folderu]
  ```
#### Przykłady:
```sh
python3 run.py node DaneMega C:\documents\file.txt
python3 run.py node FolderMega /home/user/documents
```

## Struktura katalogów w MEGA
```
DaneMega/
  2024-01-20_15-30-45/
    file.txt
```
LUB dla folderu:
```
FolderMega/
  2024-01-20_15-30-45/
    documents/
      file1.txt
      file2.txt
```

## Testy
Uruchamianie testów:
```sh
python3 test.py node
```

## Rozwiązywanie problemów
### a) Błąd dostępu do MEGA:
- Sprawdź połączenie internetowe
- Sprawdź dane logowania w `mega_account.json`

### b) Błąd braku miejsca:
- Wymagane minimum 1GB wolnego miejsca
- Zwolnij miejsce na dysku

### c) Problemy z testami:
- Upewnij się, że katalogi `toUpload` i `downloaded` nie istnieją
- Sprawdź logi błędów w konsoli

## Pliki projektu
- `mega.node.js` - główny skrypt Node.js
- `mega.deno.js` - główny skrypt Deno
- `run.py` - nakładka Pythona
- `setup.py` - skrypt instalacyjny
- `test.py` - testy jednostkowe

## Uwagi
- Program automatycznie tworzy katalogi z znacznikiem czasowym
- Wszystkie operacje są rejestrowane w konsoli
- Kod błędu `1` oznacza wystąpienie problemu
- Kod `0` oznacza pomyślne wykonanie operacji

