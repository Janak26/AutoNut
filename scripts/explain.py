import ollama



def explain_recipe(recep):

	main_prompt = f"""You are a helpful vegetarian cooking assistant.

	You will be given a recipe. The user will ask questions about it.

	You can:
	- explain steps
	- simplify instructions
	- suggest substitutions
	- adjust quantities
	- estimate time
	- make it healthier or quicker

	Always base your answers ONLY on the given recipe.
	Be clear, concise, and conversational.

	Stick to the above recipe only, do not diverge a lot if asked for variations or substitutions
	Do not hesitate to say that it may not be possible to make the dish if major ingredients are not available with the user

	Strictly keep your answers short, with 1 to 3 sentences, unless asked for detailed explaination


	Recipe:
	{recep}
	"""


	messages = [
	{"role": "system", 
	 "content": main_prompt}]

	while True:
		user_input = input("You: ")

		if user_input == 'exit':
			break

		
		
		messages.append({"role": "user", "content": user_input})

		stream = ollama.chat(
			model="qwen3.5:9b",
			messages=messages,
			stream=True,
			think=False
		)

		print("Assistant:", end=" ", flush=True)

		full_reply = ""
		for chunk in stream:
			content = chunk["message"]["content"]
			print(content, end="", flush=True)
			full_reply += content

		print()

		messages.append({"role": "assistant", "content": full_reply})


def display_choices(recipes):
	to_display = []
	for a_recipe in recipes:
		item = {}
		item['id'] = a_recipe['id']
		item['recepie name'] = a_recipe['recepie name']
		item['ingredients'] = a_recipe['ingredients']
		item['prep time'] = a_recipe['prep time minutes']
		item['cook time'] = a_recipe['cook time minutes']
		to_display.append(item)
	return to_display



def explain_recipe_chat(recipe, user_input, history):
	main_prompt = f"""You are a helpful vegetarian cooking assistant.

	You will be given a recipe. The user will ask questions about it.

	You can:
	- explain steps
	- simplify instructions
	- suggest substitutions
	- adjust quantities
	- estimate time
	- make it healthier or quicker

	Always base your answers ONLY on the given recipe.
	Be clear, concise, and conversational.

	Stick to the above recipe only, do not diverge a lot if asked for variations or substitutions
	Do not hesitate to say that it may not be possible to make the dish if major ingredients are not available with the user

	Strictly keep your answers short, with 1 to 3 sentences, unless asked for detailed explaination


	Recipe:
	{recipe}
	"""


	messages = [
	{"role": "system", 
	 "content": main_prompt}]

	
	
	messages.append({"role": "user", "content": user_input})

	stream = ollama.chat(
		model="qwen3.5:2b",
		messages=messages,
		stream=False,
		think=False
	)

	reply = stream["message"]["content"]

	history.append({"role": "user", "content": user_input})
	history.append({"role": "assistant", "content": reply})

	return reply, history












if __name__ == "__main__":
	# user_query = "I'm in a hurry and need a fast dinner option that doesn't require a lot of prep work. I need to make it for myself and my wife, so for 2 people "
	recipeC = {'id': 808, 
			'recepie name': 'Hurry Up Hero', 
			'ingredients': [
					'1⁄2 piece whole-wheat pita pocket bread', 
				   '1⁄2 teaspoon yellow mustard', 
				   '1 slice pepper jack cheese or nondairy cheese', 
				   '3 thin slices green pepper', 
				   '3 slices cucumber', 
				   '2 thin slices onion', 
				   '2 slices tomato', 
				   '1⁄4 avocado, peeled, pitted, and sliced thin', 
				   '1⁄4 cup shredded lettuce'], 
			'directions': [
					'Open the pocket in the pita bread and spread the mustard inside the pocket.', 
					'Place the cheese, green pepper, cucumber, onion, tomato, avocado, and lettuce inside the pocket.'], 
			'prep time': '5 min', 
			'cook time': '0 min', 
			'yield': '1 serving', 
			'per serving': 'calories 285 (from fat 147); fat 16g (saturated 7g); cholesterol 30mg; sodium 347mg; carbohydrate 27g (dietary fiber 7g); protein 11g.', 
			'vary it': 'Use mayo if you don’t have mustard, or drizzle a little olive oil and vinegar over the filling. '
						'If you’re out of tomatoes, medium salsa works great as a substitute. '
						'In a pinch, you can use cooked asparagus spears or tiny broccoli florets if you’re avocado-less. '
						'And you can use spinach in place of the lettuce.', 
			'tip': '', 
			'note': '', 
			'tags': ['lunch', 'quick', 'vegetarian', 'healthy', 'snack', 'whole wheat', 'no cook', 'gluten']}
	explain_recipe(recipeC)
	# print(res)