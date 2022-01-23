import pandas as pd
import matplotlib.pyplot as plt
from reviews_collector import get_json
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score


def main():
    categories = get_json('categories.json')
    dutch = pd.read_csv('dutch.csv')
    english = pd.read_csv('english.csv')

    dutch = add_prediction_row(dutch)
    english = add_prediction_row(english)
    dutch_results = []
    english_results = []

    for category, titles in categories.items():
        dutch_results.append(category_to_percentage(dutch, titles))
        english_results.append(category_to_percentage(english, titles))

    # difference_results = [abs(di - ei) for di, ei in zip(dutch_results, english_results)]
    non_abs_differences = [di - ei for di, ei in zip(dutch_results, english_results)]
    category_names = categories.keys()
    category_names = [x for _, x in sorted(zip(non_abs_differences, category_names), reverse=True)]
    english_results = [x for _, x in sorted(zip(non_abs_differences, english_results), reverse=True)]
    dutch_results = [x for _, x in sorted(zip(non_abs_differences, dutch_results), reverse=True)]
    # category_names_difference = [x for _, x in sorted(zip(non_abs_differences, category_names), reverse=True)]
    non_abs_differences = sorted(non_abs_differences, reverse=True)

    plot_results(category_names, dutch_results, english_results)
    plot_difference(category_names, non_abs_differences)


def plot_results(labels, dutch, english):
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(x - width / 2, dutch, width, label='Dutch', color='#e68a00')
    ax.bar(x + width / 2, english, width, label='English', color='#005ce6')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('% positive')
    ax.set_title('Percentage positive sentiment on games per category by language preference', fontsize=10)
    ax.set_xticks(x, labels)
    ax.legend()

    plt.xticks(rotation=45)
    fig.tight_layout()

    plt.show()


def plot_difference(labels, difference):
    positions = list(range(len(labels)))
    plt.bar(positions, difference, color='#e68a00')

    plt.ylabel('difference in %')
    plt.xticks(positions, labels, rotation=45)
    plt.axhline(y=0, color='black', linestyle='-')
    plt.title('Difference of Dutch sentiment on game categories compared to English', fontsize=11)
    plt.tight_layout()

    plt.show()


def category_to_percentage(df, titles):
    positive = 0
    negative = 0

    for _, row in df.iterrows():
        if row['Game title'] in titles:
            if row['prediction']:
                positive += 1
            else:
                negative += 1

    return 100 / (positive + negative) * positive


def add_prediction_row(df):
    df['prediction'] = df.apply(lambda row: row['positive prediction'] > row['negative prediction'], axis=1)

    return df


def label_reviews(n, df_file):
    df = pd.read_csv(df_file)

    reviews = df.sample(n)
    predictions = []
    labels = []
    label = None

    for _, review in reviews.iterrows():
        print(1 if review['positive prediction'] > review['negative prediction'] else 0)
        print(review['Review text'])
        sentinel = True
        while sentinel:
            label = int(input('label: '))
            if label == 0 or label == 1:
                sentinel = False
        print('-' * 50)

        predictions.append(1 if review['positive prediction'] > review['negative prediction'] else 0)
        labels.append(label)

    print(f'precision: {precision_score(labels, predictions)}')
    print(f'recall: {recall_score(labels, predictions)}')
    print(f'f-measure: {f1_score(labels, predictions)}')


if __name__ == '__main__':
    label_reviews(50, 'english.csv')
