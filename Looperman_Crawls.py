import requests
from bs4 import BeautifulSoup
import os

MIN_SONGS = 200
song_counter = 0
page_counter = 0

# function to create directory according to category
def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"directory {directory} created")


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

    tag_divs = soup.find_all('div', class_=lambda x: x and x.startswith('tag'))
    desired_categories = 'Bass/Bass Guitar/Bass Synth/Bass Wobble/Drum/Flute/Guitar Acoustic/Guitar Electric/Harp/Percussion/Piano/Scratch/Strings/Synth/Violin'.split('/')
    to_remove = [] # store titles that do not belong in the category

for div in tag_divs:
    # Find all <a> elements within the current <div> that have href containing the title text
    links = div.find_all('a', href=lambda href: href and href.startswith('https://www.looperman.com/loops/detail/'))
    assert len(links) == 1, f"multiple titles in {div}"

    ## get same format as downloaded text
    href = links[0].get('href')  # Get the value of the href attribute
    title_tuple = href.split('/')[-1].split('-')
    bpm_index = next((i for i, x in enumerate(title_tuple) if 'bpm' in x), None)
    title_tuple = title_tuple[:bpm_index-1]
    title = '-'.join(title_tuple) # this assumes the title is followed by 'free', 'bpm' etc 