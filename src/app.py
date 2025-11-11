from fastapi import FastAPI
from pydantic import BaseModel
from .router import Router
from .llm import get_llm

app = FastAPI(title="Ticket Triage Agent")
router = Router.bootstrap()

class Ticket(BaseModel):
    summary: str
    description: str

@app.post("/triage")
def triage(t: Ticket):
    label, prob = router.predict(f"{t.summary}\n{t.description}")
    llm = get_llm()
    reply = llm.complete(
        f"Write a short, empathetic reply for a ticket routed to '{label}'. "
        f"Ask 2 clarifying questions and list next steps."
    )
    return {"queue": label, "confidence": prob, "reply": reply}
