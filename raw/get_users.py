import multiprocessing
import os
import re
import time
import typing

import requests

URL = 'https://www.garnek.pl/0/indeks/'
DIR = 'pages'


def _download_page(url: int, filename: str) -> str:
    print('Getting', url)
    response = requests.get(url)
    assert response.status_code == 200
    assert url == url
    with open(os.path.join(DIR, filename), 'wb') as f:
        f.write(response.content)
    return response.text
    
    
def download_page(*args) -> str:
    tries = 0
    while True:
        try:
            tries += 1
            return _download_page(*args)
        except Exception:
            time.sleep(min(tries, 5))


def get_page(num: int) -> typing.Set[str]:
    response = download_page(
        '{}?p={}'.format(URL, num),
        'page_{}.html'.format(num)
    )
    results = set()
    for a, b in re.findall(r'<a href="/([^/]+)/a" title="([^"]+)">', response):
        assert a == b
        results.add(a)
    print(num, len(results))
    return results


def main():
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    main_page = download_page(URL, 'main.html')
    max_num = max(int(s) for s in re.findall(r'\?p=([0-9]+)', main_page))
    items = set()
    with multiprocessing.Pool(25) as p:
        for users in p.map(get_page, range(1, max_num+1)):
            items |= users
    with open('users.txt', 'w') as f:
        f.write('\n'.join('user:'+s for s in items)+'\n')

if __name__ == '__main__':
    main()

