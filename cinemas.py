import random
import requests
import progressbar
from bs4 import BeautifulSoup
from operator import itemgetter


def fetch_afisha_page():
    afisha_url = "http://www.afisha.ru/msk/schedule_cinema"
    return requests.get(afisha_url).content


def parse_afisha_list(raw_html, cinemas_count=10):
    cinemas = []
    soup = BeautifulSoup(raw_html, 'html.parser')
    cinemas_content = (soup.find_all(
        class_='object s-votes-hover-area collapsed'))
    proxies_list = get_proxy()
    bar = progressbar.ProgressBar(max_value=len(cinemas_content))
    for cinema_number, cinema in enumerate(cinemas_content):
        bar.update(cinema_number + 1)
        cinema_name = cinema.find(class_='usetags').text
        count_of_cinemas = 0 if not cinema.findAll(class_="b-td-item") \
            else len(cinema.findAll(class_="b-td-item"))
        cinema_info_from_kinopoisk = parse_kinopoisk_movie_page(
            fetch_movie_info(cinema_name, proxies_list))
        cinemas.append({
            'name': cinema_name,
            'count_of_cinemas': count_of_cinemas,
            'kinopoisk_raiting': cinema_info_from_kinopoisk['rating'],
            'kinopoisk_raiting_count':
            cinema_info_from_kinopoisk['raiting_count']})
    return cinemas


def get_proxy():
    url_proxy = 'http://www.freeproxy-list.ru/api/proxy'
    params = {'token': 'demo'}
    html = requests.get(url_proxy, params=params).text
    proxies_list = html.split('\n')
    return proxies_list


def get_random_user_agent():
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0)\
         Gecko/20100101 Firefox/45.0',
        'Mozilla/5.0 (X11; Linux i686; rv:2.0.1)\
         Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388\
         Version/12.17',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0)\
         Gecko/20100101 Firefox/47.0',
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1;\
         WOW64; Trident/6.0)"
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1;\
         Trident/6.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/1.22 (compatible; MSIE 10.0; Windows 3.1)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64;\
         Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3;\
          MS-RTC LM 8; Zune 4.7)",
        "Mozilla/5.0 (compatible; MSIE 9.0;\
         Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0;\
          InfoPath.3; MS-RTC LM 8; Zune 4.7",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64;\
         Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729;\
          .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0;\
           InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)",
    ]
    user_agent = random.sample(user_agent_list, 1)[0]
    return user_agent


def parse_kinopoisk_movie_page(movie_page):
    if not movie_page:
        return {'rating': 0,
                'raiting_count': 0}
    soup = BeautifulSoup(movie_page, 'html.parser')
    rating = soup.find(class_="rating_ball").text if soup.find(
        class_="rating_ball") else 0
    raiting_count = soup.find(class_="ratingCount").text if soup.find(
        class_="ratingCount") else 0
    return {'rating': rating,
            'raiting_count': raiting_count}


def fetch_movie_info(movie_title, proxies_list):
    try:
        kinopoisk_url = 'https://www.kinopoisk.ru/index.php'
        params = {'kp_query': movie_title,
                  'first': 'yes'}
        proxy = {"http": random.choice(proxies_list)}
        timeout = random.randrange(2, 10)
        headers = {"Connection": "close",
                   "User-Agent": get_random_user_agent()}
        movie_page = requests.session().get(kinopoisk_url,
                                            params=params,
                                            proxies=proxy,
                                            timeout=timeout,
                                            headers=headers)
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ChunkedEncodingError):
        return None
    else:
        return movie_page.content


def output_movies_to_console(movies, top_movies_count=10):
    print()
    for movie in sorted(movies,
                        key=itemgetter('kinopoisk_raiting',
                                       'kinopoisk_raiting_count'),
                        reverse=True)[:top_movies_count]:

        print('{} имеет рейтинг {}, оценили \
{} человек и идет в {} кинотеатрах'.format(movie['name'],
                                           movie['kinopoisk_raiting'],
                                           movie['kinopoisk_raiting_count'],
                                           movie['count_of_cinemas']))


if __name__ == '__main__':
    afisha_html = fetch_afisha_page()
    cinemas = parse_afisha_list(afisha_html)
    output_movies_to_console(cinemas)
