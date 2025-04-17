import nodriver as nd
from nodriver import *
import sqlite3
import random

async def main():
    con = sqlite3.connect("stock_status.sqlite")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY , url TEXT NOT NULL, availability TEXT NOT NULL)")

    config = Config()
    config.headless = False
    config.user_data_dir = "./profile",

    driver = await nd.start(config)
    website = "https://jellycat.com/shop-all#/sort:ss_days_since_created:asc"
    tab = await driver.get(website)
    cookies = await (tab.find("Accept All Cookies", best_match=True))
    if cookies:
        await cookies.click()
    items = await tab.query_selector(".tw-mr-8")
    items_number = float(items.text) if items else 0
    page_number = round(items_number/36)
    page = 1
    for i in range(page_number):
        cookies = await (tab.find("Accept All Cookies", best_match=True))
        if cookies:
            await cookies.click()
        print("Page: " + str(page))
        #"""
        jellies = await tab.select_all(".product")
        #print(str(len(jellies)))
        for jelly in jellies:
            #print("LOOOP")
            card = await jelly.query_selector(".card-figure__link")
            #print("BOOP")
            if card:
                #print("CARD")
                try:
                    card.attributes.index("aria-label")
                finally:
                    #print("ARIA")
                    name = card.attrs["aria-label"].replace("'", "").split(",", 1)[0] if card else None
                    if name:
                        #print("NAME")
                        items_number -= 1
                        url = card.attrs["href"] if card else ""
                        button = await jelly.query_selector(".disabled")
                        availability = button.text if button else "Available"
                        #print(name + url + availability)
                        cur.execute(
                            "INSERT INTO items (id, url , availability) VALUES('" + name + "' ,'" + url + "' ,'" + availability + "') ON CONFLICT DO UPDATE SET availability = excluded.availability;")
                        con.commit()
        #next_button = await (tab.find("Next", best_match=True))
        """
        await tab.sleep(random.randint(2, 7))
        if random.randint(0, 1) == 1:
            await tab.sleep(random.randint(1, 4))
        """
        await tab.sleep(60)
        page += 1
        website = "https://jellycat.com/shop-all?page="+str(page)+"#/sort:ss_days_since_created:asc"
        tab = await driver.get(website)
        #await next_button.click()
    await tab.close()

if __name__ == "__main__":
    nd.loop().run_until_complete(main())