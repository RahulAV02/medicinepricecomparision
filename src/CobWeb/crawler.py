from flask import Flask, render_template, request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import asyncio
import aiohttp

app = Flask(__name__)

class Scraper:

    def __init__(self, base_urls):
        self.base_urls = base_urls

    async def __parse_netmeds(self, session, medicine_name):
        url = f"{self.base_urls['netmeds']}/{medicine_name.strip()}"  # Sanitize the medicine name
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            price_tag = soup.find("span", class_="final-price")
            if price_tag:
                price = price_tag.text.strip()
                return price
            else:
                return "Price not available"

    async def __parse_pharmeasy(self, session, medicine_name):
        url = f"{self.base_urls['pharmeasy']}{medicine_name.strip()}"  # Sanitize the medicine name
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            price_tag = soup.find("div", class_="PriceInfo_ourPrice__jFYXr")
            if price_tag:
                price = price_tag.text.strip()
                return price
            else:
                return "Price not available"

    async def scrape_price(self, pharmacy, medicine_name):
        async with aiohttp.ClientSession() as session:
            if pharmacy == "netmeds":
                price = await self.__parse_netmeds(session, medicine_name)
            elif pharmacy == "pharmeasy":
                price = await self.__parse_pharmeasy(session, medicine_name)
            else:
                price = "Invalid pharmacy"
            return price

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pharmacy = request.form.get("pharmacy")
        medicine_name = request.form.get("medicine_name")
        
        scraper = Scraper({
            "netmeds": "https://www.netmeds.com/prescriptions/",
            "pharmeasy": "https://pharmeasy.in/online-medicine-order/"
        })

        if pharmacy and medicine_name:
            price = asyncio.run(scraper.scrape_price(pharmacy, medicine_name))
            return render_template("index.html", price=price, medicine_name=medicine_name)
    
    return render_template("index.html", price=None, medicine_name=None)

if __name__ == "__main__":
    app.run(debug=True)
