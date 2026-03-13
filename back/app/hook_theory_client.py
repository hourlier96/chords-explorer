import json

import requests


class HooktheoryClient:
    def __init__(self, username, password):
        if not username or not password:
            raise ValueError("HooktheoryClient : required username and password.")
        self.base_url = "https://api.hooktheory.com/v1"
        self.username = username
        self.password = password
        self.token = self._get_token()

    def _get_token(self):
        """Récupère le Bearer Token via les identifiants."""
        url = f"{self.base_url}/users/auth"
        payload = {"username": self.username, "password": self.password}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Lève une erreur si code 4xx ou 5xx
            data = response.json()
            token = data.get("activkey") or data.get("token")
            if not token:
                print("Erreur: Token non trouvé dans la réponse.")
                return None
            return token

        except requests.exceptions.HTTPError as e:
            print(f"Erreur d'authentification : {e}")
            return None

    def analyze_progression(self, chords_degrees):
        """
        Analyse une suite d'accords.
        chords_degrees: string, ex: "1,5,6,4" (pour I - V - vi - IV)
        """
        url = f"{self.base_url}/trends/nodes"
        params = {"cp": chords_degrees}
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        except requests.exceptions.HTTPError as e:
            print(f"Erreur lors de l'appel API : {e}")
            return None
