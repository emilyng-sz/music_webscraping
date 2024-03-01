import requests
from bs4 import BeautifulSoup

# loop through pages of Looperman website to get songs of desired category in my own format
song_dictionary = {}

url = f"https://www.looperman.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

player_wrappers = soup.find_all('div', class_=lambda x: x and (x.startswith('player-wrapper') or x.startswith('tag-wrapper')))[:1]

for player_wrapper in player_wrappers:
    # Retrieve information within the div
    player_wrappers = soup.find_all('div', class_=lambda x: x and x.startswith('player-wrapper'))

for player_wrapper in player_wrappers:
    nested_divs = player_wrapper.find_all('div')
    print(nested_divs)