import requests
from pprint import pprint
from bs4 import BeautifulSoup
import urllib.request
import argparse

def main(keyword):
    if keyword:
        URL = f"https://baike.baidu.com/item/{keyword}"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        meta_tag = soup.find('meta', attrs={'name': 'image'})
        if meta_tag:
            content = meta_tag.get('content')
            if content:
                base_url = content.split('?')[0]
                print(base_url)
                save_as = f'images/{keyword}.webp'
                urllib.request.urlretrieve(base_url, save_as)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("keyword")
    parser.add_argument('-k', '--keyword', help="百度百科关键词")
    args = parser.parse_args()

    main(args.keyword)
