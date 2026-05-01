import json
import os
import pandas as pd
from openai import OpenAI
import re
from dotenv import load_dotenv
from pathlib import Path


env_Path = Path('/home/linux/linux/ProjectsReal/chef') / '.env'
load_dotenv(dotenv_path = env_Path)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


KNOWLEDGE_BASE = """
You are a recipe writer. you need to evaluate whether the recipe is related or not to what the user wants and provide scores.
This is a part of a RAG system evaluation and I want to evaluate the system performance and accuracy.

Relevance:
Ensure the recipe is concise and relevant to what the user wants
Give a score between 1 to 10 with 1 being least relevant and 10 being the most relevant.


Groundedness
Ensure the recipe is grounded in the user requirement.
Ensure the recipe does not contain "hallucinated" information outside the scope of the requirement.
to what extent does the generated response agree with the retrieved context. 
give a score between 1 to 10 with 1 being least grounded and 10 being the most grounded.


relatedness:
You goal is to identify recipes which completely unrelated to the user requirement
(2) If the recipe contains ANY words or semantic meaning related to the user requirement, consider them related
It is OK if the recipe has SOME information that is unrelated to the user requirement as long as (2) is met
give a score between 1 to 10 with 1 being least related and 10 being the most related.


semantic similarity:
rate semantic similarity between the user requirement and the recipe with 10 being high semantic match and 1 being the lowest semantic match

Required Response:

{    
	"relevance"; score,
	"groundedness": score,
	"relatedness": score,
	"semantic match"; score
}

the score should strictly be as mentioned.
The response should strictly contain the keys and format as mentioned.
Please double check the response


	Return JSON.
"""




def score_responses_openai(recipe, query):
	response = client.chat.completions.create(
		model="gpt-4.1-mini",  # fast + cheap + good for extraction
		temperature=0,
		messages=[
			{
				"role": "system",
				"content": KNOWLEDGE_BASE
			},
			{
				"role": "user",
				"content": f"Keyword:\n{query}  Recipe:\n{recipe}"
			}
		]
	)

	result = response.choices[0].message.content
	return result


def parse_chatgpt_json(response: str):
	cleaned = re.sub(r"```json|```", "", response).strip()
	return json.loads(cleaned)



def score_responses(responses_json, client_query):
	scored_responses_json = []
	for single_response in responses_json:
		# print(single_response)
		scores = score_responses_openai(single_response, client_query)
		scores = parse_chatgpt_json(scores)
		# print('---')
		# print(scores)
		# single_response.update(scores)
		single_response = single_response | scores
		scored_responses_json.append(single_response)
	return scored_responses_json



def add_match_filter(scored_responses_json):
	scored_responses_list = []
	for single_scored_response in scored_responses_json:
		relevance_score = single_scored_response['relevance']
		groundedness_score = single_scored_response['groundedness']
		relatedness_score = single_scored_response['relatedness']
		semantic_match_score = single_scored_response['semantic match']

		all_sum = relevance_score + groundedness_score + relatedness_score + semantic_match_score
		if all_sum >= 34:
			single_scored_response['match'] = 'Strong Match'
		elif 34 > all_sum >= 30:
			single_scored_response['match'] = 'Moderate Match'
		elif 30 > all_sum >= 25:
			single_scored_response['match'] = 'Low Match'
		else:
			single_scored_response['match'] = 'Not a match'
		scored_responses_list.append(single_scored_response)
	return scored_responses_list


def filter_relevant(all_responses, precision_req="moderate"):
	relevant = []
	for recep in all_responses:
		if precision_req == "high":
			if recep["match"] == "Strong Match":
				relevant.append(recep)
			else:
				pass
		elif precision_req == "moderate":
			if recep["match"] == "Strong Match":
				relevant.append(recep)
			elif recep["match"] == "Moderate Match":
				relevant.append(recep)
			else:
				pass
		elif precision_req == "low":
			if recep["match"] != "Not a match":
				relevant.append(recep)
			else:
				pass
	return relevant



def clear_scoring(filtered_json):
	only_recepie = []
	for relevant_record in filtered_json:
		required_fields = ['id', 'recepie name', 'ingredients', 'directions', 'prep time', 'cook time', 'yield', 'per serving', 'vary it', 'tip', 'note', 'tags', 'prep time minutes', 'cook time minutes']
		relevant_record = {k : relevant_record[k] for k in required_fields}
		only_recepie.append(relevant_record)
	return only_recepie



def reranker_main(user_query, lanceresponses, precision_):
	results = score_responses(lanceresponses, user_query)
	results = add_match_filter(results)
	results = filter_relevant(results, precision_)
	if len(results) > 0:
		results = clear_scoring(results)	
		return results
	else:
		return results



if __name__ == "__main__":
	# user_query = "I'm in a hurry and need a fast dinner option that doesn't require a lot of prep work "
	# user_query = "doremon pikachu raichu beyblade"
	user_query = "i want a pasta recipe with tomatoes"
	lanceresponses = [{'id': 487, 'recepie name': 'Quick, no-cook, stir in Sauce for Pasta', 'ingredients': ['6 fresh tomatoes and half a cup of water OR 1 tin of tomatoes', 'A good handful of basil (both stalks and leaves)', 'A handful of parsley', '2 sticks of celery, cut into chunks', 'Half a teaspoon of sea salt', 'Dash of soy sauce (optional)', '2 teaspoons cold pressed olive oil (leave this out if you want a fat free sauce)'], 'directions': ['Whizz all the ingredients up in a liquidiser or blender until fairly smooth.', 'Stir the sauce into your favourite pasta.', 'Serve very nice with wholewheat shells and a big salad.'], 'tags': ['no-cook', 'sauce', 'pasta', 'vegetarian', 'quick', 'healthy', 'Italian', 'easy'], 'prep time': '10 minutes', 'cook time': '0 minutes', 'yield': 'Enough sauce for 4 servings', 'cook time minutes': 0, 'prep time minutes': 0, 'per serving': 'Calories and nutrition vary depending on pasta used', 'note': '', 'tip': '', 'vary it': '', 'text': 'Quick, no-cook, stir in Sauce for Pasta ingredients =  6 fresh tomatoes and half a cup of water OR 1 tin of tomatoes A good handful of basil (both stalks and leaves) A handful of parsley 2 sticks of celery, cut into chunks Half a teaspoon of sea salt Dash of soy sauce (optional) 2 teaspoons cold pressed olive oil (leave this out if you want a fat free sauce) directions =  Whizz all the ingredients up in a liquidiser or blender until fairly smooth. Stir the sauce into your favourite pasta. Serve very nice with wholewheat shells and a big salad. tags =  no-cook sauce pasta vegetarian quick healthy Italian easy prep time =  10 minutes cook time =  0 minutes yield =  Enough sauce for 4 servings per serving =  Calories and nutrition vary depending on pasta used', '_distance': 1.1212303638458252}, {'id': 740, 'recepie name': 'Creamy Potato Salad', 'ingredients': ['6 medium potatoes', '1/2 cup eggless mayonnaise (try Nayonaise or Veganaise)', '4 Tbsp. yellow mustard', '2 Tbsp. distilled white vinegar', '1/2 onion, chopped', '1/2 cup chopped celery', 'Salt and pepper, to taste', 'Paprika (optional)'], 'directions': ['Cut the potatoes into cubes.', 'Cook the potatoes in boiling water for 20 minutes.', 'Drain and let cool completely.', 'In a large bowl, combine the potatoes with the remaining ingredients.', 'Sprinkle paprika on top, if desired.'], 'tags': ['salad', 'vegetarian', 'side dish', 'eggless', 'easy', 'quick', 'potato', 'American'], 'prep time': '10 minutes', 'cook time': '20 minutes', 'yield': '4 to 6 servings', 'cook time minutes': 20, 'prep time minutes': 20, 'per serving': '', 'note': '', 'tip': '', 'vary it': '', 'text': 'Creamy Potato Salad ingredients =  6 medium potatoes 1/2 cup eggless mayonnaise (try Nayonaise or Veganaise) 4 Tbsp. yellow mustard 2 Tbsp. distilled white vinegar 1/2 onion, chopped 1/2 cup chopped celery Salt and pepper, to taste Paprika (optional) directions =  Cut the potatoes into cubes. Cook the potatoes in boiling water for 20 minutes. Drain and let cool completely. In a large bowl, combine the potatoes with the remaining ingredients. Sprinkle paprika on top, if desired. tags =  salad vegetarian side dish eggless easy quick potato American prep time =  10 minutes cook time =  20 minutes yield =  4 to 6 servings', '_distance': 1.1615145206451416}, {'id': 830, 'recepie name': 'Melted Marvel', 'ingredients': ['1 whole-wheat english muffin, cut in half', '1 hard-boiled egg, sliced', '1 thin slice tomato', '1⁄4 teaspoon fat-free italian dressing', '1 thin slice onion, separated into rings', '2 thin slices dill pickle', '1 slice low-fat sharp cheddar cheese'], 'directions': ['Set the broiler rack one position down from the top, or about 6 to 7 inches from the heat source.', 'Preheat the broiler.', 'Toast the english muffin halves in a toaster.', 'Place one half of the english muffin on a baking pan or piece of foil and lay the egg slices on top.', 'Lay the tomato slices on top of the egg and drizzle the dressing over the tomato.', 'Lay the onion and pickle on top of the tomato and cover it all with a slice of cheese.', 'Broil the sandwich for 1 minute, or until the cheese melts, and then cover the sandwich with the remaining english muffin half.'], 'tags': ['lunch', 'quick', 'sandwich', 'healthy', 'low fat', 'vegetarian', 'american'], 'prep time': '4 min', 'cook time': '2 min', 'yield': '1 serving', 'cook time minutes': 2, 'prep time minutes': 2, 'per serving': 'calories 263 (from fat 76); fat 9g (saturated 3g); cholesterol 218mg; sodium 650mg; carbohydrate 29g (dietary fiber 3g); protein 18g.', 'note': '', 'tip': '', 'vary it': 'If you don’t have an english muffin, do you have a bagel, a loaf of french bread you can slice, or a ciabatta or sub roll you can cut in half? You can use any of these breads in place of the english muffin.', 'text': 'Melted Marvel ingredients =  1 whole-wheat english muffin, cut in half 1 hard-boiled egg, sliced 1 thin slice tomato 1⁄4 teaspoon fat-free italian dressing 1 thin slice onion, separated into rings 2 thin slices dill pickle 1 slice low-fat sharp cheddar cheese directions =  Set the broiler rack one position down from the top, or about 6 to 7 inches from the heat source. Preheat the broiler. Toast the english muffin halves in a toaster. Place one half of the english muffin on a baking pan or piece of foil and lay the egg slices on top. Lay the tomato slices on top of the egg and drizzle the dressing over the tomato. Lay the onion and pickle on top of the tomato and cover it all with a slice of cheese. Broil the sandwich for 1 minute, or until the cheese melts, and then cover the sandwich with the remaining english muffin half. tags =  lunch quick sandwich healthy low fat vegetarian american prep time =  4 min cook time =  2 min yield =  1 serving per serving =  calories 263 (from fat 76); fat 9g (saturated 3g); cholesterol 218mg; sodium 650mg; carbohydrate 29g (dietary fiber 3g); protein 18g. variation =  If you don’t have an english muffin, do you have a bagel, a loaf of french bread you can slice, or a ciabatta or sub roll you can cut in half? You can use any of these breads in place of the english muffin.', '_distance': 1.1741769313812256}, {'id': 808, 'recepie name': 'Hurry Up Hero', 'ingredients': ['1⁄2 piece whole-wheat pita pocket bread', '1⁄2 teaspoon yellow mustard', '1 slice pepper jack cheese or nondairy cheese', '3 thin slices green pepper', '3 slices cucumber', '2 thin slices onion', '2 slices tomato', '1⁄4 avocado, peeled, pitted, and sliced thin', '1⁄4 cup shredded lettuce'], 'directions': ['Open the pocket in the pita bread and spread the mustard inside the pocket.', 'Place the cheese, green pepper, cucumber, onion, tomato, avocado, and lettuce inside the pocket.'], 'tags': ['lunch', 'quick', 'vegetarian', 'healthy', 'snack', 'whole wheat', 'no cook', 'gluten'], 'prep time': '5 min', 'cook time': '0 min', 'yield': '1 serving', 'cook time minutes': 0, 'prep time minutes': 0, 'per serving': 'calories 285 (from fat 147); fat 16g (saturated 7g); cholesterol 30mg; sodium 347mg; carbohydrate 27g (dietary fiber 7g); protein 11g.', 'note': '', 'tip': '', 'vary it': 'Use mayo if you don’t have mustard, or drizzle a little olive oil and vinegar over the filling. If you’re out of tomatoes, medium salsa works great as a substitute. In a pinch, you can use cooked asparagus spears or tiny broccoli florets if you’re avocado-less. And you can use spinach in place of the lettuce.', 'text': 'Hurry Up Hero ingredients =  1⁄2 piece whole-wheat pita pocket bread 1⁄2 teaspoon yellow mustard 1 slice pepper jack cheese or nondairy cheese 3 thin slices green pepper 3 slices cucumber 2 thin slices onion 2 slices tomato 1⁄4 avocado, peeled, pitted, and sliced thin 1⁄4 cup shredded lettuce directions =  Open the pocket in the pita bread and spread the mustard inside the pocket. Place the cheese, green pepper, cucumber, onion, tomato, avocado, and lettuce inside the pocket. tags =  lunch quick vegetarian healthy snack whole wheat no cook gluten prep time =  5 min cook time =  0 min yield =  1 serving per serving =  calories 285 (from fat 147); fat 16g (saturated 7g); cholesterol 30mg; sodium 347mg; carbohydrate 27g (dietary fiber 7g); protein 11g. variation =  Use mayo if you don’t have mustard, or drizzle a little olive oil and vinegar over the filling. If you’re out of tomatoes, medium salsa works great as a substitute. In a pinch, you can use cooked asparagus spears or tiny broccoli florets if you’re avocado-less. And you can use spinach in place of the lettuce.', '_distance': 1.180655837059021}, {'id': 760, 'recepie name': 'Ran-Out-Of-Cereal Breakfast', 'ingredients': ['3 large caramel-corn rice cakes', '3⁄4 cup low-fat milk or soymilk'], 'directions': ['Crumble the rice cakes into a bowl and pour in the milk.'], 'tags': ['breakfast', 'vegetarian', 'quick', 'snack', 'low fat', 'easy', 'healthy'], 'prep time': '1 min', 'cook time': '0 min', 'yield': '1 serving', 'cook time minutes': 0, 'prep time minutes': 0, 'per serving': 'calories 228 (from fat 23); fat 3g (saturated 1g); cholesterol 7mg; sodium 178mg; carbohydrate 43g (dietary fiber 1g); protein 8g.', 'note': '', 'tip': 'Make this breakfast in a plastic bowl or large paper cup if you’re going to eat it on the run.', 'vary it': '', 'text': 'Ran-Out-Of-Cereal Breakfast ingredients =  3 large caramel-corn rice cakes 3⁄4 cup low-fat milk or soymilk directions =  Crumble the rice cakes into a bowl and pour in the milk. tags =  breakfast vegetarian quick snack low fat easy healthy prep time =  1 min cook time =  0 min yield =  1 serving per serving =  calories 228 (from fat 23); fat 3g (saturated 1g); cholesterol 7mg; sodium 178mg; carbohydrate 43g (dietary fiber 1g); protein 8g. tip =  Make this breakfast in a plastic bowl or large paper cup if you’re going to eat it on the run.', '_distance': 1.1830778121948242}, {'id': 674, 'recepie name': 'Easy Sweet & Sour Sauce', 'ingredients': ['1/4 cup pineapple juice', '1 1/2 tablespoons oil', '1 tablespoon brown sugar', '1 1/4 teaspoons soy sauce', '1/2 teaspoon pepper', '2 tablespoons milk vinegar'], 'directions': ['Combine all ingredients in small bowl.'], 'tags': ['Chinese Dishes', 'Sauces', 'Dipping Sauce', 'Vegetarian', 'Easy', 'Quick', 'Condiment'], 'prep time': '0:05', 'cook time': '0:00', 'yield': '6', 'cook time minutes': 0, 'prep time minutes': 0, 'per serving': '', 'note': '', 'tip': '', 'vary it': '', 'text': 'Easy Sweet & Sour Sauce ingredients =  1/4 cup pineapple juice 1 1/2 tablespoons oil 1 tablespoon brown sugar 1 1/4 teaspoons soy sauce 1/2 teaspoon pepper 2 tablespoons milk vinegar directions =  Combine all ingredients in small bowl. tags =  Chinese Dishes Sauces Dipping Sauce Vegetarian Easy Quick Condiment prep time =  0:05 cook time =  0:00', '_distance': 1.2055385112762451}, {'id': 854, 'recepie name': 'Mexican Medley', 'ingredients': ['4 cups water', '1 package top ramen oriental soup (without the enclosed seasoning packet)', '1 cup meatless beef-flavored crumbles', '1 cup salsa', '1 cup frozen corn', '2/3 cup canned black beans, rinsed and drained', '2 teaspoons taco seasoning mix', 'dash salt', 'dash black pepper', '1/3 cup shredded low-fat sharp cheddar cheese'], 'directions': ['Bring the water to a boil in a medium saucepan over high heat.', 'Add the noodles to the water and cook over medium-high heat for about 3 minutes, or until the noodles are tender.', 'Drain, and then return the noodles to the pan.', 'While the noodles cook, put the crumbles in a microwave-safe bowl or dish, cover with wax paper, and microwave for 40 seconds.', 'Stir the crumbles, salsa, corn, beans, seasoning mix, salt, and pepper into the noodles.', 'Cook over medium-high heat for 1 minute, or until all ingredients are blended and hot.', 'Spoon the pasta onto dinner dishes and sprinkle the cheese on top.'], 'tags': ['vegetarian', 'quick', 'easy', 'Mexican', 'dinner', 'meatless', 'spicy', 'healthy'], 'prep time': '3 min', 'cook time': '6 min', 'yield': '2 servings', 'cook time minutes': 6, 'prep time minutes': 6, 'per serving': 'calories 431 (from fat 84); fat 9g (saturated 3g); cholesterol 4mg; sodium 1,495mg; carbohydrate 60g (dietary fiber 9g); protein 28g.', 'note': '', 'tip': 'To convert this recipe to vegan, use nondairy cheddar cheese. A flavor packet is enclosed in the ramen noodles package. You don’t need it for this recipe, so put it aside to use in a stir-fry or when you make rice or soup.', 'vary it': 'You can determine how tangy and hot you want this meal by the type of salsa you add: mild, medium, or hot. Or you can use taco sauce or enchilada sauce instead of the salsa if that’s what you have left over in the fridge. If you don’t have corn in the freezer, substitute another frozen vegetable (lima beans, cut green beans, or peas), or chop up leftover veggies that are hiding in the refrigerator.', 'text': 'Mexican Medley ingredients =  4 cups water 1 package top ramen oriental soup (without the enclosed seasoning packet) 1 cup meatless beef-flavored crumbles 1 cup salsa 1 cup frozen corn 2/3 cup canned black beans, rinsed and drained 2 teaspoons taco seasoning mix dash salt dash black pepper 1/3 cup shredded low-fat sharp cheddar cheese directions =  Bring the water to a boil in a medium saucepan over high heat. Add the noodles to the water and cook over medium-high heat for about 3 minutes, or until the noodles are tender. Drain, and then return the noodles to the pan. While the noodles cook, put the crumbles in a microwave-safe bowl or dish, cover with wax paper, and microwave for 40 seconds. Stir the crumbles, salsa, corn, beans, seasoning mix, salt, and pepper into the noodles. Cook over medium-high heat for 1 minute, or until all ingredients are blended and hot. Spoon the pasta onto dinner dishes and sprinkle the cheese on top. tags =  vegetarian quick easy Mexican dinner meatless spicy healthy prep time =  3 min cook time =  6 min yield =  2 servings per serving =  calories 431 (from fat 84); fat 9g (saturated 3g); cholesterol 4mg; sodium 1,495mg; carbohydrate 60g (dietary fiber 9g); protein 28g. tip =  To convert this recipe to vegan, use nondairy cheddar cheese. A flavor packet is enclosed in the ramen noodles package. You don’t need it for this recipe, so put it aside to use in a stir-fry or when you make rice or soup. variation =  You can determine how tangy and hot you want this meal by the type of salsa you add: mild, medium, or hot. Or you can use taco sauce or enchilada sauce instead of the salsa if that’s what you have left over in the fridge. If you don’t have corn in the freezer, substitute another frozen vegetable (lima beans, cut green beans, or peas), or chop up leftover veggies that are hiding in the refrigerator.', '_distance': 1.2089110612869263}, {'id': 251, 'recepie name': 'vegetable fritters', 'ingredients': ['Your choice of vegetables (potatoes, aubergines, carrots, cauliflower, chillies, etc.)', '3/4 cup besan (chick pea flour)', '1/2 cup water', '1/2 tsp turmeric powder', '1 tsp chilli powder, or to taste', '1 tsp coriander seeds', '1 tsp pomegranate seeds', 'A pinch of soda bicarbonate', 'Salt to taste'], 'directions': ['Slice vegetables into thin slices (similar size pieces).', 'If using potatoes, boil in salted water until almost fork tender before slicing.', 'Mix batter ingredients into a smooth batter.', 'Dip vegetables into the mixture before deep-frying in hot oil.', 'Fry until golden brown.', 'Drain on absorbent paper towels and serve hot with a chutney dip.'], 'tags': ['snacks', 'vegetarian', 'fried', 'Indian cuisine', 'spicy', 'appetizer'], 'prep time': '20 minutes', 'cook time': '15 minutes', 'yield': 'Not specified', 'cook time minutes': 15, 'prep time minutes': 15, 'per serving': 'Not specified', 'note': '', 'tip': '', 'vary it': '', 'text': 'vegetable fritters ingredients =  Your choice of vegetables (potatoes, aubergines, carrots, cauliflower, chillies, etc.) 3/4 cup besan (chick pea flour) 1/2 cup water 1/2 tsp turmeric powder 1 tsp chilli powder, or to taste 1 tsp coriander seeds 1 tsp pomegranate seeds A pinch of soda bicarbonate Salt to taste directions =  Slice vegetables into thin slices (similar size pieces). If using potatoes, boil in salted water until almost fork tender before slicing. Mix batter ingredients into a smooth batter. Dip vegetables into the mixture before deep-frying in hot oil. Fry until golden brown. Drain on absorbent paper towels and serve hot with a chutney dip. tags =  snacks vegetarian fried Indian cuisine spicy appetizer prep time =  20 minutes cook time =  15 minutes yield =  Not specified per serving =  Not specified', '_distance': 1.2160556316375732}, {'id': 888, 'recepie name': 'Stewed Vegetable Dinner', 'ingredients': ['Nonstick cooking spray', '3 medium, unpeeled red potatoes, cut into wedges', '1 small onion, diced', '6 baby carrots, sliced thin', '1 stalk celery, sliced thin', '1 box (10 ounces) frozen chopped spinach, thawed', '1 can (8 ounces) french cut green beans plus liquid', '1 can (8 ounces) garbanzo beans, rinsed and drained', '1 tablespoon olive oil', '1 can (8 ounces) tomato sauce', '1/2 teaspoon minced garlic (fresh or from a jar)', '1/4 teaspoon cinnamon', '1 tablespoon dried parsley flakes', '1/4 teaspoon italian seasoning', '1/4 teaspoon salt', '1/4 teaspoon black pepper', '1 cup frozen peas'], 'directions': ['Spray the inside of a 2-quart slow cooker with nonstick spray.', 'Stir all the ingredients except the peas into the slow cooker, making sure the potato wedges are at the bottom because they take a little longer to cook than the other vegetables.', 'Cover the pot and cook for 8 hours on low.', 'Fifteen minutes before serving, stir in the peas.'], 'tags': ['vegetarian', 'dinner', 'slow cooker', 'healthy', 'low cholesterol', 'high fiber', 'gluten free', 'comfort food'], 'prep time': '8 min', 'cook time': '8 hr', 'yield': '2 servings', 'cook time minutes': 480, 'prep time minutes': 480, 'per serving': 'calories 516 (from fat 84); fat 9g (saturated 1g); cholesterol 0mg; sodium 1,553mg; carbohydrate 93g (dietary fiber 20g); protein 20g.', 'note': 'Eight hours of cooking time definitely exceeds the 30-minute limit of this chapter, but follow the reasoning here. This dinner takes only about 8 minutes to assemble, and the slow cooker does the rest, so technically, it’s not your time that’s being monopolized. Right?', 'tip': '', 'vary it': '', 'text': 'Stewed Vegetable Dinner ingredients =  Nonstick cooking spray 3 medium, unpeeled red potatoes, cut into wedges 1 small onion, diced 6 baby carrots, sliced thin 1 stalk celery, sliced thin 1 box (10 ounces) frozen chopped spinach, thawed 1 can (8 ounces) french cut green beans plus liquid 1 can (8 ounces) garbanzo beans, rinsed and drained 1 tablespoon olive oil 1 can (8 ounces) tomato sauce 1/2 teaspoon minced garlic (fresh or from a jar) 1/4 teaspoon cinnamon 1 tablespoon dried parsley flakes 1/4 teaspoon italian seasoning 1/4 teaspoon salt 1/4 teaspoon black pepper 1 cup frozen peas directions =  Spray the inside of a 2-quart slow cooker with nonstick spray. Stir all the ingredients except the peas into the slow cooker, making sure the potato wedges are at the bottom because they take a little longer to cook than the other vegetables. Cover the pot and cook for 8 hours on low. Fifteen minutes before serving, stir in the peas. tags =  vegetarian dinner slow cooker healthy low cholesterol high fiber gluten free comfort food prep time =  8 min cook time =  8 hr yield =  2 servings per serving =  calories 516 (from fat 84); fat 9g (saturated 1g); cholesterol 0mg; sodium 1,553mg; carbohydrate 93g (dietary fiber 20g); protein 20g. note =  Eight hours of cooking time definitely exceeds the 30-minute limit of this chapter, but follow the reasoning here. This dinner takes only about 8 minutes to assemble, and the slow cooker does the rest, so technically, it’s not your time that’s being monopolized. Right?', '_distance': 1.2305878400802612}, {'id': 775, 'recepie name': 'Quick Grits', 'ingredients': ['2⁄3 cup water', '1 teaspoon butter', '2 1⁄2 tablespoons quick grits', '2 1⁄2 tablespoons shredded low-fat cheddar cheese or nondairy cheese', 'dash salt', 'dash black pepper'], 'directions': ['Bring the water to a boil in a saucepan over high heat.', 'Add the butter.', 'Stir in the grits.', 'Reduce heat to medium, cover the pan, and cook, stirring occasionally, for 3 minutes, or until the grits are nearly done and most of the water has been absorbed.', 'Cook 1 minute longer if you like thicker grits.', 'Add the cheese, salt, and pepper and stir until the cheese is melted.'], 'tags': ['breakfast', 'quick', 'easy', 'comfort food', 'gluten-free', 'vegetarian', 'snack'], 'prep time': '1–2 min', 'cook time': '3 min', 'yield': '1 serving', 'cook time minutes': 3, 'prep time minutes': 3, 'per serving': 'calories 160 (from fat 48); fat 5g (saturated 3g); cholesterol 14mg; sodium 348mg; carbohydrate 21g (dietary fiber 0g); protein 7g.', 'note': '', 'tip': '', 'vary it': '', 'text': 'Quick Grits ingredients =  2⁄3 cup water 1 teaspoon butter 2 1⁄2 tablespoons quick grits 2 1⁄2 tablespoons shredded low-fat cheddar cheese or nondairy cheese dash salt dash black pepper directions =  Bring the water to a boil in a saucepan over high heat. Add the butter. Stir in the grits. Reduce heat to medium, cover the pan, and cook, stirring occasionally, for 3 minutes, or until the grits are nearly done and most of the water has been absorbed. Cook 1 minute longer if you like thicker grits. Add the cheese, salt, and pepper and stir until the cheese is melted. tags =  breakfast quick easy comfort food gluten-free vegetarian snack prep time =  1–2 min cook time =  3 min yield =  1 serving per serving =  calories 160 (from fat 48); fat 5g (saturated 3g); cholesterol 14mg; sodium 348mg; carbohydrate 21g (dietary fiber 0g); protein 7g.', '_distance': 1.2310346364974976}]
	precision_ = "high"
	print(len(lanceresponses))
	reranked_results = reranker_main(user_query, lanceresponses, precision_)
	print(reranked_results)
	print(len(reranked_results))