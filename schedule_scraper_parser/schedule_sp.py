from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
from scraping_funcs import (login, set_default_group, get_lecturers, 
                            get_lecturer_classes, select_lecturer, show_schedule)

def get_schedule(user_name: str, user_password: str):
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize web driver
    WEB_DRIVER = webdriver.Chrome(options=chrome_options)
    # Navigate to the TSI site
    WEB_DRIVER.get('https://my.tsi.lv')
    # Authenticate
    login(WEB_DRIVER, user_name, user_password)
    # Navigate to the schedule page
    WEB_DRIVER.get('https://my.tsi.lv/schedule')
    # Initial schedule setup
    set_default_group(WEB_DRIVER)
    # Get all lecturers
    lecturers = get_lecturers(WEB_DRIVER)
    print(f"Schedule has {len(lecturers)} lecturers")

    # Scrape schedule for each lecturer
    schedule = []
    count = 1
    for lecturer in lecturers:
        try:
            select_lecturer(WEB_DRIVER, lecturer["value"])
            show_schedule(WEB_DRIVER)
            lecturer_classes = get_lecturer_classes(WEB_DRIVER)
            schedule.append(dict(lecturer=lecturer["full_name"], classes=lecturer_classes))
            count += 1
            break
        except Exception as e:
            count += 1
            continue

    # Close the web driver
    WEB_DRIVER.quit()

    # Parse schedule
    parsed_schedule = []
    for lecturer_schedule in schedule:
        lecturer = lecturer_schedule['lecturer']
        for day, lessons in lecturer_schedule['classes'].items():
            date = day
            for lesson in lessons:
                time = lesson['time']
                subject = lesson['subject'],
                type = lesson['class_type'],
                room = lesson['room'],
                groups = lesson['groups'],
                comment = lesson['comment']
                parsed_schedule.append(dict(date=date, time=time, lecturer=lecturer, 
                                            subject=subject[0], type=type[0], room=room[0], 
                                            groups=groups[0], comment=comment))
                
    # Sort by date and time
    parsed_schedule.sort(key=lambda x: (x['date'], x['time']['start']))

    # Save to json
    saved_at = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f'parsing_results/TSI_schedule_{saved_at}.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_schedule, f, ensure_ascii=False, indent=2)

    return parsed_schedule
