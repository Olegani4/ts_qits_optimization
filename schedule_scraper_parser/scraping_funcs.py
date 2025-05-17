from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import datetime

def login(WEB_DRIVER, user_name, user_password):
    # Authentication of the user
    username_input = WEB_DRIVER.find_element(By.NAME, "username")
    username_input.send_keys(user_name)

    password_input = WEB_DRIVER.find_element(By.NAME, "password")
    password_input.send_keys(user_password)

    submit_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

def set_default_group(WEB_DRIVER):
    # Select default group -1
    group_select = WEB_DRIVER.find_element(By.NAME, "sel-group")
    select = Select(group_select)
    select.select_by_value("-1") 

def get_lecturers(WEB_DRIVER):
    lecturer_select = WEB_DRIVER.find_element(By.NAME, "sel-lecturer")
    # Get all lecturers names and values
    lecturers = []  # dict(full_name: str, value: str)
    for option in lecturer_select.find_elements(By.TAG_NAME, "option"):
        lecturers.append({"full_name": option.text, "value": option.get_attribute("value")})
    lecturers.pop(0)  # Remove first element - "Select lecturer"
    return lecturers

def select_lecturer(WEB_DRIVER, lecturer_value):
    lecturer_select = WEB_DRIVER.find_element(By.NAME, "sel-lecturer")
    select = Select(lecturer_select)
    select.select_by_value(lecturer_value) 

def get_schedule_title(WEB_DRIVER):
    schedule_title = WEB_DRIVER.find_element(By.CSS_SELECTOR, "div[class='col-lg-6 form-row']")
    return schedule_title.text

def get_schedule_back(WEB_DRIVER):
    # Get month back button
    back_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[name='prev']")
    back_button.click()

def get_schedule_next(WEB_DRIVER):
    next_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[name='next']")
    next_button.click()

def show_schedule(WEB_DRIVER):
    show_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[name='show']")
    show_button.click()

def get_schedule_day(WEB_DRIVER):
    day_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[name='day']")
    day_button.click()

def get_schedule_month(WEB_DRIVER):
    month_button = WEB_DRIVER.find_element(By.CSS_SELECTOR, "button[name='mon']")
    month_button.click()

def get_day_classes(WEB_DRIVER):
    """
    Output example:
    [{'class_number': '1',
    'time': {'start': '08:45:00', 'end': '10:15:00'},
    'room': '703',
    'groups': ['3102BNA', '3202BNA', '3203BNA'],
    'subject': 'Business Economics and Marketing Basics',
    'class_type': 'Lesson',
    'comment': None},
    {'class_number': '2',
    'time': {'start': '10:30:00', 'end': '12:00:00'},
    'room': '703',
    'groups': ['3102BNA', '3202BNA', '3203BNA'],
    'subject': 'Business Economics and Marketing Basics',
    'class_type': 'Lesson',
    'comment': None}]
    """

    # Scraping schedule
    schedule_table = WEB_DRIVER.find_element(By.CSS_SELECTOR, "table[class='table table-bordered table-condensed']")

    # get tbody
    tbody = schedule_table.find_element(By.TAG_NAME, "tbody")

    # get all rows from the tbody
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    classes = []

    for row in rows:
        cells = []
        for cell in row.find_elements(By.TAG_NAME, "td"):
            cells.append(cell.text)

        if cells[1] == "":
            continue

        class_number = cells[0]
        time_str = cells[1]  # Format: "8:45 - 10:15"
        
        # Convert to proper time format
        start_time = datetime.datetime.strptime(time_str.split(" - ")[0], "%H:%M").time()
        end_time = datetime.datetime.strptime(time_str.split(" - ")[1], "%H:%M").time()
        
        time = dict(
            start=start_time.strftime("%H:%M:%S"),
            end=end_time.strftime("%H:%M:%S")
        )
        
        room = cells[2] if cells[2] != "" else None
        groups = cells[3].split(", ") if cells[3] != "" else []
        subject = cells[5] if cells[5] != "" else None
        class_type = cells[6] if cells[6] != "" else None
        comment = cells[7] if cells[7] != "" else None

        lecture = dict(class_number=class_number, time=time, room=room, groups=groups, 
                      subject=subject, class_type=class_type, comment=comment)

        classes.append(lecture)

    return classes

def get_day_date(WEB_DRIVER):
    # Friday, March 21, 2025
    schedule_title = get_schedule_title(WEB_DRIVER)
    month_and_day = schedule_title.split(", ")[1]
    month = month_and_day.split(" ")[0] 
    month = datetime.datetime.strptime(month, '%B').month
    day = int(month_and_day.split(" ")[1])
    year = int(schedule_title.split(", ")[2])
    date = datetime.datetime(year, month, day)
    return date.strftime('%Y-%m-%d')

def go_to_schedule_start(WEB_DRIVER):
    get_schedule_month(WEB_DRIVER)
    start_date = datetime.datetime(2025, 1, 1)
    while True:
        try:
            schedule_date_str = get_schedule_title(WEB_DRIVER)
            schedule_date = datetime.datetime.strptime(schedule_date_str, '%B %Y')
            if schedule_date <= start_date:
                break
            get_schedule_back(WEB_DRIVER)
        except Exception as e:
            pass
    
    try:
        start_date_str = start_date.strftime('%Y-%m-%d')
        start_date_elem = WEB_DRIVER.find_element(By.ID, start_date_str)
        start_date_elem.click()
    except Exception as e:
        pass

def get_lecturer_classes(WEB_DRIVER):
    go_to_schedule_start(WEB_DRIVER)
    lecturer_classes = dict()
    # Iterate through all days in semester
    expected_schedule_end_date = datetime.datetime(2025, 5, 31)
    while True:
        try:
            classes = get_day_classes(WEB_DRIVER)
            day_date = get_day_date(WEB_DRIVER)
            day_date_datetime = datetime.datetime.strptime(day_date, '%Y-%m-%d')
            if day_date_datetime > expected_schedule_end_date:
                break
            get_schedule_next(WEB_DRIVER)
            lecturer_classes[day_date] = classes
        except Exception as e:
            pass
    return lecturer_classes
