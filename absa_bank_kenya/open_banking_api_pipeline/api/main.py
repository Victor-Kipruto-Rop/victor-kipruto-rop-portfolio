from fastapi import FastAPI, Depends
from .account_client import AbsaAccountClient
from .oauth2_handler import AbsaOAuth2Handler
import os

app = FastAPI(title="Absa Open Banking Integration")

def get_account_client():
    handler = AbsaOAuth2Handler(
        os.getenv("ABSA_CONSUMER_KEY"), 
        os.getenv("ABSA_CONSUMER_SECRET")
    )
    return AbsaAccountClient(handler)

@app.get("/")
def read_root():
    return {"status": "operational", "message": "Absa Open Banking API Integration is running"}

@app.get("/accounts")
def get_accounts(client: AbsaAccountClient = Depends(get_account_client)):
    return client.get_accounts()

@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: str, client: AbsaAccountClient = Depends(get_account_client)):
    return client.get_transactions(account_id)
