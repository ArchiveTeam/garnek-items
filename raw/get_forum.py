import multiprocessing
import os
import re
import string
import typing

from get_users import download_page

URL = 'https://www.garnek.pl/0/fotofora/'
DIR = 'forum'


def get_forum_page(letter: str, num: int) -> typing.Set[str]:
    response = download_page(
        '{}?ch={}&p={}'.format(URL, letter, num),
        os.path.join(DIR, 'char_{}_page_{}.html'.format(letter, num))
    )
    results = set(re.findall('<a href="/forum/([^"]+)">', response))
    print(letter, num, len(results))
    return results
    
    
def get_forum_letter(letter: str) -> typing.Tuple[str, int]:
    response = download_page(
        '{}?ch={}'.format(URL, letter),
        os.path.join(DIR, 'char_{}.html'.format(letter))
    )
    pages = set(re.findall(r'\?ch='+letter+'&p=([0-9]+)', response))
    if len(pages) == 0:
        return letter, 1
    return letter, max(int(s) for s in pages)


def main():
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    main_page = download_page(URL, os.path.join(DIR, 'main.html'))
    params = set()
    items = set()
    with multiprocessing.Pool(25) as p:
        for letter, max_page in p.map(get_forum_letter, string.ascii_uppercase):
            params |= {(letter, i) for i in range(1, max_page+1)}
        for forums in p.starmap(get_forum_page, params):
            items |= forums
    with open('forums.txt', 'w') as f:
        f.write('\n'.join('forum:'+s for s in items)+'\n')

if __name__ == '__main__':
    main()

