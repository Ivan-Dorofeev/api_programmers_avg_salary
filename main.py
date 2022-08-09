import os
from itertools import count
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def make_table(title, avg_languages_salary):
    table_rows = []

    table_headers = ['Языки программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя заработная плата']
    table_rows.append(table_headers)
    for language, salary in avg_languages_salary.items():
        table_rows.append(
            [language, salary['vacancies_found'], salary['processed_vacancies'], salary['average_salary']])

    table = AsciiTable(table_rows, title)
    table.justify_columns[4] = 'right'
    return table.table


def predict_rub_salary_for_hh(vacancy):
    if not vacancy['salary']:
        return None
    elif vacancy['salary']['from']:
        return int(vacancy['salary']['from'] * 1.2)
    elif vacancy['salary']['from']:
        return int(vacancy['salary']['to'] * 0.8)
    return int((vacancy['salary']['from'] + vacancy['salary']['to']) / 2)


def predict_rub_salary_for_superJob(vacantion):
    if not vacantion['payment_from'] and not vacantion['payment_to']:
        return None
    elif vacantion['payment_from'] and not vacantion['payment_to']:
        return int(vacantion['payment_from'] * 1.2)
    elif not vacantion['payment_from'] and vacantion['payment_to']:
        return int(vacantion['payment_to'] * 0.8)
    return int((vacantion['payment_from'] + vacantion['payment_to']) / 2)


def get_json_page_superjob(page, language, api_key):
    period_days = 7
    open_access = 1
    response = requests.get('https://api.superjob.ru/2.0/vacancies',
                            headers={'X-Api-App-Id': api_key},
                            params={'keyword': language,
                                    'page': page,
                                    'published': open_access,
                                    'period': period_days,
                                    'town': 'Москва',
                                    })
    response.raise_for_status()
    return response.json()


def get_avg_salary_for_one_language_superjob(language, api_key):
    vacancy_salaries = []
    vacancies_on_page = 0

    for page in count():
        all_page = get_json_page_superjob(page, language, api_key)
        for vacancy in all_page['objects']:
            avg_salary = predict_rub_salary_for_superJob(vacancy)
            if avg_salary:
                vacancy_salaries.append(avg_salary)
                vacancies_on_page += 1

        if not all_page['more']:
            break

    if not vacancies_on_page:
        return {'average_salary': None,
                'vacancies_found': None,
                'processed_vacancies': None}

    return {'average_salary': int(sum(vacancy_salaries) / len(vacancy_salaries)),
            'vacancies_found': all_page['total'],
            'processed_vacancies': vacancies_on_page}


def get_json_page_hh(page, language):
    period_days = 3
    moscow_region = 1
    url = 'https://api.hh.ru/vacancies'
    vacancies_params = {'text': language,
                        'area': moscow_region,
                        'period': period_days,
                        'page': page
                        }
    page_response = requests.get(url, params=vacancies_params)
    page_response.raise_for_status()
    return page_response.json()


def get_avg_salary_for_one_language_headhunter(language):
    vacancy_salaries = []
    vacancies_on_page = 0

    for page in count():
        all_page = get_json_page_hh(page, language)
        if page >= all_page['pages']:
            break

        for vacancy in all_page['items']:
            avg_salary = predict_rub_salary_for_hh(vacancy)
            if avg_salary:
                vacancy_salaries.append(avg_salary)
                vacancies_on_page += 1

    return {'average_salary': int(sum(vacancy_salaries) / len(vacancy_salaries)),
            'vacancies_found': all_page['found'],
            'processed_vacancies': vacancies_on_page}


def get_avg_salary_superjob(languages, api_key):
    languages_avg_salary = {}
    for language in languages:
        languages_avg_salary[language] = get_avg_salary_for_one_language_superjob(language, api_key)
    return languages_avg_salary


def get_avg_salary_headhumter(languages):
    languagies_avg_salary = {}
    for language in languages:
        languagies_avg_salary[language] = get_avg_salary_for_one_language_headhunter(language)
    return languagies_avg_salary


def main():
    load_dotenv()
    super_job_api_key = os.environ['SUPERJOB_SECRET_KEY']
    languages = ['python', 'java', 'goland', 'javascript', 'ruby', 'c++']

    avg_salary_superjob = get_avg_salary_superjob(languages, super_job_api_key)
    print(make_table('Superjob', avg_salary_superjob))

    avg_salary_headhumter = get_avg_salary_headhumter(languages)
    print(make_table('HeadHunter', avg_salary_headhumter))


if __name__ == '__main__':
    main()
