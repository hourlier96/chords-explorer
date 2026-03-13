import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.hook_theory_client import HooktheoryClient

load_dotenv()

app = FastAPI()


@app.get("/next-chord")
def health_check(suite: str = "6,5,1"):
    client = HooktheoryClient(os.getenv("HT_USER"), os.getenv("HT_PASS"))

    if client.token:
        resultats = client.analyze_progression(suite)

        if resultats:
            return {
                "status": "success",
                "results": resultats[:10],
            }

    else:
        print("Échec de l'initialisation du client.")


if __name__ == "__main__":
    health_check()
