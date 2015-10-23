import argparse


parser = argparse.ArgumentParser(description="Scraper configuration")
parser.add_argument('--slave', dest='slave', action='store_true')
parser.add_argument('--starting-url', dest='url', help='Override url scraper will start from')
parser.add_argument('--concurrent-crawlers', dest='concurrent', type=int,
                    help='Max number of concurrent crawlers')
parser.add_argument('--clean-redis', dest='clear', help='Before starting crawler clear redis db',
                    action='store_true')

args = parser.parse_args()
