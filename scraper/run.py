import argparse
import requests
import lxml.html as lh
import pandas as pd
from bs4 import BeautifulSoup


def args_parse():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='osu_scraper')
    parser.add_argument("-n", default=50, type=int,
                        help='number_of_rows(max=50)')
    parser.add_argument("--name", type=str, default="./osu_top50_scrapper")
    args = parser.parse_args()
    return args


def column_maker(data):
    # Create empty list
    col = []
    i = 0
    # For each row, store each first element (header) and an empty list
    for t in data[0]:
        i += 1
        name = t.text_content().replace('\n                    ', '')
        name = name.replace('\n                ', '')
        col.append((name, []))
    return col


def df_maker(elements, col, num_row):
    for j in range(1, num_row + 1):
        # j'th row
        row = elements[j]

        # i is the index of our column
        i = 0

        # Iterate through each element of the row
        for t in row.iterchildren():
            data = t.text_content()
            # Check if row is empty
            if i > 0:
                # Convert any numerical value to integers
                try:
                    data = float(data.replace(',', '.'))
                except:
                    pass
            # Append the data to the empty list of the i'th column
            col[i][1].append(data)
            # Increment i for the next column
            i += 1

    dictionary = {title: column for (title, column) in col}
    df = pd.DataFrame(dictionary)
    df = df.replace('\n                    ', value='', regex=True)
    return df


def osu_df_maker(df, page, num_row):
    soup = BeautifulSoup(page.content, "html.parser")

    names = soup.find_all(
        'a', class_="ranking-page-table__user-link-text js-usercard")
    names_list = []
    for name in names:
        names_list.append(name.get_text().split(sep='>')[-1][33:-29])
    df['Username'] = names_list[:num_row]

    countries = soup.find_all("span", class_="flag-country")
    countries_list = []
    for country in countries:
        countries_list.append(country.get('title'))
    df.insert(loc=1, column='Country', value=countries_list[:num_row])
    return df


def main(args):
    if args.n <= 50:
        num_row = args.n
    else:
        num_row = 50
    url = 'https://osu.ppy.sh/rankings/osu/performance'
    page = requests.get(url)
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')

    col = column_maker(tr_elements)
    col[0] = ("Rank", [])
    col[1] = ("Username", [])
    df = df_maker(tr_elements, col, num_row)
    df = osu_df_maker(df, page, num_row)
    df.to_csv(args.name)


if __name__ == '__main__':
    args = args_parse()
    main(args)
