import requests
import json
import os
from settings import GITHUB_TOKEN as TOKEN

def find_file_recursive(username: str, repository_name: str, path: str = "", github_token: str = TOKEN) -> str | None:
    """
    Recherche récursivement un fichier dans un dépôt GitHub.
    """
    headers = {'Authorization': f"token {github_token}"} if github_token else {}
    
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{path}?ref=master'
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"Erreur lors de la récupération du contenu du dépôt: {r.status_code} - {r.text}")
        return None
    
    contents = r.json()
    
    for item in contents:
        if item['type'] == 'file' and item['name'] == 'global.ini':
            return f"https://raw.githubusercontent.com/{username}/{repository_name}/refs/heads/master/{item['path']}"
        elif item['type'] == 'dir':
            result = find_file_recursive(username, repository_name, item['path'], github_token)
            if result:
                return result
    
    return None

def update_repo_url(file_path: str, key_json: str, new_url: str) -> bool:
    """
    Met à jour la clé REPO_URL dans un fichier JSON.
    """
    try:
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"REPO_URL": ""}, f, indent=4)
        
        # Lire et mettre à jour
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if data.get(key_json) == new_url:
            return True
        
        data[key_json] = new_url
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        print(f"✅ {key_json} mis à jour: {new_url}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def get_repo_url(file_path: str, key_json: str) -> str | None:
    """
    Récupère l'URL depuis le fichier JSON.
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(key_json)
    except:
        return None