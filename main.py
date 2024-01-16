import base64
import os
import time
import jdatetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select


def get_base_path():
    # Determine the directory of the script (whether it's frozen or not)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # If frozen, adjust the script directory to the base directory
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(script_dir)

    return script_dir


path = get_base_path()

executable_path = f'{path}\\chromedriver\\chromedriver.exe'


def retrieve_data_from_the_txt():
    data_list = []
    with open(f'{path}\\#starting_list.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        addon_date = ''
        i = 0
        for line in lines:
            if i == 0:
                addon_date = line
            else:
                line = f'{line}|{addon_date}'
                line = line.replace('\n', '')
                line = line.split('|')
                try:
                    data_list.append(line)
                except:
                    pass
            i += 1
    return data_list


def scrap_data():
    folder_maker()
    options = Options()
    options.add_argument("--window-size=1920,1200")
    prefs = {"download.default_directory": f"{path}\\downloads"}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    driver.get("https://sso2.setadiran.ir/portal/login")
    time.sleep(45)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.TAG_NAME, 'label')))
    labels = driver.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        if str(label.text) == 'توسعه انرژی سپهر کاسپین':
            label.click()
            time.sleep(2)
            break
    labels = driver.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        if str(label.text) == 'خرید':
            label.click()
            time.sleep(2)
            break
    labels = driver.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        if str(label.text) == 'تامین کننده':
            label.click()
            time.sleep(2)
            break
    start_button = driver.find_element(By.ID, 'start-button')
    start_button.click()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'annoncement')))
    annoncement_iframe = driver.find_element(By.ID, 'annoncement')
    driver.switch_to.frame(annoncement_iframe)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'buttonDivision')))
    button_divisions = driver.find_elements(By.CLASS_NAME, 'buttonDivision')
    for button_division in button_divisions:
        if str(button_division.text) == 'جستجوی پیشرفته (Advanced Search)':
            advance_search_script = button_division.get_attribute('onclick')
            driver.execute_script(advance_search_script)
            break
    driver.switch_to.default_content()
    onclick_list = []
    for organization in retrieve_data_from_the_txt():
        or_name = organization[0]
        or_city = organization[1]
        or_date_from = organization[2]
        or_date_to = organization[3]
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'positive-btn')))
            positive_btn = driver.find_elements(By.CLASS_NAME, 'positive-btn')
            i = 0
            for item in positive_btn:
                print(f'{i} - {item.get_attribute("value")}')
                i += 1
                if str(item.get_attribute("value")) == '...':
                    item.click()
                    break
        except Exception as e:
            # print(str(e))
            pass
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'organizationSelectionFrame')))
            iframe = driver.find_element(By.ID, 'organizationSelectionFrame')
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'organizationName')))
            organization_name = driver.find_element(By.ID, 'organizationName')
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'organizationProvince')))
            organization_province = driver.find_element(By.ID, 'organizationProvince')
            organization_name.send_keys(or_name)
            province_dropdown = Select(organization_province)
            province_dropdown.select_by_visible_text(or_city)
            form_search_btn = driver.find_elements(By.CLASS_NAME, 'positive-btn')
            for item in form_search_btn:
                if str(item.get_attribute("value")) == 'جستجو':
                    item.click()
                    break
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'tblSelectOrganizationList')))
            result_select_organization_list_table = driver.find_element(By.ID, 'tblSelectOrganizationList')
            submit_pick = result_select_organization_list_table.find_elements(By.TAG_NAME, 'input')
            for item in submit_pick:
                try:
                    submit_pick_item_attribute = item.get_attribute('value')
                    if str(submit_pick_item_attribute) == 'انتخاب':
                        item.click()
                        break
                except:
                    pass
            time.sleep(1)
            driver.switch_to.default_content()
            radio_btn = driver.find_elements(By.ID, 'radioItems')
            for item in radio_btn:
                item.click()
                break
            # calender_date_from
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'needDateFrom')))
            driver.execute_script(f"document.getElementById('needDateFrom').removeAttribute('readonly',0);")
            driver.execute_script(f"document.getElementById('needDateFrom').value = '{or_date_from}';")
            # calendar_date_to
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'needDateTo')))
            driver.execute_script(f"document.getElementById('needDateTo').removeAttribute('readonly',0);")
            driver.execute_script(f"document.getElementById('needDateTo').value = '{or_date_to}';")
            time.sleep(1)
            try:
                captcha_image = driver.find_element(By.ID, 'stickyImgId')
                captcha_image_url = f'{captcha_image.get_attribute("src")}'
                print(captcha_image_url)
            except:
                pass
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'btnSerach')))
            advance_form_search_btn = driver.find_element(By.ID, 'btnSerach')
            advance_form_search_btn.click()
            time.sleep(1)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'needAdvancedSearchDisplayTableId')))
            needAdvancedSearchDisplayTableId = driver.find_element(By.ID, 'needAdvancedSearchDisplayTableId')
            result_table_details_item = needAdvancedSearchDisplayTableId.find_elements(By.TAG_NAME, 'a')
            for item in result_table_details_item:
                try:
                    # print(int(item.text))
                    onclick_list.append([organization, int(item.text), item.get_attribute('onclick')])
                except:
                    pass
            time.sleep(5)
        except Exception as e:
            # print(str(e))
            pass
    time.sleep(5)

    main_window_handle = driver.current_window_handle
    not_completed_list = []
    for onclick_href in onclick_list:
        try:
            purchase_need_dto = None
            purchase_organization_name = None
            deadline_duration_date_minus_1_day = None
            extra_docs_btn_script = None
            print_btn_script = None
            driver.execute_script(onclick_href[2])
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, 'form')))
            purchase_need_view_form = driver.find_element(By.TAG_NAME, 'form')
            purchase_need_view_form_inputs = purchase_need_view_form.find_elements(By.TAG_NAME, 'input')
            for purchase_need_view_form_input in purchase_need_view_form_inputs:
                try:
                    purchase_need_view_form_input_name = str(purchase_need_view_form_input.get_attribute('name'))
                    if purchase_need_view_form_input_name == 'purchaseNeedDto.needNo':
                        purchase_need_dto = purchase_need_view_form_input.get_attribute('value')
                        print(purchase_need_dto)
                    elif purchase_need_view_form_input_name == 'purchaseNeedDto.purchaseRequestDto.organization.name':
                        purchase_organization_name = purchase_need_view_form_input.get_attribute('value')
                        print(purchase_organization_name)
                    elif purchase_need_view_form_input_name == 'deadlineDurationDateStr':
                        deadline_duration_date = purchase_need_view_form_input.get_attribute('value')
                        deadline_duration_date = str(deadline_duration_date)
                        deadline_duration_date = deadline_duration_date.split('/')
                        deadline_duration_date = jdatetime.datetime(year=int(deadline_duration_date[0]),
                                                                    month=int(deadline_duration_date[1]),
                                                                    day=int(deadline_duration_date[2]))
                        deadline_duration_date_minus_1_day = deadline_duration_date - jdatetime.timedelta(days=1)
                        deadline_duration_date_minus_1_day = deadline_duration_date_minus_1_day.strftime('%Y-%m-%d')
                        print(deadline_duration_date_minus_1_day)
                except:
                    pass
                try:
                    purchase_need_view_form_input_on_click = str(purchase_need_view_form_input.get_attribute('onclick'))
                    if purchase_need_view_form_input_on_click == 'return anonymousShowAppendix()':
                        extra_docs_btn_script = purchase_need_view_form_input.get_attribute('onclick')
                    elif purchase_need_view_form_input_on_click == 'callPrint()':
                        print_btn_script = purchase_need_view_form_input.get_attribute('onclick')
                except:
                    pass
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'purchaseNeedDto.needName')))
            details_summary_textarea = purchase_need_view_form.find_element(By.ID, 'purchaseNeedDto.needName')
            details_summary = details_summary_textarea.text
            print(details_summary)
            folder_name = f'{purchase_organization_name}_{purchase_need_dto}_{deadline_duration_date_minus_1_day}'
            folder_path = f'{path}\\archive\\{folder_name}'
            try:
                os.mkdir(folder_path)
            except:
                pass
            screenshot_path = f'{folder_path}\\{purchase_need_dto}.jpg'
            driver.save_screenshot(screenshot_path)
            main_window_handle = driver.current_window_handle
            driver.execute_script(print_btn_script)
            try:
                wait = WebDriverWait(driver, 15)
                new_window_handle = None
                # Wait for the new window handle to be different from the main window handle
                wait.until(lambda driver: len(driver.window_handles) > 1)
                for handle in driver.window_handles:
                    if handle != main_window_handle:
                        new_window_handle = handle
                        break
                driver.switch_to.window(new_window_handle)
                params = {
                    'transferMode': 'ReturnAsBase64',
                    'paperWidth': 8.27,  # A4 width in inches
                    'paperHeight': 11.69,  # A4 height in inches
                    'marginTop': 0,
                    'marginBottom': 0,
                    'marginLeft': 0,
                    'marginRight': 0,
                    'printBackground': True,  # Ensure background colors and images are included
                    'preferCSSPageSize': True,  # Use the CSS page size when specified
                    'displayHeaderFooter': False,  # Disable header and footer
                    'emulateMedia': 'print',  # Emulate print media type for better compatibility
                    'headerTemplate': '',  # Customize header if needed
                    'footerTemplate': '',  # Customize footer if needed
                    'scale': 1,  # Adjust scale if needed
                }
                result = driver.execute_cdp_cmd('Page.printToPDF', params)
                pdf_content_base64 = result['data']
                pdf_content = base64.b64decode(pdf_content_base64)
                pdf_file_path = f'{folder_path}\\{purchase_need_dto}.pdf'
                with open(pdf_file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)
                time.sleep(1)
                driver.close()
                driver.switch_to.window(main_window_handle)
            except Exception as e:
                # print(str(e))
                pass

            driver.execute_script(extra_docs_btn_script)
            wait = WebDriverWait(driver, 10)
            new_window_handle = None
            wait.until(lambda driver: len(driver.window_handles) > 1)
            for handle in driver.window_handles:
                if handle != main_window_handle:
                    new_window_handle = handle
                    break
            driver.switch_to.window(new_window_handle)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'btnShowFile')))
            extra_docs_btn_show_file = driver.find_element(By.ID, 'btnShowFile')
            extra_docs_btn_show_file_script = extra_docs_btn_show_file.get_attribute('onclick')
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'mainContent')))
            extra_docs_main_content = driver.find_element(By.ID, 'mainContent')
            extra_docs_inputs = extra_docs_main_content.find_elements(By.TAG_NAME, 'input')
            doc_select_scripts = []
            for extra_docs_input in extra_docs_inputs:
                try:
                    extra_docs_input_on_click = extra_docs_input.get_attribute('onclick')
                    if str(extra_docs_input_on_click).find('select_item') != -1:
                        doc_select_scripts.append(extra_docs_input_on_click)
                except:
                    pass
            print(doc_select_scripts)
            for doc_select_script in doc_select_scripts:
                driver.execute_script(doc_select_script)
                time.sleep(1)
                driver.execute_script(extra_docs_btn_show_file_script)
            driver.close()
            driver.switch_to.window(main_window_handle)
            time.sleep(20)
            source_folder = f'{path}\\downloads'
            files_to_move = os.listdir(source_folder)
            for file_name in files_to_move:
                source_file_path = f'{source_folder}\\{file_name}'
                try:
                    os.replace(source_file_path, f"{folder_path}/{file_name}")
                    os.remove(source_file_path)
                except:
                    pass
        except:
            driver.switch_to.window(main_window_handle)
            source_folder = f'{path}\\downloads'
            files_to_move = os.listdir(source_folder)
            for file_name in files_to_move:
                source_file_path = f'{source_folder}\\{file_name}'
                try:
                    os.remove(source_file_path)
                except:
                    pass
            not_completed_list.append(onclick_href)
            print(f'problem happens during handling {onclick_href}')
            time.sleep(5)
        print('-------------')
    time.sleep(10)
    try:
        with open(f'{path}\\not-completed-list.txt', 'w') as not_completed_file:
            for file_name in not_completed_list:
                not_completed_file.write(f'{file_name}')
    except:
        pass
    driver.quit()


def folder_maker():
    try:
        os.mkdir(f'{path}\\archive')
    except:
        pass
    try:
        os.mkdir(f'{path}\\downloads')
    except:
        pass


try:
    while True:
        print('please choose a number')
        print('1. scrap data')
        number = input()
        try:
            number = int(number)
            if number == 1:
                if number == 1:
                    try:
                        scrap_data()
                    except Exception as e:
                        print(str(e))
            else:
                print('wrong choice. please try again.')
        except:
            print('wrong choice. please try again.')

except Exception as e:
    print(f'err: {str(e)}')
    input('Press Enter to exit')
