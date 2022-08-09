import os
from itertools import count
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(vacancy):
    if vacancy['salary'] is not None:
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        if salary_from is not None and salary_to is not None:
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
    if vacantion['payment_from'] not in [None, 0] or vacantion['payment_to'] not in [None, 0]:
        avg_salary = int((vacantion['payment_from'] + vacantion['payment_to']) / 2)
        return avg_salary
    return None


def superjob_avg_salary(languages):
    languages_avg_salary = {}
    for language in languages:
        language_salary_and_vacancies = {"vacancies_found": None,
                                         "vacancies_processed": None,
                                         "average_salary": None
                                         }
        response = requests.get('https://api.superjob.ru/2.0/vacancies',
                                headers={'X-Api-App-Id': os.environ['SUPERJOB_SECRET_KEY']},
                                params={'keyword': language,
                                        'published': 1,
                                        'period': 7,
                                        'town': 'Москва',
                                        })
        response.raise_for_status()

        language_salaies = []
        for i in response.json()['objects']:
            avg_salary = predict_rub_salary_for_superJob(i)
            if avg_salary is not None:
                language_salaies.append(avg_salary)

        if not len(language_salaies) == 0:
            language_salary_and_vacancies['average_salary'] = int(sum(language_salaies) / len(language_salaies))
            language_salary_and_vacancies['vacancies_processed'] = len(language_salaies)
            language_salary_and_vacancies['vacancies_found'] = response.json()['total']

        languages_avg_salary[language] = language_salary_and_vacancies

    make_table('SuperJob', languages_avg_salary)


def hh_avg_salary(languages):
    languagies_avg_salary = {}
    for language in languages:
        salary = []
        vacancies_on_page = []

        for page in count():
            url = 'https://api.hh.ru/vacancies'
            vacancies_params = {'text': language,
                                'area': 1,
                                'period': 3,
                                'page': page
                                }
            page_response = requests.get(url, params=vacancies_params)
            page_response.raise_for_status()
            all_page = page_response.json()
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

        languagies_avg_salary[language] = {'average_salary': int(sum(salary) / len(salary)),
                                           'vacancies_found': all_page['found'],
                                           'vacancies_processed': vacancies_processed}

    make_table('HeadHunter', languagies_avg_salary)


if __name__ == '__main__':
    load_dotenv()
    languages = ['python', 'java', 'goland', 'javascript', 'ruby', 'c++']
    superjob_avg_salary(languages)
    hh_avg_salary(languages)
