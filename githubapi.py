import requests
import json
import os
from settings import GITHUB_TOKEN as TOKEN

def find_file_recursive(username, repository_name, path="", github_token=TOKEN):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
    
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{path}?ref=master'
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        return None
    
    contents = r.json()
    
    for item in contents:
        if item['type'] == 'file' and item['name'] == 'global.ini':
            return item['path']
        elif item['type'] == 'dir':
            result = find_file_recursive(username, repository_name, item['path'], github_token)
            if result:
                return result
    
    return None

def main():
    username = 'mrkraken'
    repository_name = 'starstrings'
    
    path = find_file_recursive(username, repository_name)
    
    if path:
        print(path)
    else:
        print("Fichier non trouvé")

if __name__ == '__main__':
    main()
    