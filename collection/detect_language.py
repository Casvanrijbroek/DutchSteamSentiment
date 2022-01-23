from collection.reviews_collector import get_json, write_json
from langdetect import detect, LangDetectException
import os


def separate_directory(reviews_dir, files_dir):
    filenames = os.listdir(f'{reviews_dir}/{files_dir}')

    for filename in filenames:
        if not os.path.exists(f'{reviews_dir}/ver_dutch/{filename}'):
            separate_dutch(f'{reviews_dir}/{files_dir}', filename, reviews_dir)


def separate_dutch(reviews_dir, reviews_file, output_dir):
    reviews = get_json(f'{reviews_dir}/{reviews_file}')

    dutch = []
    non_dutch = []

    for review in reviews:
        try:
            if len(review['review']) < 3:
                continue
            if detect(review['review']) == 'nl':
                dutch.append(review)
            else:
                non_dutch.append(review)
        except LangDetectException:
            pass

    write_json(dutch, f'{output_dir}/ver_dutch/{reviews_file}')
    write_json(non_dutch, f'{output_dir}/ver_non_dutch/{reviews_file}')


if __name__ == '__main__':
    separate_directory('../reviews', 'dutch')
