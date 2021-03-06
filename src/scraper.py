import csv
import os

import requests
from bs4 import BeautifulSoup

DATA_DIR = 'data'
DELIMITER = ';'


def parse_html(url):
    body = requests.get(url).text
    return BeautifulSoup(body, 'html.parser')


def get_url(year, page, results_per_page, sex, age_class):
    return f'https://hannover.r.mikatiming.de/{year}/?page={page}&event=HM&num_results={results_per_page}&pid=list&search[sex]={sex}&search[age_class]={age_class}'


def get_csv(year, sex, age_class='%', results_per_page=100) -> str:
    filename = f'{year}_{sex}_{age_class}.csv'
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        page = 1
        url = get_url(year, page, results_per_page, sex, age_class)

        document = parse_html(url)
        n = int(document.select_one(
            'li.hidden-xs:nth-child(5) > a:nth-child(1)').text)

        with open(filepath, 'w') as file:
            csv_writer = csv.writer(file, delimiter=DELIMITER)
            for i in range(1, n + 1):
                print(get_url(year, i, results_per_page, sex, age_class))
                first = document.select(
                    'li.list-group-item > div.list-field-wrap > div.row')
                second = document.select(
                    'li.list-group-item > div.list-field-wrap > div.pull-left > div.row')
                third = document.select(
                    'li.list-group-item > div.list-field-wrap > div.pull-right > div.row')
                for j, row in enumerate(zip(first, second, third)):
                    # skip header line if not first line
                    if i != 1 and j == 0:
                        continue
                    line = []
                    for block in row:
                        for field in block.select('.list-field'):
                            labels = list(field.strings)
                            if len(labels) == 2:
                                line.append(labels[1])
                            if len(labels) == 1:
                                line.append(labels[0])
                    csv_writer.writerow(line)
                    print(line)
                if i != n:
                    document = parse_html(
                        get_url(year, i + 1, results_per_page, sex, age_class))
    return filepath


if __name__ == '__main__':
    get_csv(2018, 'W')
