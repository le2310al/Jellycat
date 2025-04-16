import nodriver as nd
import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sqlite3
import os
from selenium.webdriver.support import expected_conditions as EC
import re
import random
import asyncio

async def new():

    browser = await nd.start()

    con = sqlite3.connect("stock_status.sqlite")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY , url TEXT NOT NULL, availability TEXT NOT NULL)")

    page = 1
    while page < 5:
        # print("Page: " + str(page))
        website = "https://jellycat.com/shop-all?page=" + str(page)
        print(website)
        page = await browser.get(website)
        try:
            cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(cookies))
            cookies.click()
        finally:
            list_items = driver.find_element(By.ID, "searchspring-content").find_elements(By.TAG_NAME, "article")
            for item in list_items:
                element = item.find_element(By.CLASS_NAME, "card-figure__link")
                name = str(element.get_attribute("aria-label")).replace("'", "").split(",", 1)[0]
                url = str(element.get_attribute("href"))
                try:
                    item.find_element(By.PARTIAL_LINK_TEXT, "Coming")
                    availability = "Coming Soon"
                except NoSuchElementException:
                    availability = "Available"
                print(name + url + availability)
                cur.execute(
                    "INSERT INTO items (id, url , availability) VALUES('" + name + "' ,'" + url + "' ,'" + availability + "') ON CONFLICT DO UPDATE SET availability = excluded.availability;")
                con.commit()
            next_page = driver.find_element(By.LINK_TEXT, "Next")
            next_page.click()
            driver.implicitly_wait(random.randint(10, 30))
        page += 1
    await page.close()

if __name__ == "__main__":
    asyncio.run(new())