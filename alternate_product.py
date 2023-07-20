import requests
from bs4 import BeautifulSoup
import nltk
from difflib import get_close_matches

# Download the NLTK stopwords
nltk.download('stopwords')

# Define the URL format for the search results page
search_url = "https://www.amazon.com/s?k={}"

# Function to extract the product description from a given Amazon product page link
def get_product_description(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    description = soup.find("div", {"id": "productDescription"})
    if description:
        return description.get_text()
    else:
        return ""

# Get the user input for the product
product_name = "iphone"

# Search for the product on Amazon and get the HTML response
response = requests.get(search_url.format(product_name))

# Parse the HTML response using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Find all the product titles and links on the search results page
product_titles = [title.get_text() for title in soup.find_all("span", {"class": "a-size-medium a-color-base a-text-normal"})]
product_links = [link.get("href") for link in soup.find_all("a", {"class": "a-link-normal a-text-normal"})]

# Combine the product titles and links into a list of tuples
product_data = list(zip(product_titles, product_links))

# Check if the user input matches any of the product titles exactly
exact_match = False
for title, link in product_data:
    if product_name.lower() == title.lower():
        print("Exact match found: {}".format(title))
        exact_match = True
        break

if not exact_match:
    # Tokenize the user input and remove stopwords
    stop_words = set(nltk.corpus.stopwords.words('english'))
    tokens = [token.lower() for token in nltk.word_tokenize(product_name) if token.lower() not in stop_words]
    
    # Find the closest matches between the tokenized input and the product titles
    closest_matches = get_close_matches(' '.join(tokens), product_titles, n=5, cutoff=0.7)
    
    if closest_matches:
        # Print the closest matches
        print("No exact match found. Did you mean one of these?")
        for match in closest_matches:
            print("- {}".format(match))
        
        # Prompt the user to select one of the closest matches
        selection = input("Enter a number to select a product (or enter 'n' to exit): ")
        if selection.isdigit() and int(selection) <= len(closest_matches):
            selected_product = closest_matches[int(selection) - 1]
            selected_product_link = product_data[product_titles.index(selected_product)][1]
            selected_product_description = get_product_description(selected_product_link)
            print("Selected product: {}".format(selected_product))
            print("Product description: {}".format(selected_product_description))
        else:
            print("Exiting...")
    else:
        print("No matches found. Please try again with a different product name.")
