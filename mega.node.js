const { Storage } = require('megajs');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class MegaHandler {
    constructor(email, password) {
        this.email = email;
        this.password = password;
        this.storage = null;
        
        Object.defineProperty(global, 'crypto', {
            value: {
                getRandomValues: arr => crypto.randomBytes(arr.length)
            }
        });
    }

    async connect() {
        if (!this.storage) {
            this.storage = await new Storage({
                email: this.email,
                password: this.password
            }).ready;
        }
        return this.storage;
    }

    async createRemoteFolder(folderPath) {
        const storage = await this.connect();
        const parts = folderPath.split('/').filter(Boolean);
        let currentFolder = storage.root;

        for (const part of parts) {
            let folder = currentFolder.children.find(f => f.name === part && f.directory);
            if (!folder) {
                folder = await currentFolder.mkdir(part);
                console.log(`Utworzono folder: ${part}`);
            }
            currentFolder = folder;
        }
        return currentFolder;
    }

    async uploadFile(sourcePath, megaPath) {
        const storage = await this.connect();
        const fileContent = await fs.readFile(sourcePath);
        
        // Tworzenie struktury folderów jeśli potrzebna
        const dirPath = path.dirname(megaPath);
        if (dirPath !== '.') {
            const folder = await this.createRemoteFolder(dirPath);
            // Upload pliku do konkretnego folderu - używamy pełnej nazwy pliku
            const file = await folder.upload(megaPath.split('/').pop(), fileContent).complete;
            console.log(`Plik został pomyślnie wysłany do ${megaPath}`);
            return file;
        } else {
            // Upload pliku do głównego katalogu
            const file = await storage.upload(megaPath, fileContent).complete;
            console.log(`Plik został pomyślnie wysłany do ${megaPath}`);
            return file;
        }
    }

    async uploadDirectory(sourcePath, megaPath) {
        const files = await fs.readdir(sourcePath, { withFileTypes: true });
        const results = [];
        
        // Najpierw tworzenie folderu głównego
        const remoteFolder = await this.createRemoteFolder(megaPath);
        
        // Następnie upload plików i podfolderów
        for (const dirent of files) {
            const localPath = path.join(sourcePath, dirent.name);
            // Ważna zmiana: używamy path.join dla ścieżki w MEGA
            const remotePath = path.join(megaPath, dirent.name).replace(/\\/g, '/');
            
            if (dirent.isFile()) {
                const result = await this.uploadFile(localPath, remotePath);
                results.push(result);
            } else if (dirent.isDirectory()) {
                const subResults = await this.uploadDirectory(localPath, remotePath);
                results.push(...subResults);
            }
        }
        
        return results;
    }

    async downloadFile(megaFileName, localFilePath) {
        const storage = await this.connect();
        
        // Szukamy pliku rekurencyjnie w strukturze folderów
        const findFileInFolder = (folder, fileName) => {
            for (const item of folder.children) {
                if (!item.directory && item.name === fileName) {
                    return item;
                }
                if (item.directory) {
                    const found = findFileInFolder(item, fileName);
                    if (found) return found;
                }
            }
            return null;
        };

        const file = findFileInFolder(storage.root, path.basename(megaFileName));
        
        if (!file) {
            throw new Error(`Nie znaleziono pliku: ${megaFileName}`);
        }
        
        const fileContent = await file.downloadBuffer();
        await fs.mkdir(path.dirname(localFilePath), { recursive: true });
        await fs.writeFile(localFilePath, fileContent);
        
        console.log(`Plik został pomyślnie pobrany z MEGA`);
        return file;
    }
}

// Główna funkcja obsługująca argumenty
async function main() {
    try {
        const args = process.argv.slice(2);
        
        if (args.length === 0) {
            console.error('Brak argumentów. Użycie:');
            console.error('1. Upload pliku:    node mega.node.js ./plik.txt uploads/folder');
            console.error('2. Upload folderu:  node mega.node.js ./folder uploads/backup');
            console.error('3. Download pliku:  node mega.node.js plik.txt ./pobrane/plik.txt');
            console.error('4. Download folderu: node mega.node.js folder ./pobrane/folder');
            process.exit(1);
        }

        // Wczytanie danych logowania
        const accountData = JSON.parse(await fs.readFile('mega_account.json', 'utf8'));
        const mega = new MegaHandler(accountData.email, accountData.password);
        
        if (args[0] === "--create-folder") {
            const folderPath = args[1];
            await mega.createRemoteFolder(folderPath);
            process.exit(0);
        } else if (args.length === 1) {
            const sourcePath = args[0];
            const megaPath = path.basename(sourcePath);
            const stats = await fs.stat(sourcePath);
            
            if (stats.isFile()) {
                await mega.uploadFile(sourcePath, megaPath);
            } else {
                await mega.uploadDirectory(sourcePath, megaPath);
            }
        } else if (args.length === 2) {
            const sourcePath = args[0];
            const targetPath = args[1];
            
            if (await fs.access(sourcePath).then(() => true).catch(() => false)) {
                const stats = await fs.stat(sourcePath);
                if (stats.isFile()) {
                    await mega.uploadFile(sourcePath, targetPath);
                } else {
                    await mega.uploadDirectory(sourcePath, targetPath);
                }
            } else {
                await mega.downloadFile(sourcePath, targetPath);
            }
        }
        
        process.exit(0);
    } catch (error) {
        console.error('Wystąpił błąd:', error);
        process.exit(1);
    }
}

process.on('unhandledRejection', (error) => {
    console.error('Nieobsłużony błąd asynchroniczny:', error);
    process.exit(1);
});

main();