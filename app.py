from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
from urllib.request import urlopen
import smtplib
import config


class BikeScraper:
    def __init__(self, location, category_code, keyword):
        self.location = location
        self.keyword = keyword
        self.category_code = category_code
        self.url = "https://" + location + ".craigslist.org/search/"+ category_code +"?query=" + keyword
        self.driver = webdriver.Chrome('/Users/tlueders/Desktop/chromedriver')
        self.delay = 3

    def load_url(self):
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, self.delay)
            wait.until(EC.presence_of_element_located((By.ID, "searchform")))
        except TimeoutException:
            print("Timed Out")

    def extract_data(self):
        all_posts = self.driver.find_elements_by_class_name("result-row")

        dates = []
        titles = []
        prices = []

        for post in all_posts:
            title = post.text.split("$")

            if title[0] == '':
                title = title[1]
            else:
                title = title[0]

            title = title.split("\n")
            price = title[0]
            title = title[-1]

            title = title.split(" ")

            month = title[0]
            day = title[1]
            title = ' '.join(title[2:])
            date = month + " " + day

            titles.append(title)
            prices.append(price)
            dates.append(date)
        return titles, prices, dates

    def extract_urls(self):
        url_list = []
        html_page = urlopen(self.url)
        soup = BeautifulSoup(html_page, "html.parser")
        for link in soup.findAll("a", {"class": "result-title"}):
            url_list.append(link["href"])
        return url_list

    def quit(self):
        self.driver.close()

    def send_email(self, subject, msg):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(config.EMAIL_ADDRESS, config.PASSWORD)
            message = "Subject: {}\n\n{}".format(subject, msg)
            server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, message)
            server.quit()
            print("Success: Email sent.")
        except:
            print('Failed: Email was not sent.')

    def create_message(self):
        titles, prices, dates = self.extract_data()
        url_list = self.extract_urls()
        posts = []
        for title, price, date, url in zip(titles, prices, dates, url_list):
            post = "Price: " + price, "Title: " + title, "Date: " + date, "URL: " + url
            posts.append(post)
            print("{} \n".format(post))
        return posts


# Initialize Scraper
scraper = BikeScraper("bend", "bia", "specialized")
scraper.load_url()

# Create & Send Message
# subject = "Daily Craigslist Updates"
msg = scraper.create_message()
print(msg)
# scraper.send_email(subject, msg)

# Close Scraper
scraper.quit()