import lancedb
from sentence_transformers import SentenceTransformer
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path


env_Path = Path('/home/linux/linux/ProjectsReal/chef') / '.env'
load_dotenv(dotenv_path = env_Path)

DB_PATH = os.getenv("LanceDB_Path")


TABLE_NAME = "recepies"

EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


query_parser_knowledge_base = """

You are an intelligent text summariser for a recipe recommendation system.

Your task is to convert a user's natural language into keywords

Extract or develop only the relevant keywords according to the text:

type of meal for example breakfast, lunch, dinner, snack, dessert, drink, full course (infer from time/context if not explicit)
time required (if mentioned or implied like quick, fast
dietary constraints for e.g., no eggs, no dairy, vegan, no onion, etc.
ingredients to include
ingredients to avoid
cuisine (e.g., Indian, Italian, Greek, etc.)
dish type (e.g., curry, soup, salad, rice, pasta, etc.)
nutrition e.g., high protein, lowcalorie, healthy, light)
difficulty for example easy, medium, hard

Please be aware of the context, do not add unnecessary and irrelevant keywords

Rules:
- Infer intelligently from context (e.g., "7pm" → dinner, "after gym" → high protein)
- Do NOT explain anything

The response should be between atleast 3 and maximum 8 keywords strictly in a single phrase
Please double check the response format
"""


print("Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)



def load_table():
	db = lancedb.connect(DB_PATH)
	return db.open_table(TABLE_NAME)



def search(table, query, TOP_K=5):

	query_embedding = model.encode(query).tolist()

	results = (
		table.search(query_embedding)
		.limit(TOP_K)
		.to_list()
	)

	return results


def haveRelevantFields(response):
	required_fields = ['id', 'recepie name', 'ingredients', 'directions', 'prep time', 'cook time', 'yield', 'per serving', 'vary it', 'tip', 'note', 'tags', 'prep time minutes', 'cook time minutes']
	response = {k : response[k] for k in required_fields}
	return response




def queryParser(client_query):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # fast + cheap + good for extraction
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": query_parser_knowledge_base
            },
            {
                "role": "user",
                "content": f"Develop keywords from this text. Text:\n{client_query}"
            }
        ]
    )

    result = response.choices[0].message.content
    return result




def queryingLance(query):
	table = load_table()
	query = queryParser(query)
	print(query)
	results = search(table, query, TOP_K)
	results = [haveRelevantFields(k) for k in results]
	return results




if __name__ == "__main__":
	userQuery = "i am hungry, want something to eat very quickly, but it should be rich in protien, maybe a good sandwich"
	searched = queryingLance(userQuery)
	for res in searched:
		print(res)
		print("-----")
