from fastapi import FastAPI
from pydantic import BaseModel
import queryLance
import reranker
import explain


app = FastAPI()

class InputData(BaseModel):
	text: str

class ChatRequest(BaseModel):
    recipe: dict
    message: str
    history: list


@app.post("/echo")
def echo(user_input: InputData):
	dbResponse = queryLance.queryingLance(user_input)
	rerankedResponse = reranker.reranker_main(user_input, dbResponse, "moderate")

	if len(rerankedResponse) == 0:
		return {"message": None}
	

	return {"message": rerankedResponse}

@app.post("/chat")
def chat(req: ChatRequest):

    reply, history = explain.explain_recipe_chat(
        recipe=req.recipe,
        user_input=req.message,
        history=req.history
    )

    return {
        "reply": reply,
        "history": history
    }