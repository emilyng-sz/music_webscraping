import requests
from bs4 import BeautifulSoup
import os

MIN_SONGS = 50
song_counter = 0
page_counter = 0

# loop through pages of Looperman website to get songs of desired category in my own format
song_dictionary = {}

while song_counter < MIN_SONGS:
    page_counter += 1 # update page counter
    url = f"https://www.looperman.com/loops?page={page_counter}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')


    # get detailed information of each song located in the tag divs

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
        title = '-'.join(title_tuple[:bpm_index-1]) # this assumes the title is followed by 'free', 'bpm' etc 
        if title not in song_dictionary:
            #print(f"Title {title} not found in dictionary")
            #continue
            song_dictionary[title] = {'download_link': None}
        song_dictionary[title]['url'] = href
        
        # get the tags

        ## get bpm
        bpm_divs = div.find_all('a', title = lambda  title: title and title.startswith("Find more loops at"))
        assert len(bpm_divs) == 1, f"multiple bpm values in {title}"
        bpm_text = bpm_divs[0].get_text()
        assert "bpm" in bpm_text, f"bpm not found in {title}"
        bpm = bpm_text.replace("bpm", "").strip()
        song_dictionary[title]['bpm'] = bpm

        ## get Genre
        genre_divs = div.find_all('a', title = lambda title: title and title.startswith("Genre"))
        genre_list = []
        for genre_div in genre_divs:
            genre = genre_div.get_text().replace("Loops", "").strip()
            genre_list.append(genre)

        if len(genre_divs) > 1:
            song_dictionary[title]['genre'] = genre_list
        else:
            song_dictionary[title]['genre'] = genre

        ## get Category
        category_divs = div.find_all('a', title = lambda title: title and title.startswith("Category"))
        category_list = []
        for category_div in category_divs:
            category = category_div.get_text().replace("Loops", "").strip()
            if category in desired_categories:
                category_list.append(category)

        if len(category_list) > 1:
            song_dictionary[title]['category'] = category_list
        elif len(category_list) == 1:  
            song_dictionary[title]['category'] = category_list[0]
        else: # remove the song to avoid errors later on
            to_remove.append(title)

        ## get key
        key_divs = div.find_all('a', title = lambda  title: title and "key" in title.lower())
        if len(key_divs) == 1:
            key_text = key_divs[0].get_text().split(":")[-1].strip()
        else:
            key_text = 'Unknown'
        song_dictionary[title]['key'] = key_text
    
    # get song, title and download link
    player_title_divs = soup.find_all('div', class_=lambda x: x and (x.startswith('player-wrapper') or x == "desc-wrapper")) # 25 for one page
    for div in player_title_divs:
        rel_link = div.get('rel')
        if rel_link:
            full_title = rel_link.split('/')[-1].split('.')[0].split('-')
            if 'bpm' in full_title[-1]:
                title = '-'.join(full_title[4:-2])
            else:
                title = '-'.join(full_title[4:])

            # the titles will then start with "https://www.looperman.com/media/loops/2273068/looperman-l-2273068-0353864-" "
            if title not in song_dictionary:
                print(f"Title {title} not found in dictionary")
                continue
            song_dictionary[title]['download_link'] = rel_link
            song_dictionary[title]["full_name"] = '-'.join(full_title)

            # update song_counter
            song_counter += 1

        if div.get('class')[0] == "desc-wrapper": # this will update the most recently parsed song with description
            text = div.get_text(strip=True).replace("Description : ", "")
            if title not in song_dictionary:
                print(f"Title {title} not found in dictionary")
                continue
            song_dictionary[title]['description'] = text if text else ''

    for title in to_remove:
        del song_dictionary[title]
        song_counter -= 1

print(song_dictionary)
print(song_dictionary.keys())

# function to create directory according to category
def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"directory {directory} created")


create_directory('Looperman_Loops')
json_dict = {}
for song in song_dictionary:
    print("song"   , song)
    category = song_dictionary[song]['category']
    category = category.replace(" ", "_") # use underscores
    create_directory(f'Looperman_Loops/{category}')

    # download song and write to file
    download_link = song_dictionary[song]['download_link']
    response = requests.get(download_link)
    with open(f'Looperman_Loops/{category}/{song}.wav', 'wb') as f:
        f.write(response.content)

# c) Create json structured dictionary with all the information (in the same loop)

    if category not in json_dict:
        json_dict[category] = {}

    full_title = song_dictionary[song]['full_name']
    song_info = {
        "bpm": song_dictionary[song]['bpm'],
        "genre": song_dictionary[song]['genre'],
        "key": song_dictionary[song]['key'],
        "description": song_dictionary[song]['description'],
        "url": song_dictionary[song]['url']
    }
    json_dict[category][full_title] = song_info


# Save the json dictionary to a json file
import json
with open('meta.json', 'w') as f:
    json.dump(json_dict, f, indent=4)

