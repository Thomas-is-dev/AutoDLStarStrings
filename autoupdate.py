import requests
import os
import hashlib
import argparse
from pathlib import Path
from functools import lru_cache
from githubapi import find_file_recursive, update_repo_url, get_repo_url

class StarCitizenLocalizationUpdater:
    """Gère les mises à jour des fichiers de localisation de Star Citizen"""
    
    JSON_FILE = 'repo_url.json'
    JSON_KEY = 'REPO_URL'
    
    def __init__(self, sc_path: str):
        self.sc_path = Path(sc_path)
        self.localization_path = self.sc_path / 'data' / 'Localization' / 'english'
        self.file_path = self.localization_path / 'global.ini'
        self.repo_url = self._get_or_find_url()
        
    def _get_or_find_url(self):
        """Récupère l'URL existante ou en trouve une nouvelle"""
        url = get_repo_url(self.JSON_FILE, self.JSON_KEY)
        
        # Si l'URL existe, on la teste
        if url:
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ URL existante valide")
                    return url
            except:
                pass
            print("⚠️  URL existante invalide, recherche d'une nouvelle...")
        
        # Trouver une nouvelle URL
        new_url = find_file_recursive('mrkraken', 'starstrings')
        if new_url:
            update_repo_url(self.JSON_FILE, self.JSON_KEY, new_url)
            return new_url
        
        print("❌ Aucune URL trouvée")
        return None
        
    def ensure_directory_exists(self) -> None:
        """Crée le répertoire s'il n'existe pas"""
        self.localization_path.mkdir(parents=True, exist_ok=True)
        
    def file_exists(self) -> bool:
        """Vérifie si le fichier existe"""
        return self.file_path.exists()
    
    @lru_cache(maxsize=1)
    def get_file_hash(self, content: bytes) -> str:
        """Calcule le hash MD5 d'un contenu"""
        return hashlib.md5(content).hexdigest()
    
    def read_local_file(self) -> bytes | None:
        """Lit le fichier local"""
        try:
            with open(self.file_path, 'rb') as f:
                return f.read()
        except:
            return None
    
    def fetch_remote_file(self) -> tuple[bytes | None, str | None]:
        """Récupère le fichier distant"""
        if not self.repo_url:
            return None, "❌ Aucune URL disponible"
        
        try:
            response = requests.get(self.repo_url, timeout=10)
            response.raise_for_status()
            return response.content, None
        except Exception as e:
            # Si l'URL échoue, chercher une nouvelle
            print(f"⚠️  Échec téléchargement: {e}")
            new_url = find_file_recursive('mrkraken', 'starstrings')
            if new_url and new_url != self.repo_url:
                update_repo_url(self.JSON_FILE, self.JSON_KEY, new_url)
                self.repo_url = new_url
                try:
                    response = requests.get(new_url, timeout=10)
                    response.raise_for_status()
                    return response.content, None
                except:
                    pass
            return None, f"❌ Échec du téléchargement"
    
    def save_file(self, content: bytes) -> bool:
        """Sauvegarde le fichier local"""
        try:
            self.ensure_directory_exists()
            with open(self.file_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def needs_update(self, local_content: bytes, remote_content: bytes) -> bool:
        """Vérifie si une mise à jour est nécessaire"""
        return self.get_file_hash(local_content) != self.get_file_hash(remote_content)
    
    def check_for_updates(self) -> bool:
        """Vérifie les mises à jour et applique si nécessaire"""
        if not self.repo_url:
            print("❌ Aucune URL disponible")
            return False
        
        print(f"🌐 URL: {self.repo_url}")
        print(f"📁 Fichier: {self.file_path}")
        print("-" * 50)
        
        remote_content, error = self.fetch_remote_file()
        if error:
            print(error)
            return False
        
        local_content = self.read_local_file()
        
        if local_content is None:
            print("📝 Création du fichier local...")
            return self.save_file(remote_content)
        
        if not self.needs_update(local_content, remote_content):
            print("✅ Aucune mise à jour nécessaire")
            return True
        
        print("🔄 Mise à jour disponible...")
        if self.save_file(remote_content):
            print("✅ Mise à jour appliquée")
            return True
        else:
            print("❌ Échec mise à jour")
            return False

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description='Met à jour les fichiers de localisation de Star Citizen')
    parser.add_argument(
        '-p', '--path',
        type=str,
        default=r'E:\Program Files\Roberts Space Industries\StarCitizen\LIVE',
        help='Chemin d\'installation de Star Citizen'
    )
    return parser.parse_args()

def main():
    """Point d'entrée principal"""
    args = parse_arguments()
    
    if not os.path.exists(args.path):
        print(f"⚠️  Le chemin '{args.path}' n'existe pas")
        response = input("Continuer? (o/N): ")
        if response.lower() != 'o':
            print("Opération annulée.")
            return 1
    
    updater = StarCitizenLocalizationUpdater(args.path)
    success = updater.check_for_updates()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())