import codecs
import configparser
import os
from datetime import datetime
import time
from datetime import date
import requests


config = configparser.ConfigParser()
config.read_file(codecs.open("config.ini", 'r', 'utf8'))
# config.read('config.ini')

RESULT = config.get('Main', 'RESULT')
ARCHIVE = config.get('Main', 'ARCHIVE')
TOKEN = config.get('Main', 'TOKEN')

SLEEP = int(config.get('Main', 'SLEEP'))
START_ID = int(config.get('Main', 'START_ID'))
vacancy_ids = []

today = str(date.today())

url = 'https://api.rabota.ru/v6/vacancies.json'
headers = {
    'Content-Type': 'application/json',
    'X-Token': TOKEN}
data = {
    "request": {
        "fields": [
            "id",
            "title",
            "salary",
            "salary.from",
            "salary.currency",
            "salary.currency_sign",
            "salary.to",
            "salary.pay_type",
            "description",
            "short_description",
            "places",
            "places.id",
            "places.name",
            "places.address",
            "places.kladr_id",
            "places.street_kladr_id",
            "places.city_kladr_id",
            "places.settlement_kladr_id",
            "places.house",
            "places.is_show_on_map",
            "places.region",
            "places.company_representation",
            "places.geopoint",
            "places.subway_stations",
            "places.comment",
            "contact_person",
            "contact_person.name",
            "contact_person.has_phone",
            "contact_person.phones",
            "contact_person.email",
            "publish_start_at",
            "modified_date",
            "operating_schedule",
            "operating_schedule.id",
            "operating_schedule.name",
            "operating_schedule.name_case",
            "experience",
            "experience.id",
            "experience.name",
            "education",
            "education.id",
            "education.name",
            "is_promoted",
            "professional_areas",
            "professional_areas.id",
            "professional_areas.name",
            "professional_areas.tree",
            "professional_areas.selectable",
            "professional_areas.custom_position_name_ids",
            "tariff_group",
            "tariff_group.id",
            "tariff_group.name",
            "tags",
            "tags.id",
            "tags.name",
            "tags.tooltip",
            "skills",
            "skills.id",
            "skills.name",
            "status",
            "og_image_url",
            "vk_image_url",
            "twitter_image_url",
            "is_favourite",
            "is_study_course",
            "response",
            "response.id",
            "response.created_at",
            "response.resume",
            "response.vacancy",
            "response.recruiter",
            "response.last_message",
            "response.sent_by",
            "response.status",
            "response.last_modified_at",
            "response.has_new",
            "response.deleted_vacancy_title",
            "response.is_autoresponse",
            "seo",
            "seo.backpath",
            "seo.links",
            "seo.canonical",
            "seo.title",
            "seo.h1",
            "seo.description",
            "seo.keywords",
            "seo.is_noindex",
            "seo.is_nofollow",
            "company",
            "company.id",
            "company.name",
            "company.slug",
            "company.offer_branches",
            "company.logo",
            "company.logo_vacancy_preview",
            "company.logo_company_preview",
            "company.logo_vacancy_detail_preview",
            "company.type",
            "company.short_description",
            "company.description_pages",
            "company.company_size",
            "company.company_type_of_ownership",
            "company.company_main_representation",
            "company.is_direct_recruiter",
            "company.awards",
            "company.benefits",
            "company.call_tracking_enabled",
            "company.rostrud_sync_enabled",
            "company.personal_manager",
            "company.is_verified",
            "company.status",
            "company.is_activated_recently",
            "company.is_sbbol",
            "company.is_in_blacklist",
            "company.is_basic_solution_project",
            "company.vacancies_count",
            "breadcrumbs",
            "breadcrumbs.title",
            "breadcrumbs.url",
            "view_more_links",
            "view_more_links.title",
            "view_more_links.url",
            "responded_recently",
            "query_groups",
            "query_groups.id",
            "query_groups.name",
            "query_groups.is_main",
            "top_position",
            "top_position.id",
            "top_position.name",
            "branding_settings",
            "branding_settings.search",
            "branding_settings.page",
            "places_summary",
            "places_summary.text",
            "places_summary.name",
            "places_summary.name_case_accs",
            "places_summary.name_case_loct",
            "places_summary.type",
            "places_summary.count",
            "places_summary.subway_line_color",
            "places_summary.distance",
            "places_summary.travel_time",
            "branding",
            "branding.card",
            "branding.search_result"
        ],
        "vacancy_ids": vacancy_ids,
        "location": {
            "max_distance": None,
            "geopoint": {
                "latitude": 0,
                "longitude": 0
            },
            "type": "region",
            "name": "",
            "region_id": 5,
            "subway_station_id": None,
            "max_time": None,
            "region": {
                "id": 0,
                "name": "",
                "name_case_loct": "",
                "name_case_gent": "",
                "domain": "",
                "tree_path_ids": [
                    0
                ],
                "type_id": 0,
                "is_big_city": None,
                "specify": "",
                "has_subway": False,
                "geopoint": {
                    "latitude": 0,
                    "longitude": 0
                },
                "distance": None
            }
        }
    },
    "user_tags": [
        {
            "id": None,
            "name": "",
            "add_date": '2022-05-30',
            "campaign_key": None
        }
    ],
    "rabota_ru_id": "",
    "cache_control_max_age": 0
}


def check_duplicate():
    if os.path.exists(RESULT):
        print(datetime.now().time(), ': Проверка RESULT на дубликаты')
        with open(RESULT, 'r', encoding='utf-8') as f:
            uniqlines = set(f.readlines())
        with open(RESULT, 'w', encoding='utf-8') as f:
            f.writelines(set(uniqlines))
        print(datetime.now().time(), ': Закончил проверку RESULT')

    if os.path.exists(ARCHIVE):
        print(datetime.now().time(), ': Проверка ARCHIVE на дубликаты')
        with open(ARCHIVE, 'r', encoding='utf-8') as f:
            uniqlines = set(f.readlines())
        with open(ARCHIVE, 'w', encoding='utf-8') as f:
            f.writelines(set(uniqlines))
        print(datetime.now().time(), ': Закончил проверку ARCHIVE')


def check_active():
    print(datetime.now().time(), ': Проверка RESULT на активные вакансии')
    with open(RESULT, 'r', encoding='utf-8') as f:
        file = [i for i in f.readlines()]
    new_list = []
    for vacancy in file:
        vac_id = vacancy.split(';')[1].split('/')[-1]

        data = {
    "request": {
        "fields": [
            "id",
            "title",
            "salary",
            "salary.from",
            "salary.currency",
            "salary.currency_sign",
            "salary.to",
            "salary.pay_type",
            "description",
            "short_description",
            "places",
            "places.id",
            "places.name",
            "places.address",
            "places.kladr_id",
            "places.street_kladr_id",
            "places.city_kladr_id",
            "places.settlement_kladr_id",
            "places.house",
            "places.is_show_on_map",
            "places.region",
            "places.company_representation",
            "places.geopoint",
            "places.subway_stations",
            "places.comment",
            "contact_person",
            "contact_person.name",
            "contact_person.has_phone",
            "contact_person.phones",
            "contact_person.email",
            "publish_start_at",
            "modified_date",
            "operating_schedule",
            "operating_schedule.id",
            "operating_schedule.name",
            "operating_schedule.name_case",
            "experience",
            "experience.id",
            "experience.name",
            "education",
            "education.id",
            "education.name",
            "is_promoted",
            "professional_areas",
            "professional_areas.id",
            "professional_areas.name",
            "professional_areas.tree",
            "professional_areas.selectable",
            "professional_areas.custom_position_name_ids",
            "tariff_group",
            "tariff_group.id",
            "tariff_group.name",
            "tags",
            "tags.id",
            "tags.name",
            "tags.tooltip",
            "skills",
            "skills.id",
            "skills.name",
            "status",
            "og_image_url",
            "vk_image_url",
            "twitter_image_url",
            "is_favourite",
            "is_study_course",
            "response",
            "response.id",
            "response.created_at",
            "response.resume",
            "response.vacancy",
            "response.recruiter",
            "response.last_message",
            "response.sent_by",
            "response.status",
            "response.last_modified_at",
            "response.has_new",
            "response.deleted_vacancy_title",
            "response.is_autoresponse",
            "seo",
            "seo.backpath",
            "seo.links",
            "seo.canonical",
            "seo.title",
            "seo.h1",
            "seo.description",
            "seo.keywords",
            "seo.is_noindex",
            "seo.is_nofollow",
            "company",
            "company.id",
            "company.name",
            "company.slug",
            "company.offer_branches",
            "company.logo",
            "company.logo_vacancy_preview",
            "company.logo_company_preview",
            "company.logo_vacancy_detail_preview",
            "company.type",
            "company.short_description",
            "company.description_pages",
            "company.company_size",
            "company.company_type_of_ownership",
            "company.company_main_representation",
            "company.is_direct_recruiter",
            "company.awards",
            "company.benefits",
            "company.call_tracking_enabled",
            "company.rostrud_sync_enabled",
            "company.personal_manager",
            "company.is_verified",
            "company.status",
            "company.is_activated_recently",
            "company.is_sbbol",
            "company.is_in_blacklist",
            "company.is_basic_solution_project",
            "company.vacancies_count",
            "breadcrumbs",
            "breadcrumbs.title",
            "breadcrumbs.url",
            "view_more_links",
            "view_more_links.title",
            "view_more_links.url",
            "responded_recently",
            "query_groups",
            "query_groups.id",
            "query_groups.name",
            "query_groups.is_main",
            "top_position",
            "top_position.id",
            "top_position.name",
            "branding_settings",
            "branding_settings.search",
            "branding_settings.page",
            "places_summary",
            "places_summary.text",
            "places_summary.name",
            "places_summary.name_case_accs",
            "places_summary.name_case_loct",
            "places_summary.type",
            "places_summary.count",
            "places_summary.subway_line_color",
            "places_summary.distance",
            "places_summary.travel_time",
            "branding",
            "branding.card",
            "branding.search_result"
        ],
        "vacancy_id": vac_id,
        "location": {
            "max_distance": None,
            "geopoint": {
                "latitude": 0,
                "longitude": 0
            },
            "type": "region",
            "name": "",
            "region_id": 3,
            "subway_station_id": None,
            "max_time": None,
            "region": {
                "id": 0,
                "name": "",
                "name_case_loct": "",
                "name_case_gent": "",
                "domain": "",
                "tree_path_ids": [
                    0
                ],
                "type_id": 0,
                "is_big_city": None,
                "specify": "",
                "has_subway": None,
                "geopoint": {
                    "latitude": 0,
                    "longitude": 0
                },
                "distance": None
            }
        }
    },
    "user_tags": [
        {
            "id": None,
            "name": "",
            "add_date": today,
            "campaign_key": None
        }
    ],
    "rabota_ru_id": "",
    "cache_control_max_age": 0
}
        url = 'https://api.rabota.ru/v6/vacancy.json'
        result = requests.post(url, headers=headers, json=data).json()
        if result['response']['status'] not in ['deleted', 'unpublished']:
            new_list.append(vacancy)
    with open(RESULT, 'w', encoding='utf-8') as f:
        f.writelines(new_list)


def write_data(vacancies):
    with open(RESULT, 'a', encoding='utf-8') as r:
        with open(ARCHIVE, 'a', encoding='utf-8') as a:
            written_vacancies = set()
            for vacancy in vacancies:
                if vacancy['id'] not in written_vacancies:
                    if vacancy['status'] not in ['deleted', 'unpublished']:
                        print(datetime.now().time(), f": Записываю данные {vacancy['id']}")
                        link = f"https://www.rabota.ru/vacancy/{vacancy['id']}" if vacancy['id'] is not None else ''
                        phone = f"{vacancy['contact_person']['phones'][0]['number_international']}" \
                            if len(vacancy['contact_person']['phones']) > 0 else ''
                        phone2 = f"{vacancy['contact_person']['phones'][1]['number_international']}" \
                            if len(vacancy['contact_person']['phones']) >= 2 else ''
                        name = f"{vacancy['contact_person']['name']}" \
                            if {vacancy['contact_person']['name'] is not None} else ''
                        vacancy_name = f"{vacancy['title']}" if vacancy['title'] is not None else ''
                        email = f"{vacancy['contact_person']['email']}" \
                            if {vacancy['contact_person']['email']} is not None else ''
                        company = f"{vacancy['company']['name']}" if vacancy['company'] is not None else ''
                        str_to_write = f";{link};{phone};{phone2};{name};{vacancy_name};{email};{company};\n"
                        r.write(str_to_write)
                        a.write(str_to_write)
                        written_vacancies.add(vacancy['id'])


def get_vacancies():
    print(datetime.now().time(), ': Отправляю запрос')
    return requests.post(url, headers=headers, json=data)


def main():
    last_vacancy_id = START_ID
    while True:
        vacancy_ids.clear()
        print(datetime.now().time(), ': Добавляю в очередь id вакансий')
        for i in range(last_vacancy_id, last_vacancy_id+99):
            vacancy_ids.append(i)
        response = get_vacancies()
        try:
            if len(response.json()['response']['vacancies']) == 0 and last_vacancy_id < 49000000:
                last_vacancy_id += 1
            elif len(response.json()['response']['vacancies']) == 0:
                print(datetime.now().time(), ': Дошел до конца')
                last_vacancy_id = START_ID
                config.set("Main", "last_vacancy_id", str(last_vacancy_id))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                print(datetime.now().time(), f': Проверка дубликатов, активный вакансий'
                                             f' и ожидание {SLEEP} сек.')
                check_duplicate()
                check_active()
            else:
                write_data(response.json()['response']['vacancies'])
                print(datetime.now().time(), ': Обновляю очередь')

                last_vacancy_id += len(response.json()['response']['vacancies'])
                vacancy_ids.clear()

        except Exception as e:
            print(datetime.now().time(), f': [!] Ошибка: {e}')
            continue
        print(datetime.now().time(), f': Запись последнего Id в конфиг - {last_vacancy_id}')
        config.set("Main", "last_vacancy_id", str(last_vacancy_id))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)


if __name__ == '__main__':
    check_duplicate()
    main()
