import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup

results = {}
ids = 0
import csv

tasks = []


class Teleplay:
    def __init__(self, id, title, description, star, leader, tags, years, country, director_description, image_link, language, time_length, imdb_link):
        self.imdb_link = imdb_link
        self.time_length = time_length
        self.id = id
        self.star = star
        self.description = description
        self.title = title
        self.leader = leader
        self.tags = tags
        self.years = years
        self.country = country
        self.director_description = director_description
        self.image_link = image_link
        self.language = language


async def fetch(url, index):
    print('fetching url', url)
    async with aiohttp.ClientSession()as session:
        async with session.get(url) as response:
            assert response.status == 200
            print("this is index", index)
            return await response.text()


async def write_images(image_link, image_name):
    print('write images....', image_link)
    async with aiohttp.ClientSession()as session:
        async with session.get(image_link) as response:
            assert response.status == 200
            with open('teleplay_images/' + image_name, 'wb')as opener:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    opener.write(chunk)


async def parse_teleplay_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('span', {'property': 'v:itemreviewed'}).text
    image_link = soup.find('a', {'class': 'nbgnbg'}).find('img')['src']
    info = soup.find('div', {'id': 'info'})
    director = info.find_all('a', {'rel': 'v:directedBy'})
    if director is not None and len(director) > 0:
        director = director[0].text
    leader = [a.text for a in info.find_all('a', {'rel': 'v:starring'})]
    tags = [a.text for a in info.find_all('span', {'property': 'v:genre'})]
    country = info.find('span', string='制片国家/地区:')
    if country is not None:
        country = country.next_sibling
    language = info.find('span', string='语言:')
    if language is not None:
        language = language.next_sibling
    show_time = info.find('span', {'property': 'v:initialReleaseDate'})
    if show_time is not None:
        show_time = show_time.text
    time_length = info.find('span', {'property': 'v:runtime'})
    if time_length is not None:
        time_length = time_length.text
    imdb_link = info.find('span', string='IMDb链接:')
    try:
        if imdb_link is not None:
            imdb_link = imdb_link.fetchNextSiblings()[0]['href']
    except:
        imdb_link = None
    description = soup.find('span', {'property': 'v:summary'})
    if description is not None:
        description = description.text
    star = soup.find('strong', {'property': 'v:average'})
    if star is not None:
        star = star.text

    # comments = soup.find_all('div', {'class': 'comment-item'})
    return Teleplay(image_link=image_link, title=title, star=star, leader=leader, tags=tags, country=country, director_description=director, years=show_time, id=ids, description=description, time_length=time_length, imdb_link=imdb_link, language=language)


async def write_teleplays(teleplay, index, filename):
    print('write teleplays..')
    with open(filename, 'a+')as opener:
        writer = csv.writer(opener)
        if opener.tell() == 0:
            writer.writerow(['id', 'title ', 'image_link ', 'country ', 'years ', 'director_description', 'leader', 'star ', 'description', 'tags', 'imdb', 'language', 'time_length', ''])
        writer.writerow([index, teleplay.title, teleplay.image_link, teleplay.country, teleplay.years, teleplay.director_description, teleplay.leader, teleplay.star, teleplay.description, '/'.join(teleplay.tags), teleplay.imdb_link, teleplay.language, teleplay.time_length])


async def get_results(index, url, parser, filename):
    html = await fetch(url, index)
    teleplays = await parser(html)
    image_name = teleplays.image_link.split('/')[-1]
    await write_images(image_link=teleplays.image_link, image_name=image_name)
    await write_teleplays(teleplays, index, filename)


async def handle_tasks(work_queue, parser, filename):
    while not work_queue.empty():
        index, current_url = await work_queue.get()
        current_url = current_url[0]
        print('index', current_url, index)
        try:
            await get_results(index, current_url, parser, filename)
        except Exception as e:
            logging.exception('Error for {}'.format(current_url), exc_info=True)


def envent_loop(link_filename, write_filename):
    q = asyncio.Queue()
    with open(link_filename, 'r')as opener:
        reader = csv.reader(opener)
        for index, link in enumerate(reader):
            q.put_nowait((index, link))
    loop = asyncio.get_event_loop()
    tasks.append(handle_tasks(q, parse_teleplay_page, write_filename))
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    # 读写电视剧内容
    envent_loop(link_filename='all_links.csv', write_filename='all_links_details.csv')
