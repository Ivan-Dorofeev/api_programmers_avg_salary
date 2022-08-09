import os
from itertools import count
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(vacancy):
    if vacancy['salary']:
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        if salary_from and salary_to:
            avg_salary = int((salary_to + salary_from) / 2)
            return avg_salary
        return None
    return None


def make_table(title, avg_languages_salary):
    table_rows = []

    table_headers = ['Языки программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя заработная плата']
    table_rows.append(table_headers)
    for language, salary in avg_languages_salary.items():
        table_rows.append(
            [language, salary['vacancies_found'], salary['vacancies_processed'], salary['average_salary']])

    table = AsciiTable(table_rows, title)
    table.justify_columns[4] = 'right'
    return table.table


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
    vacancies_salary = []
    vacancies_on_page = 0

    for page in count():
        all_page = get_json_page_superjob(page, language, api_key)
        for vacancy in all_page['objects']:
            avg_salary = predict_rub_salary_for_superJob(vacancy)
            if avg_salary:
                vacancies_salary.append(avg_salary)
                vacancies_on_page += 1

        if not all_page['more']:
            break

    if not vacancies_on_page:
        return {'average_salary': None,
                'vacancies_found': None,
                'vacancies_processed': None}

    return {'average_salary': int(sum(vacancies_salary) / len(vacancies_salary)),
            'vacancies_found': all_page['total'],
            'vacancies_processed': vacancies_on_page}


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
    salary = []
    vacancies_on_page = []

    for page in count():
        all_page = get_json_page_hh(page, language)
        if page >= all_page['pages']:
            break

        vacancies_on_page.append(all_page['per_page'])

        for vacancy in all_page['items']:
            avg_salary = predict_rub_salary(vacancy)
            if avg_salary is not None:
                salary.append(avg_salary)

    if sum(vacancies_on_page) > all_page['found']:
        vacancies_processed = all_page['found']
    else:
        vacancies_processed = sum(vacancies_on_page)

    return {'average_salary': int(sum(salary) / len(salary)),
            'vacancies_found': all_page['found'],
            'vacancies_processed': vacancies_processed}


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
