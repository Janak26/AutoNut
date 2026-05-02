## AutoNut, an end-to-end intelligent recipe assistant that allows users to search, explore, and interact with vegetarian recipes using natural language.


https://github.com/user-attachments/assets/1c292d98-8b48-4630-bce0-f474de7a7645


### The system supports:
Smart recipe retrieval
Context-aware filtering
Interactive conversational assistance over recipes




## 🚀 Features
🔍 Natural language recipe search
🧠 Intelligent query understanding (time, diet, preferences)
🗂️ Structured recipe storage and retrieval
💬 Chat-based interaction with selected recipes
🎯 Context-aware responses (substitutions, simplifications, etc.)
⚡ Fast and lightweight (runs locally)



## 📊 Dataset

The dataset consists of ~900 vegetarian recipes collected from:

The Bold Vegetarian Chef by Ken Charney
Vegetarian Recipes Collection
Student's Vegetarian Cookbook for Dummies by Connie Sarros
Creative Vegetarian Cooking



## 🧹 Data Processing Pipeline
1. PDF → Text Extraction
Manual Restructuring of some recipe books
Extracted raw text from recipe books
Cleaned formatting artifacts
2. Text Cleaning
Normalized structure (ingredients, directions, etc.)
3. Structuring
Converted recipes into JSON format
Handled missing fields gracefully
4. Feature Engineering
Created:
text field (for semantic search)
normalized time fields
consistent schema


## 🗄️ Database (LanceDB)

Recipes are stored in LanceDB with:

Vector embeddings
Metadata fields (ingredients, cook time, etc.)



## 🔎 Query & Retrieval
Step 1: User Query
Example:
"I want something quick for dinner after gym"

Step 2: Query Processing using OpenAI API for intent extraction
Extract intent:
meal type → dinner
constraint → quick
nutrition → high protein

Step 3: Retrieval
Semantic search over embeddings
Top-K results fetched

Step 4: Filtering
Score and filter results based on relevance, groundedness, relatedness, and semantic match using OpenAI APIs



## 💬 Chat Capabilities

Once a recipe is selected, users can:

-Ask for simplification

-Get substitutions

-Adjust serving size

-Make recipes healthier or quicker

-Understand steps



## 🧠 Prompt Design

Key principles:

Grounded strictly in recipe
Short and concise responses (1–3 sentences)
Avoid hallucination
Respect constraints
