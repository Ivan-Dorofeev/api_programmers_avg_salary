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


def make_table(title, table):
    table_rows = []

    table_headers = ['Языки программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя заработная плата']
    table_rows.append(table_headers)
    for k, v in table.items():
        table_rows.append([k, v['vacancies_found'], v['vacancies_processed'], v['average_salary']])

    table = AsciiTable(table_rows, title)
    table.justify_columns[4] = 'right'
    print(table.table)
    print()


def predict_rub_salary_for_superJob(vacantion):
    if vacantion['payment_from'] and vacantion['payment_to']:
        avg_salary = int((vacantion['payment_from'] + vacantion['payment_to']) / 2)
        return avg_salary
    return None


def get_avg_salary_for_one_language_superjob(language):
    period_days = 7
    open_access = 1
    language_salary_and_vacancies = {"vacancies_found": None,
                                     "vacancies_processed": None,
                                     "average_salary": None
                                     }
    response = requests.get('https://api.superjob.ru/2.0/vacancies',
                            headers={'X-Api-App-Id': os.environ['SUPERJOB_SECRET_KEY']},
                            params={'keyword': language,
                                    'published': open_access,
                                    'period': period_days,
                                    'town': 'Москва',
                                    })
    response.raise_for_status()

    language_salaries = []
    vacancies = response.json()['objects']
    for vacancy in vacancies:
        avg_salary = predict_rub_salary_for_superJob(vacancy)
        if avg_salary:
            language_salaries.append(avg_salary)

    if language_salaries:
        language_salary_and_vacancies['average_salary'] = int(sum(language_salaries) / len(language_salaries))
        language_salary_and_vacancies['vacancies_processed'] = len(language_salaries)
        language_salary_and_vacancies['vacancies_found'] = response.json()['total']

    return language_salary_and_vacancies


def get_all_page(page, language):
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


def get_avg_salary_for_one_language_headhumter(language):
    salary = []
    vacancies_on_page = []

    for page in count():
        all_page = get_all_page(page, language)
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


def get_avg_salary_superjob(languages):
    languages_avg_salary = {}
    for language in languages:
        languages_avg_salary[language] = get_avg_salary_for_one_language_superjob(language)
    return languages_avg_salary


def get_avg_salary_headhumter(languages):
    languagies_avg_salary = {}
    for language in languages:
        languagies_avg_salary[language] = get_avg_salary_for_one_language_headhumter(language)
    return languagies_avg_salary


if __name__ == '__main__':
    load_dotenv()
    languages = ['python', 'java', 'goland', 'javascript', 'ruby', 'c++']

    avg_salary_superjob = get_avg_salary_superjob(languages)
    make_table('Superjob', avg_salary_superjob)

    avg_salary_headhumter = get_avg_salary_headhumter(languages)
    make_table('HeadHunter', avg_salary_headhumter)
