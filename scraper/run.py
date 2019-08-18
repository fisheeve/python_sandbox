import argparse
import requests
import lxml.html as lh
import scrapers


def args_parse():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='osu_scraper')
    parser.add_argument("-n", default=50, type=int,
                        help='number_of_rows(max=50)')
    parser.add_argument("--name", type=str, default="./osu_top50_scrapper")
    args = parser.parse_args()
    return args


scraper = scrapers.CSVScraper()


def main(args):
    if args.n <= 50:
        num_row = args.n
    else:
        num_row = 50
    url = 'https://osu.ppy.sh/rankings/osu/performance'
    page = requests.get(url)
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')

    col = scraper.column_maker(tr_elements)
    col[0] = ("Rank", [])
    col[1] = ("Username", [])
    df = scraper.df_maker(tr_elements, col, num_row)
    df = scraper.osu_df_maker(df, page, num_row)
    scraper.csv_maker(df, args.name)
    pass


if __name__ == '__main__':
    args = args_parse()
    main(args)
