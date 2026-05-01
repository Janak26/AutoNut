import streamlit as st
import requests
import time

st.set_page_config(page_title="Auto Nut", layout="wide")

# ---------- STATE INIT ----------
if "selected_recipe" not in st.session_state:
	st.session_state.selected_recipe = None

if "chat_history" not in st.session_state:
	st.session_state.chat_history = []

if "query_input" not in st.session_state:
	st.session_state.query_input = ""

if "results" not in st.session_state:
	st.session_state.results = []

if "reset_query" not in st.session_state:
	st.session_state.reset_query = False


# ---------- RESET HANDLER ----------
if st.session_state.reset_query:
	st.session_state.query_input = ""
	st.session_state.reset_query = False


# ---------- GLOBAL STYLE ----------
st.markdown("""
<style>
.main {
	background-color: #f5f7fb;
}

.header {
	font-size: 32px;
	font-weight: 700;
	margin-bottom: 10px;
}

.search-box {
	background: white;
	padding: 15px;
	border-radius: 12px;
	box-shadow: 0 2px 8px rgba(0,0,0,0.05);
	margin-bottom: 20px;
}

.card {
	background: white;
	padding: 16px;
	border-radius: 12px;
	box-shadow: 0 2px 6px rgba(0,0,0,0.06);
	transition: 0.2s;
}
.card:hover {
	box-shadow: 0 4px 14px rgba(0,0,0,0.12);
	transform: translateY(-2px);
}

.big-card {
	background: white;
	padding: 24px;
	border-radius: 14px;
	box-shadow: 0 4px 18px rgba(0,0,0,0.08);
	margin-bottom: 20px;
}

.section-title {
	font-size: 22px;
	font-weight: 600;
	margin: 20px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.markdown('<div class="header">🍳 AutoNut Chef AI Assistant</div>', unsafe_allow_html=True)


# ---------- SEARCH ----------
with st.container():
	st.markdown('<div class="search-box">', unsafe_allow_html=True)

	with st.form("search_form"):
		user_input = st.text_input(
			"How do you feel, and what would you like to eat?",
			key="query_input",
			disabled=st.session_state.selected_recipe is not None
		)
		submitted = st.form_submit_button(
			"Search",
			disabled=st.session_state.selected_recipe is not None
		)

		if submitted and user_input.strip():
			response = requests.post(
				"http://localhost:8000/echo",
				json={"text": user_input}
			)
			data = response.json()

			# ✅ Ensure results is always a list
			results = data.get("message", [])
			if not isinstance(results, list):
				results = []

			st.session_state.results = results

	st.markdown('</div>', unsafe_allow_html=True)


# ---------- RESULTS ----------
if st.session_state.selected_recipe is None:


	cols = st.columns(3)

	if not st.session_state.results:
		st.info("Explore creative cuisine by making a search")

	else:
		
		for i, item in enumerate(st.session_state.results):

			# ✅ Skip invalid entries
			if not isinstance(item, dict):
				continue

			with cols[i % 3]:

				st.markdown(f"### {item.get('recepie name','')}")

				st.markdown("**Ingredients:**")
				ingredients = item.get("ingredients", [])

				if isinstance(ingredients, list):
					for ing in ingredients:
						st.markdown(f"- {ing}")
				else:
					st.write(ingredients)

				if st.button("View Recipe", key=f"select_{i}"):
					st.session_state.selected_recipe = item
					st.session_state.chat_history = []


# ---------- DETAIL + CHAT ----------
else:
	recipe = st.session_state.selected_recipe

	# ✅ Safety check
	if not isinstance(recipe, dict):
		st.error("Invalid recipe format received.")
		st.write(recipe)
		st.stop()

	# ---------- RECIPE ----------
	with st.container():
		st.markdown('<div class="big-card">', unsafe_allow_html=True)

		st.markdown(f"## {recipe.get('recepie name','')}")

		# Ingredients
		st.markdown("**Ingredients:**")
		ingredients = recipe.get("ingredients", [])

		if isinstance(ingredients, list):
			for ing in ingredients:
				st.markdown(f"- {ing}")
		else:
			st.write(ingredients)

		# Directions
		st.markdown("**Directions:**")
		directions = recipe.get("directions", [])

		if isinstance(directions, list):
			for i, step in enumerate(directions, 1):
				st.markdown(f"{i}. {step}")
		else:
			st.write(directions)

		# Times
		st.markdown(f"**Prep Time:** {recipe.get('prep time','')}")
		st.markdown(f"**Cook Time:** {recipe.get('cook time','')}")
		
		st.markdown(f"**Note:** {recipe.get('note','')}")
		st.markdown(f"**Tip:** {recipe.get('tip','')}")
		st.markdown(f"**Variations:** {recipe.get('vary it','')}")
		st.markdown(f"**Per Serving:** {recipe.get('per serving','')}")
		st.markdown(f"**Yield:** {recipe.get('yield','')}")

		st.markdown('</div>', unsafe_allow_html=True)

	if st.button("⬅ Back to results"):
		st.session_state.selected_recipe = None
		st.session_state.chat_history = []

	# ---------- CHAT ----------
	st.markdown('<div class="section-title">💬 Ask Chef AI</div>', unsafe_allow_html=True)

	for msg in st.session_state.chat_history:
		st.chat_message(msg["role"]).write(msg["content"])

	user_msg = st.chat_input("Ask something about this recipe... or if you have any questions")

	if user_msg:
		st.chat_message("user").write(user_msg)

		if user_msg.strip().lower() == "exit":
			st.session_state.selected_recipe = None
			st.session_state.chat_history = []
			st.session_state.results = []

			st.session_state.reset_query = True
			st.rerun()
			

		response = requests.post(
			"http://localhost:8000/chat",
			json={
				"recipe": recipe,
				"message": user_msg,
				"history": st.session_state.chat_history
			}
		).json()

		st.session_state.chat_history = response["history"]
		st.chat_message("assistant").write(response["reply"])