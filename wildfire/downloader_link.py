import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def download(user, passw, scene):
    options = Options()

    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Настройка опций
    options.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки сертификата
    options.add_argument("--ignore-ssl-errors")  # Игнорировать ошибки SSL
    # Указание пути к папке сохранения
    download_directory = os.path.join(script_directory, "download_folder")
    # options.add_argument(f"--download.default_directory={download_directory}")
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": script_directory,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    # Создание экземпляра ChromeDriver с опциями
    driver = webdriver.Chrome(options=options)

    # Вход на сайт
    driver.get('https://ers.cr.usgs.gov/login')
    username_input = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/form/div[1]/div[1]/input')
    password_input = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/form/div[1]/div[2]/input')
    login_button = driver.find_element(By.XPATH, value='//*[@id="loginButton"]')
    username_input.send_keys(user)
    password_input.send_keys(passw)
    login_button.click()
    time.sleep(5)
    # Завершение предыдущей сессии
    leave_old_sess = driver.find_element(By.XPATH, value='//*[@id="logoutEverwhereButton"]')
    leave_old_sess.click()
    time.sleep(5)
    # Переход на страницу загрузки
    driver.get(f'https://earthexplorer.usgs.gov/download/632211e26883b1f7/{scene}/')
    time.sleep(1)
    cont = driver.find_element(By.XPATH, value='//*[@id="centeredContainer"]/div/a[1]/div')
    cont.click()
    # Проверка доступности загрузки и переход на альтернативную страницу
    time.sleep(5)
    driver.get(f'https://earthexplorer.usgs.gov/download/632211e26883b1f7/{scene}/')
    time.sleep(1)
    text_to_find = '{"errorMessage":"Download is not available","isPending":false,"url":null}'
    text_to_find2 = '{"errorMessage":"Invalid scene or product","isPending":false,"url":null}'
    if driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(text_to_find)) or \
        driver.find_element(By.XPATH, "//*[contains(text(), '{}')]".format(text_to_find2)):
        driver.get(f'https://earthexplorer.usgs.gov/download/5e83d14fec7cae84/{scene}/')
    time.sleep(10)

    DISCONNECTED_MSG = 'Unable to evaluate script: no such window: target window already closed\nfrom unknown error: web view not found\n'

    while True:
        # Проверка закрытия окна браузера пользователем
        if len(driver.get_log('driver')) > 0:
            if driver.get_log('driver')[0]['message'] == DISCONNECTED_MSG:
                print('Browser window closed by user')
                driver.quit()
                break
        time.sleep(1)

    # Получение списка файлов в папке
    file_list = os.listdir(script_directory)

    # Фильтрация только файлов (исключение папок)
    file_list = [f for f in file_list if os.path.isfile(os.path.join(script_directory, f))]

    # Сортировка файлов по дате изменения (самый новый файл будет первым)
    sorted_files = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(script_directory, x)), reverse=True)

    if sorted_files:
        newest_file = sorted_files[0]
        return newest_file
    else:
        return 'None'

