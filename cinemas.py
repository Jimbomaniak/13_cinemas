import requests
import re
from bs4 import BeautifulSoup as BS


AFISHA_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://www.kinopoisk.ru/get'
NUMBER_MOVIES_TO_SHOW = 10


def fetch_afisha_page():
    response = requests.get(AFISHA_URL)
    return response.content


def parse_afisha_list(html):
    soup = BS(html, 'html.parser')
    movies_info = soup.find('div', {
        'class': 'b-theme-schedule m-schedule-with-collapse',
        'id': 'schedule'})
    movies = []
    for movie in movies_info.find_all(class_='object s-votes-hover-area collapsed'):
        one_movie = fetch_movie_info(movie.h3.a.text)
        one_movie['title'] = movie.h3.a.text
        one_movie['cinema_number'] = len(movie.find_all('td', {'class': 'b-td-item'}))
        movies.append(one_movie)
    return movies


def fetch_movie_info(movie_title):
    payload = {'kp_query': movie_title, 'first': 'yes'}
    response = requests.get(KINOPOISK_URL, params=payload)
    soup = BS(response.content, 'html.parser')
    try:
        rate = float(soup.find('span', class_='rating_ball').text)
        rating_count_site = soup.find('span', class_='ratingCount').text
        rating_count_digits = re.search(r'\d+', rating_count_site)
        rating_count = int(rating_count_digits.group())
    except AttributeError:
        rate, rating_count = 0, 0
    return {'rate': rate, 'ratingCount': rating_count}


def sort_movies(movies, how_sort_movies):
    sort_by = how_sort_movies and 'cinema_number' or 'rate'
    movies.sort(key=lambda item: item[sort_by], reverse=True)
    return movies


def output_movies_to_console(movies, number_movies_to_show):
    for num, movie in enumerate(movies[:number_movies_to_show]):
        print('{0}. {title}, movie rate - {rate},'
              'you can watch in {cinema_number} cinema'.format(num+1, **movie))
        print('------')


if __name__ == '__main__':
    movies = parse_afisha_list(fetch_afisha_page())
    how_sort_movies = int(input('0 - movies by rating\n'
                       '1 - movies by cinema numbers\nEnter 1 or 0: '))
    sort_movies = sort_movies(movies, how_sort_movies)
    output_movies_to_console(sort_movies, NUMBER_MOVIES_TO_SHOW)
