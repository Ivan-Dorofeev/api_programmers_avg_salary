import os
from statistics import mean

import requests
from dotenv import load_dotenv


def predict_rub_salary(vacancy):
    if vacancy['salary'] is not None:
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        if salary_from is not None and salary_to is not None:
            avg_salary = int((salary_to + salary_from) / 2)
            return avg_salary
        return None
    return None


def main():
    load_dotenv()
    languages = ['python', 'java', 'goland', 'javascript']
    lang_salaries = {}
    for language in languages:
        url = 'https://api.hh.ru/vacancies'
        vacancies_params = {'text': language,
                            'area': 1,
                            'period': 30,
                            'per_page': 100
                            }
        vacancies = requests.get(url, params=vacancies_params)
        vacancies_salary = []
        vacancies_processed = len(vacancies.json()['items'])
        for vacancy in vacancies.json()['items']:
            avg_vacancy_salary = predict_rub_salary(vacancy)
            if avg_vacancy_salary is not None:
                vacancies_salary.append(avg_vacancy_salary)
        if len(vacancies_salary) == 0:
            average_salary = 0
        else:
            average_salary = int(sum(vacancies_salary) / len(vacancies_salary))
        lang_salaries[language] = {'vacancies_processed': vacancies_processed, 'average_salary': average_salary}
    print(lang_salaries)


if __name__ == '__main__':
    main()
