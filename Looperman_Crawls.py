import requests
from bs4 import BeautifulSoup

# loop through pages of Looperman website to get songs of desired category in my own format
song_dictionary = {}

url = f"https://www.looperman.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

player_wrappers = soup.find_all('div', class_=lambda x: x and (x.startswith('player-wrapper') or x.startswith('tag-wrapper')))[:1]

for div in player_wrappers:
    # Retrieve information within the div
    rel_link = div.get('rel')
    if rel_link:
        full_title = rel_link.split('/')[-1].split('.')[0] 
        title = '-'.join(full_title.split('-')[4:])
        # the titles will then start with "https://www.looperman.com/media/loops/2273068/looperman-l-2273068-0353864-" "
        song_dictionary[title] = {'download_link': rel_link}
        song_dictionary[title]["full_name"] = full_title