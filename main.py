import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()

    # get_token_url = f'https://hh.ru/oauth/authorize'
    # params = {'response_type': os.environ['AUTHORIZATION_CODE'],
    #           'client_id': os.environ['CLIENT_ID'],
    #           'state': 'state',
    #           'redirect_uri': 'https://hh.ru/'}

    # regions = requests.get('https://api.hh.ru/areas')
    # print(regions.text)

    url = 'https://api.hh.ru/vacancies'
    vacancies_params = {'text': 'python',
                        'area': 1,
                        'period': 30,
                        'per_page': 20
                        }
    vacancies = requests.get(url, params=vacancies_params)
    for vacancy in vacancies.json()['items']:
        print(vacancy['salary'])


if __name__ == '__main__':
    main()
