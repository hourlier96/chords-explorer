import requests


class HooktheoryClient:
    def __init__(self, username, password):
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

            # Hooktheory renvoie souvent 'activetoken'
            print(data)
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
        if not self.token:
            print("Action impossible : pas de token valide.")
            return None

        url = f"{self.base_url}/trends/nodes"
        params = {"cp": chords_degrees}
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Erreur lors de l'appel API : {e}")
            return None


# --- CONFIGURATION ET TEST ---

# 1. Remplacez par vos vrais identifiants
USER = "augu.hourlier@gmail.com"
PASS = "01Ziezot"

client = HooktheoryClient(USER, PASS)

if client.token:
    print("Connecté ! Token récupéré.\n")

    # 2. Exemple : On analyse la suite Am - G - C (en Do Majeur : 6, 5, 1)
    # L'API renvoie les probabilités pour l'accord SUIVANT.
    ma_suite = "6,5,1"
    resultats = client.analyze_progression(ma_suite)

    if resultats:
        print(f"Analyse pour la suite [{ma_suite}] :")
        for suggestion in resultats[:5]:  # On affiche les 5 probabilités les plus hautes
            print(
                f"- Accord suivant probable : {suggestion['chord_ID']} ({round(float(suggestion['probability']) * 100, 2)}%)"
            )
else:
    print("Échec de l'initialisation du client.")
