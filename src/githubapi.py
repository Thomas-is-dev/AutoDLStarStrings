import requests
from i18n import t

REQUEST_TIMEOUT = 10


def find_global_ini(owner: str, repository: str, branch: str, token: str | None = None) -> str | None:
    """Return the raw URL of the first global.ini found in a GitHub repository (single API request)"""
    headers = {'Authorization': f"token {token}"} if token else {}
    url = f'https://api.github.com/repos/{owner}/{repository}/git/trees/{branch}?recursive=1'
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        print(t('github_error', error=error))
        return None

    if not isinstance(payload, dict) or not isinstance(payload.get('tree'), list):
        print(t('github_invalid'))
        return None

    for item in payload['tree']:
        path = item.get('path', '')
        if item.get('type') == 'blob' and path.rsplit('/', 1)[-1] == 'global.ini':
            return f'https://raw.githubusercontent.com/{owner}/{repository}/refs/heads/{branch}/{path}'
    return None
