import smtplib
import getpass
import ssl
from time import sleep
import requests
from bs4 import BeautifulSoup

"""
Python script that checks the stock on AMD website and sends a mail when new products are in stock.
Uses BeautifulSoup for webscraping and smtplib for sending emails
"""

#Returns the content of the webpage given by url in html form
def get_page_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36"}
    page = requests.get(url, headers=headers)
    return page.content


def get_items_in_stock(url):
    page_html = get_page_html(url)
    soup = BeautifulSoup(page_html, 'html.parser')
    products = soup.findAll("div", {"class": "shop-links"})
    stock_status = list()

    for elem in products:
        stock_status.append(elem.get_text().strip())
    current_stock = list()
    for product in stock_status:
        if product != 'Out of Stock':
            try:
                current_stock.append(product.split('\n')[1].strip())
            except Exception:
                current_stock.append(product)
    print("Current stock:" + str(current_stock))
    return current_stock


def send_mail(sender_email, password, receiver_email, message):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
    except Exception as e:
        # Print any error messages to stdout
        print(e)


def stock_checker(url, refresh_rate, sender_email, password, receiver_email):
    previous_stock = get_items_in_stock(url)
    # Testing:
    # send_mail("Stock changed!")
    while True:
        current_stock = get_items_in_stock(url)
        if len(current_stock) > len(previous_stock):
            send_mail(sender_email, password, receiver_email, "New Products Available!")
        else:
            print("Same stock!")
        previous_stock = current_stock
        sleep(refresh_rate)


if __name__ == "__main__":
    sender = input("Sender email:")
    pw = getpass.getpass("Password:")
    receiver = input("Receiver email: ")
    try:
        refresh = int(input("Website refresh rate: "))
    except ValueError:
        print("Invalid refresh rate!")
        exit(1)
    website_url = "https://www.amd.com/en/direct-buy/ro"
    stock_checker(website_url, refresh, sender, pw, receiver)
