import json
import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://en.wikipedia.org/wiki/Django_Reinhardt"

logging.basicConfig(
    filename='wikipedia_example.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logging.info("START CRAWLER")

logging.info("Launch Driver..")
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
logging.info(f"Get to: {TARGET_URL}")
driver.get(TARGET_URL)

xpath = '//h2[contains(text(),"References")]'
for _ in range(30):
    if driver.find_elements("xpath", xpath):
        break
    time.sleep(2)
else:
    raise Exception(f"Could not load: {xpath}")

logging.info(f"Element <{xpath}> loaded")


result_dict = {}
title_xp = '//h1[@id="firstHeading"]/span'
imgs_xp = '//a[contains(@href,"/wiki/File")]'
cites_xp = '//ol/li[contains(@id,"cite_note")]//cite'
table_rows_xp = '//div[@id="mw-content-text"]/div/table/tbody[1]/tr/th[@scope]'

logging.info(f"Find basic info")
el = driver.find_element("xpath", title_xp)
result_dict["title"] = el.text
els = driver.find_elements("xpath", table_rows_xp)
for el in els:
    label = el.text
    td_el = el.find_element("xpath", '../td')
    value = td_el.get_attribute("innerText")
    result_dict[label] = value

logging.info(f"Find images")
els = driver.find_elements("xpath", imgs_xp)
img_list = [el.get_attribute("href") for el in els]
logging.info(f"Images found: %s" % len(img_list))
result_dict["imgs"] = img_list

logging.info(f"Find cites")
els = driver.find_elements("xpath", cites_xp)
cite_list = []
for el in els:
    cite = el.get_attribute("innerText")
    anchor_els = el.find_elements("xpath", './/a')
    links = [el.get_attribute("href") for el in anchor_els]
    cite_list.append(
        {"cite": cite, "links": links}
    )

logging.info(f"Cites found: %s" % len(cite_list))
result_dict["cites"] = cite_list


driver.quit()
logging.info(f"driver.quit()")

json_str = json.dumps(result_dict, ensure_ascii=False)
OUTPUT_PATH = "output_dir/Django_Reinhardt_wiki.json"

with open(OUTPUT_PATH, "w") as file:
    file.write(json_str)
logging.info(f"File {OUTPUT_PATH} is saved")

logging.debug("END CRAWLER")
