import requests
import os
import hashlib
import argparse
from pathlib import Path
from functools import lru_cache

class StarCitizenLocalizationUpdater:
    """Gère les mises à jour des fichiers de localisation de Star Citizen"""
    
    REPO_URL = 'https://raw.githubusercontent.com/MrKraken/StarStrings/refs/heads/master/src/For_Players/Data/Localization/english/global.ini'
    GITHUB_REPO_URL = 'https://github.com/MrKraken/StarStrings'

    def __init__(self, sc_path: str):
        self.sc_path = Path(sc_path)
        self.localization_path = self.sc_path / 'data' / 'Localization' / 'english'
        self.file_path = self.localization_path / 'global.ini'
        
    def ensure_directory_exists(self) -> None:
        """Crée le répertoire s'il n'existe pas"""
        self.localization_path.mkdir(parents=True, exist_ok=True)
        
    def file_exists(self) -> bool:
        """Vérifie si le fichier existe"""
        return self.file_path.exists()
    
    @lru_cache(maxsize=1)
    def get_file_hash(self, content: bytes) -> str:
        """Calcule le hash MD5 d'un contenu (avec cache)"""
        return hashlib.md5(content).hexdigest()
    
    def read_local_file(self) -> bytes | None:
        """Lit le fichier local et retourne son contenu"""
        try:
            with open(self.file_path, 'rb') as f:
                return f.read()
        except (FileNotFoundError, OSError) as e:
            print(f"Erreur lors de la lecture du fichier local: {e}")
            return None
    
    def fetch_remote_file(self) -> tuple[bytes | None, str | None]:
        """Récupère le fichier distant et retourne (contenu, message d'erreur)"""
        try:
            response = requests.get(self.REPO_URL, timeout=10)
            response.raise_for_status()
            return response.content, None
        except requests.exceptions.RequestException as e:
            return None, f"Erreur lors de la récupération du fichier distant: {e} \nSource : {self.GITHUB_REPO_URL}"
    
    def save_file(self, content: bytes) -> bool:
        """Sauvegarde le contenu dans le fichier local"""
        try:
            self.ensure_directory_exists()
            with open(self.file_path, 'wb') as f:
                f.write(content)
            return True
        except OSError as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def needs_update(self, local_content: bytes, remote_content: bytes) -> bool:
        """Vérifie si une mise à jour est nécessaire"""
        local_hash = self.get_file_hash(local_content)
        remote_hash = self.get_file_hash(remote_content)
        return local_hash != remote_hash
    
    def check_for_updates(self) -> bool:
        """Vérifie les mises à jour et applique si nécessaire"""
        if not self.file_exists():
            print(f"Fichier local non trouvé: {self.file_path}")
            self.ensure_directory_exists()
        
        remote_content, error = self.fetch_remote_file()
        if error:
            print(error)
            return False
        
        local_content = self.read_local_file()
        
        if local_content is None:
            print("Création du fichier local...")
            return self.save_file(remote_content)
        
        if not self.needs_update(local_content, remote_content):
            print("✅ Aucune mise à jour nécessaire. Version à jour.")
            return True
        
        print("🔄 Mise à jour disponible! Téléchargement en cours...")
        if self.save_file(remote_content):
            print("✅ Mise à jour appliquée avec succès.")
            return True
        else:
            print("❌ Échec de l'application de la mise à jour.")
            return False

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Met à jour les fichiers de localisation de Star Citizen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s                          # Utilise le chemin par défaut
  %(prog)s -p "D:\\StarCitizen\\LIVE"  # Utilise un chemin personnalisé
  %(prog)s --path "C:\\Games\\StarCitizen\\LIVE"
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        type=str,
        default=r'E:\Program Files\Roberts Space Industries\StarCitizen\LIVE',
        help='Chemin d\'installation de Star Citizen (par défaut: %(default)s)'
    )
    
    return parser.parse_args()

def main():
    """Point d'entrée principal"""
    args = parse_arguments()
    
    # Validation du chemin
    if not os.path.exists(args.path):
        print(f"⚠️  Attention: Le chemin '{args.path}' n'existe pas")
        response = input("Voulez-vous continuer quand même? (o/N): ")
        if response.lower() != 'o':
            print("Opération annulée.")
            return 1
    
    updater = StarCitizenLocalizationUpdater(args.path)
    success = updater.check_for_updates()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
    