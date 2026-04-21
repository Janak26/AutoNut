import lancedb
from sentence_transformers import SentenceTransformer
import json
import os


DB_PATH = "./lancedb"
TABLE_NAME = "recepies"
DATA_PATH = "gptedencodedFullwithText.json"

EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5



print("Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL)



def load_data(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)



def create_table(data):
	print("Creating LanceDB table...")

	db = lancedb.connect(DB_PATH)

	# Prepare records with embeddings
	records = []
	for item in data:
		embedding = model.encode(item["text"]).tolist()

		item["embedding"] = embedding

		records.append(item)

	# Create table (overwrite if exists)
	table = db.create_table(TABLE_NAME, data=records, mode="overwrite")

	print(f" Stored {len(records)} chunks in LanceDB")
	return table



def load_table():
	db = lancedb.connect(DB_PATH)
	return db.open_table(TABLE_NAME)




def main():
	# Step 1: Load data
	data = load_data(DATA_PATH)

	# Step 2: Create table
	if not os.path.exists(DB_PATH):
		table = create_table(data)
	else:
		table = load_table()
	


if __name__ == "__main__":
	main()