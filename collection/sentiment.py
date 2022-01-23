import os

from transformers import RobertaTokenizer, RobertaForSequenceClassification
from reviews_collector import get_json
import pandas as pd


def main():
    tokenizer = RobertaTokenizer.from_pretrained('pdelobelle/robBERT-dutch-books')
    model = RobertaForSequenceClassification.from_pretrained('pdelobelle/robBERT-dutch-books')

    reviews = get_json('../reviews/ver_dutch/The_binding_of_Isaac_Rebirth.json')

    for review in reviews:
        if len(review['review'].split(' ')) > 5:
            print(review['review'])
            prediction = model(tokenizer(review['review'],
                                         return_tensors='pt',
                                         truncation=True,
                                         max_length=512)['input_ids'])
            print(prediction)
            print('positief' if prediction.logits[0][1] > prediction.logits[0][0] else 'negatief')


def make_prediction(text):
    tokenizer = RobertaTokenizer.from_pretrained('pdelobelle/robBERT-dutch-books')
    model = RobertaForSequenceClassification.from_pretrained('pdelobelle/robBERT-dutch-books')

    prediction = model(tokenizer(text, return_tensors='pt')['input_ids'])
    print('positief' if prediction.logits[0][1] > prediction.logits[0][0] else 'negatief')


def collect_sentiment_from_reviews(reviews_dir, output_file='dutch.csv', pretrained='pdelobelle/robBERT-dutch-books'):
    """
    'pdelobelle/robBERT-dutch-books' for Dutch
    'siebert/sentiment-roberta-large-english' for English

    :param reviews_dir: directory where the reviews are stored
    :param output_file: name of the output file
    :param pretrained: huggingface model to use
    """
    tokenizer = RobertaTokenizer.from_pretrained(pretrained)
    model = RobertaForSequenceClassification.from_pretrained(pretrained)

    games = get_json('games.json')
    data = []

    for game in games.keys():
        print(f'Processing {game}')

        reviews = get_json(f'{reviews_dir}/{game.replace(" ", "_").replace(":", "")}.json')

        for review in progressbar(reviews, prefix='Progress:', suffix='Complete', length=50):
            if len(review['review'].split(' ')) > 5:
                prediction = model(tokenizer(review['review'],
                                             return_tensors='pt',
                                             truncation=True,
                                             max_length=512)['input_ids'])

                neg, pos = prediction.logits.detach().numpy()[0][0], prediction.logits.detach().numpy()[0][1]

                data.append([game, review['review'], neg, pos])

    df = pd.DataFrame(data, columns=['Game title', 'Review text', 'negative prediction', 'positive prediction'])
    df.to_csv(output_file, encoding='utf-8', index=False)


def progressbar(iterable, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd=''):
    """
    Credit for this function goes to Diogo from the Stackoverflow community

    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def print_progressbar (iteration):
        try:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filled_length = int(length * iteration // total)
            bar = fill * filled_length + '-' * (length - filled_length)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        except ZeroDivisionError:
            pass

    # Initial Call
    print_progressbar(0)
    # Update Progress Bar
    for i, item_ in enumerate(iterable):
        yield item_
        print_progressbar(i + 1)
    # Print New Line on Complete
    print()


if __name__ == '__main__':
    collect_sentiment_from_reviews('../reviews/english', output_file='english.csv', pretrained='siebert/sentiment-roberta-large-english')
