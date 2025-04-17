""""
Clicking the next badge as opposed to using the URL to navigate to the next page
caused 'query_selector' to not detect all items on the page past page 2.
"""

#import sqlite3
import psycopg2
import nodriver as nd
from nodriver import *
import random

# Accept cookies; possibly aids remaining undetected
async def accept_cookies(tab):
    cookies = await (tab.query_selector("#onetrust-accept-btn-handler"))
    if cookies:
        await cookies.click()
    popup = await tab.query_selector(".go3588653706")
    if popup:
        await popup.click()


async def main():
    # Connect to PostgreSQL database
    con = psycopg2.connect("dbname=stockStatus user=postgres")

    # Create a SQLite database
    #con = sqlite3.connect("stock_status.sqlite")

    cur = con.cursor()
    #cur.execute("CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY , url TEXT NOT NULL, availability TEXT NOT NULL)")

    # Create persistent nodriver config; possibly aids remaining undetected
    config = Config()
    config.headless = False
    config.user_data_dir = "./profile",

    # Initiate nodriver
    browser = await nd.start(config)
    website = "https://jellycat.com/shop-all#/sort:ss_days_since_created:asc"
    tab = await browser.get(website)
    await tab.sleep(5)
    await tab.get_content()
    await accept_cookies(tab)
    await browser.cookies.save()

    # Calculate number of pages based on total number of items; assumes 3x12 grid
    total_products_str = await tab.query_selector(".tw-mr-8")
    total_products_float = float(total_products_str.text) if total_products_str else 0
    total_pages = round(total_products_float/36)
    current_page = 1

    # Loop through all pages
    for i in range(total_pages):
        products = await tab.select_all(".product")
        #print("PAGE " + str(current_page) + "ITEMS " + str(len(products)))
        for product in products:
            # Commit new product to database or update availability
            try:
                product_card = await product.query_selector(".card-figure__link")
                #Strips price from product name
                name = product_card.attrs["aria-label"].replace("'", "").split(",", 1)[0]
                url = product_card.attrs["href"]
                badge = await product.query_selector(".ss__badge")
                availability = badge.text if badge else "Available"
                cur.execute(
                    "INSERT INTO products (id, url , availability) "
                    +"VALUES('" + name + "' ,'" + url + "' ,'" + availability + "') "
                    +"ON CONFLICT (id) DO UPDATE SET availability = EXCLUDED.availability;"
                )
                con.commit()
            except:
                print("                                                         ERROR")
        # Delay loading next page
        await tab.sleep(random.randint(2, 7))
        if random.randint(0, 1) == 1:
            await tab.sleep(random.randint(1, 4))
        current_page += 1
        website = "https://jellycat.com/shop-all?page="+str(current_page)+"#/sort:ss_days_since_created:asc"
        tab = await browser.get(website)
        await browser.cookies.load()
        await tab.sleep(3)
        await tab.get_content()
    await tab.close()

if __name__ == "__main__":
    nd.loop().run_until_complete(main())