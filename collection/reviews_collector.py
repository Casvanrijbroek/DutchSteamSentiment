import json
import os
from urllib import parse

import requests


def games_file_to_reviews(games_file, reviews_directory, overwrite=False, language='dutch'):
    games = get_json(games_file)

    for title, game_id in games.items():
        if overwrite or not os.path.exists(f'{reviews_directory}/{title.replace(" ", "_").replace(":", "")}.json'):
            get_all_language_reviews(f'{reviews_directory}/{title.replace(" ", "_").replace(":", "")}.json',
                                     game_id,
                                     overwrite=overwrite,
                                     language=language)


def get_all_language_reviews(review_path, game_id, language='dutch', overwrite=False):
    if os.path.exists(review_path) and not overwrite:
        raise RuntimeError('Attempt to overwrite existing reviews path, set overwrite=True if intended')

    reviews = []
    cursor = parse.quote('*')
    seen_cursors = set()
    sentinel = True

    while sentinel:
        response = requests.get(f'https://store.steampowered.com/appreviews/{game_id}'
                                f'?json=1&num_per_page=100&day_range=10000&filter=recent&language={language}&cursor={cursor}')

        if response.status_code == 200:
            content = response.json()
            cursor = parse.quote(content['cursor'])

            if cursor in seen_cursors:
                sentinel = False
            else:
                new_reviews = content['reviews']
                reviews.extend(new_reviews)

                if len(new_reviews) == 0:
                    sentinel = False

    write_json(reviews, review_path)


def dutch_to_english(reviews_dir, dutch_dir, language='english', overwrite=False):
    games = get_json('games.json')

    for title, game_id in games.items():
        dutch_reviews_len = len(get_json(f'{reviews_dir}/{dutch_dir}/{title.replace(" ", "_").replace(":", "")}.json'))

        get_n_reviews(f'{reviews_dir}/english/{title.replace(" ", "_").replace(":", "")}.json',
                      game_id,
                      dutch_reviews_len,
                      language=language,
                      overwrite=overwrite)


def get_n_reviews(review_path, game_id, n, language='english', overwrite=False):
    if os.path.exists(review_path) and not overwrite:
        raise RuntimeError('Attempt to overwrite existing reviews path, set overwrite=True if intended')

    reviews = []
    cursor = parse.quote('*')
    seen_cursors = set()
    sentinel = True

    while sentinel:
        response = requests.get(f'https://store.steampowered.com/appreviews/{game_id}'
                                f'?json=1&num_per_page=100&day_range=10000&filter=recent&language={language}&cursor={cursor}')

        if response.status_code == 200:
            content = response.json()
            cursor = parse.quote(content['cursor'])

            if cursor in seen_cursors:
                sentinel = False
            else:
                new_reviews = content['reviews']

                if n < len(new_reviews):
                    new_reviews = new_reviews[:n]
                n = n - len(new_reviews)
                if n == 0:
                    sentinel = False

                reviews.extend(new_reviews)

                if len(new_reviews) == 0:
                    sentinel = False

    write_json(reviews, review_path)


def get_json(path):
    with open(path, 'r') as input_handle:
        content = json.load(input_handle)

    return content


def write_json(obj, path):
    with open(path, 'w') as output_handle:
        json.dump(obj, output_handle)


if __name__ == '__main__':
    # games_file_to_reviews('games.json', '../reviews/dutch')
    dutch_to_english('../reviews', 'ver_dutch')
