import argparse


parser = argparse.ArgumentParser(description="Scraper configuration")
parser.add_argument('--slave', dest='slave', action='store_true')
parser.add_argument('--starting-url', dest='url', help='Override url scraper will start from')
parser.add_argument('--concurrent-crawlers', dest='concurrent', type=int,
                    help='Max number of concurrent crawlers')

args = parser.parse_args()
