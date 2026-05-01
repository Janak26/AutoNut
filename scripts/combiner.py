import queryLance
import reranker
import explain



def full_process():
	precision_ = "moderate"

	user_input = input("What would you like to have today? : ")
	dbResponse = queryLance.queryingLance(user_input)
	
	rerankedResponse = reranker.reranker_main(user_input, dbResponse, precision_)

	if len(rerankedResponse) == 0:
		return "No relevant Recipes found"
	
	available_choices = explain.display_choices(rerankedResponse)

	for choice in available_choices:
		print(choice)
	
	input_choice = int(input("Write the ID of your choice : "))

	print(input_choice)
	
	selected_recipe = next((item for item in available_choices if item.get("id") == input_choice), None)

	print("your selected recipe")
	print(selected_recipe)

	qna = explain.explain_recipe(selected_recipe)



if __name__ == "__main__":
	full_process()