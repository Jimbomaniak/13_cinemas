import requests, re
from bs4 import BeautifulSoup as BS


AFISHA_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://www.kinopoisk.ru/get'


def fetch_afisha_page():
    response = requests.get(AFISHA_URL)
    return response.content


def parse_afisha_list(html):
    soup = BS(html, 'html.parser')
    movies_info = soup.find('div', {
        'class': 'b-theme-schedule m-schedule-with-collapse',
        'id': 'schedule'})
    movies = []
    for num,movie in enumerate(movies_info.find_all(class_='object s-votes-hover-area collapsed')):
        print('{0} movies find'.format(num+1))
        rate, rating_count = fetch_movie_info(movie.h3.a.text)
        movies.append({
            'title': movie.h3.a.text,
            'cinema_number': len(movie.find_all('td', {'class': 'b-td-item'})),
            'rate': rate,
            'ratingCount': rating_count
            })
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
    return (rate, rating_count)


def sort_movies(movies, how_sort='rate'):
    sort_element = how_sort
    for i in range(len(movies)):
        for j in range(len(movies) - 1, i, -1):
            if movies[j][sort_element] > movies[j-1][sort_element]:
                movies[j], movies[j-1] = movies[j-1], movies[j]

    return movies


def output_movies_to_console(movies):
    for num, movie in enumerate(movies[0:10]):
        print('{0}. {title}, movie rate - {rate}, you can watch in {cinema_number} cinema'.format(num+1, **movie))
        print('------')


if __name__ == '__main__':
    movies = parse_afisha_list(fetch_afisha_page())
    sort_movies1 = sort_movies(movies)
    sort_movies2 = sort_movies(movies, 'cinema_number')
    output_movies_to_console(sort_movies1)
    output_movies_to_console(sort_movies2)

