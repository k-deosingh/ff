import re
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import date, timedelta

mydb = mysql.connector.connect(
  host="167-99-56-221.cprapid.com",
  #host="localhost",
  user="tavishop_forex",
  password="Doubles1000",
  database="forexfactory"
)

query = mydb.cursor()
query.execute("SELECT date FROM news")
result = query.fetchall()
list = []

for res in result:
   list.append(res[0])

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2023, 9, 1)
end_date = date.today()  + timedelta(days=1)
for each in daterange(start_date, end_date):

   this_date = each.strftime("%b%d.%Y")

   if this_date in list:
      continue
   else:

      print("\n"+this_date)
      quote_page = "https://www.forexfactory.com/calendar?day="+this_date
      hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
      page = requests.get(quote_page, headers=hdr).content

      def remove_html_tags(text):
         clean = re.compile('<.*?>')
         return re.sub(clean, '', text)

      # Create a BeautifulSoup object
      soup = BeautifulSoup(page, 'html.parser')

      current_time = None

      # Find all rows with the specified criteria
      rows = soup.find_all('tr', class_='calendar__row')

      # Iterate through the rows and extract the desired information
      for row in rows:
         time_cell = row.find('td', class_='calendar__time')
         time_cell_2 = remove_html_tags(str(time_cell))

         if time_cell_2:
            current_time = time_cell_2

         currency_cell = row.find('td', class_='calendar__currency')
         impact_cell = row.find('td', class_='calendar__impact')

         if currency_cell and impact_cell:
            currency = currency_cell.text.strip()
            impact = impact_cell.find('span', class_='icon').get('class')[1]

            if currency == 'USD' and (impact == 'icon--ff-impact-red' or impact == 'icon--ff-impact-ora'):
                  event_name = row.find('span', class_='calendar__event-title').text.strip()
                  time = row.find('td', class_='calendar__time').text.strip()
                  color = ""

                  if(impact == 'icon--ff-impact-red'):
                     color = "RED"
                  elif(impact == 'icon--ff-impact-ora'):
                     color = "ORANGE"

                  # Insert into Database
                  mycursor = mydb.cursor()
                  sql = "INSERT INTO news (date, time, currency, title, color) VALUES (%s, %s, %s, %s, %s)"
                  val = (this_date, current_time, "USD", event_name, color)
                  mycursor.execute(sql, val)
                  mydb.commit()

                  print(f"Time: {current_time}, Name: {event_name}, Color: {color}")