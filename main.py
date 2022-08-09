import os
from itertools import count
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(vacancy):
    if not vacancy['salary']:
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


def get_avg_salary_superjob(languages):
    period_days = 7
    open_access = 1

    languages_avg_salary = {}
    for language in languages:
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
            if not avg_salary:
                language_salaries.append(avg_salary)

        if not language_salaries:
            language_salary_and_vacancies['average_salary'] = int(sum(language_salaries) / len(language_salaries))
            language_salary_and_vacancies['vacancies_processed'] = len(language_salaries)
            language_salary_and_vacancies['vacancies_found'] = response.json()['total']

        languages_avg_salary[language] = language_salary_and_vacancies

    make_table('SuperJob', languages_avg_salary)


def get_avg_salary_headhumter(languages):
    period_days = 3
    moscow_region = 1

    languagies_avg_salary = {}
    for language in languages:
        salary = []
        vacancies_on_page = []

        for page in count():
            url = 'https://api.hh.ru/vacancies'
            vacancies_params = {'text': language,
                                'area': moscow_region,
                                'period': period_days,
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
    get_avg_salary_superjob(languages)
    get_avg_salary_headhumter(languages)
