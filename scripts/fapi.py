from fastapi import FastAPI
from pydantic import BaseModel
import queryLance
import reranker
import explain
from logger import get_logger


logger = get_logger(__name__)


app = FastAPI()

class InputData(BaseModel):
	text: str

class ChatRequest(BaseModel):
	recipe: dict
	message: str
	history: list



def logFirstSearch(query, results, filteresresults):
	dbids = [k['id'] for k in results]
	if len(filteresresults) > 0:
		reraIds = [k['id'] for k in filteresresults]
	else:
		reraIds = []
	logger.info("user search: %s | ids: %s | reranked: %s", query, dbids, reraIds)



def logChat(recipe_id, message_from, chat_history):
	logger.info("recipe id: %s | %s: %s", recipe_id, message_from, chat_history)





@app.post("/echo")
def echo(user_input: InputData):
	dbResponse = queryLance.queryingLance(user_input)
	rerankedResponse = reranker.reranker_main(user_input, dbResponse, "moderate")

	logFirstSearch(user_input, dbResponse, rerankedResponse)

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

	
	logChat(req.recipe['id'], "user", req.message)
	logChat(req.recipe['id'], "system", reply)


	return {
		"reply": reply,
		"history": history
	}