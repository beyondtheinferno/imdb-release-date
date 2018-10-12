from bs4 import BeautifulSoup
import requests
import re
import datetime
import smtplib
import email.message
import sqlite3

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# USER DEFINIED FUNCTIONS -

def text_in_tag(tag):
    string = tag.get_text()
    string = string.rstrip()
    string = string.lstrip()
    return string

def isValidEmail(email):
    if len(email) > 7:
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email) != None:
            return True
    return False

def saveSQL(email, shows, urls, d):
    conn = sqlite3.connect('data/userQueries')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Queries(Id INTEGER PRIMARY KEY,
MailID TEXT, Shows TEXT, BaseURLs STRING, Date DATE)''')
    conn.execute('''INSERT INTO Queries(MailID, Shows, BaseURLs, Date)
values (?,?,?,?)''', (email, shows, urls, d))
    print("Successfully updated USER QUERIES in SQLITE3 DB!!")
    conn.commit()
    conn.close()

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# USER INPUT -

# INPUT MAIL ID
while(True):
    to_email_id = input("Enter your email id: ")
    if isValidEmail(to_email_id) == True:
        break
    else:
        print("You've entered a wrong email id!! Please enter the right one!")

# INPUT TV SHOWS
tv_show = input("Enter the name of TV Shows (separated by commas) -> ")
tv_shows = tv_show.split(',')
for i in range(len(tv_shows)):
    tv_shows[i] = tv_shows[i].lstrip()
    tv_shows[i] = tv_shows[i].rstrip()
    tv_shows[i] = tv_shows[i].lower()
    tv_shows[i] = tv_shows[i].replace(' ', '+')

# SEARCH IMDb FOR THE TV SHOW TITLES AND RETURN A LIST OF DICTIONARY CONTAINING
# THE POSSIBLE HITS FOR THAT SEARCH RESULT
master_list = []
for x in tv_shows:
    link = 'https://www.imdb.com/find?q={}&s=all'.format(x)
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='findList')
    table_data = table.find_all('td', class_='result_text')
    show_links = {}
    for i in range(len(table_data)):
        title = table_data[i].get_text()
        a = table_data[i].find('a')
        title_link = a['href'][:17]
        show_links[i+1] = [title, title_link]
    master_list.append(show_links)

# ASK THE USER TO SELECT THE SHOW FROM THE LIST AND STORE THE IMDb ID OF
# EACH SHOW IN base_urls list
base_urls = []
for x in master_list:
    print("\nThe options available are - \n" , x , "\n")
    choice = int(input("Which one do you select? Give the index value: "))
    base_urls.append(x[choice][1])
    print()
# print(base_urls)

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# IMDb SCRAPING AND PROCESSING -

body = []

for url in base_urls:
    response = requests.get('https://www.imdb.com'+url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # TITLE
    div12 = soup.find('div', class_='title_wrapper')
    h1 = div12.find('h1')
    title = text_in_tag(h1)
    print("TV SHOW -> ", title)

    # IMAGE URL
    div123 = soup.find('div', class_='poster')
    image_tag = div123.find('img')
    image = image_tag['src']
    print('Image URL -> ', image)

    # STORY
    div = soup.find_all('div', id='titleStoryLine')[0]
    temp = div.find('div', class_='inline canwrap')
    temp = temp.find('span')
    story = text_in_tag(temp)
    print('\nStory ->', story)

    # GENRES
    temp2 = div.find('div', class_='see-more inline canwrap')
    temp2 = temp2.find_all('a')
    genre = []
    for x in temp2:
        g = text_in_tag(x)
        if g.lower().startswith('see all'):
            break
        genre.append(g)
    print("\nGenre -> ", genre)

    # LATEST SEASON NUMBER AND LINK
    div = soup.find_all('div', class_='seasons-and-year-nav')[0]
    a_list = div.find_all('a')
    latest_season = a_list[0].get_text()
    latest_season_link = a_list[0]['href']
    print("Latest season -> ",latest_season)
    # print("Link -> ", latest_season_link)

    # WE SCRAPE THE LATEST SEASON PAGE
    episodes_url = 'https://www.imdb.com' + latest_season_link
    response2 = requests.get(episodes_url)
    soup2 = BeautifulSoup(response2.content, 'html.parser')
    #print(soup2.prettify())

    div = soup2.find_all('div', class_='airdate')

    # TODAY'S DATE
    current_date = datetime.datetime.now().date()
    #print("Today's date = ", current_date)
    c_date = datetime.datetime.strftime(current_date, "%d %B %Y")
    #print("Today's date = ", c_date)
    print()

    # INDEXING MONTHS
    short = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'Jun.', 'May', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
    long = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    release_dates = {}

    for i,x in enumerate(div):
        # Episode number
        #print('e{}'.format(i+1))
        date_string = text_in_tag(x)

        # Convert short form of months to full expansion, as string
        for y in short:
            if y in date_string:
                date_string = date_string.replace(y, long[short.index(y)])
        #print('Release Date -> ', date_string)

        # Setting high values initially so that if none of the conditions in this
        # loop modify this variable, it doesn't enter the condition outside the loop too
        date = 40
        month = 13
        year = 10000

        # DATES IN IMDb ARE NOT MENTIONED
        if len(date_string) == 0:
            message = 'Air Date yet to be decided!'
            print(message)
            break

        # MM/YY
        elif date_string[0].isalpha():
            date_string = datetime.datetime.strptime(date_string, "%B %Y")
            month = date_string.month
            year = date_string.year

            # AIRS ON THIS MONTH
            if(month == current_date.month) and (year == current_date.year):
                message = 'The next episode/season airs this month, ' + long[month-1] + ' ' + str(year)
                print(message)
                break

            # AIRS ON MONTH AFTER THIS MONTH
            elif(month > current_date.month) and (year >= current_date.year):
                message = 'The next episode/season airs on ' + long[month-1] + ' ' + str(year)
                print(message)
                break

        # DD/MM/YY
        elif date_string[3].isalpha():
            date_string = datetime.datetime.strptime(date_string, "%d %B %Y")
            date = date_string.day
            month = date_string.month
            year = date_string.year

            # AIRS TODAY
            if(date == current_date.day) and (month == current_date.month) and (year == current_date.year):
                message = 'The episode/season airs today!! -> ' + str(date) + 'th ' + long[month-1] + ' ' + str(year)
                print(message)
                break

            # AIRS IN FUTURE WHERE dates > current date
            elif (date > current_date.day) and (month >= current_date.month) and (year >= current_date.year):
                message = 'The next episode/season airs on -> ' + str(date) + 'th ' + long[month-1] + ' ' + str(year)
                print(message)
                break

            # AIRS IN FUTURE WHERE dates < current date, but month > current month
            elif (date <= current_date.day) and (month > current_date.month) and (year >= current_date.year):
                message = 'The next episode/season airs on -> ' + str(date) + 'th ' + long[month-1] + ' ' + str(year)
                print(message)
                break

        # YY
        else:
            date_string = datetime.datetime.strptime(date_string, "%Y")
            year = date_string.year
            
            # SAME YEAR
            if year == current_date.year:
                message = "The next episode/season begins this year i.e. {}!".format(str(year))
                print(message)
                break

            # UPCOMING YEARS
            if year > current_date.year:
                message = "The next episode/season begins in {}!".format(str(year))
                print(message)
                break

    if (year < current_date.year) or (month < current_date.month and year <= current_date.year) or (date < current_date.day and month == current_date.month and year == current_date.year):
        message = "The show has finished streaming all its episodes!"
        print(message)

    email_content_image = """<tr>
              <td width="180" valign="top" bgcolor="d0d0d0" style="padding:5px;">
              <img src=\"""" + image + """\" width="182" height="286"/>
              </td>
              <td width="15"></td>
              <td valign="top">"""
    email_content_title = """<h5>""" + title + """</h5>"""
    # email_content_story = """<p><b>STORY -> </b>""" + story + """</p><br>"""
    email_content_season = """<p><b>SEASON -> </b>""" + latest_season + """</p><br>"""
    email_content_message = """<p><em>""" + message + """</em></p></td></tr>"""
    series_content = email_content_image + email_content_title + email_content_season + email_content_message
    body.append(series_content)

    print("\n\n")

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# EMAIL PART -

email_content_top = """
<html>
<head>
    
   <title>TV Show release dates</title>
   <style type="text/css">
    a {color: #d80a3e;}
  body, #header h1, #header h2, p {margin: 0; padding: 0;}
  #main {border: 1px solid #cfcece;}
  img {display: block;}
  #top-message p, #bottom p {color: #3f4042; font-size: 12px; font-family: Arial, Helvetica, sans-serif; }
  #header h1 {color: #ffffff !important; font-family: "Lucida Grande", sans-serif; font-size: 24px; margin-bottom: 0!important; padding-bottom: 0; }
  #header p {color: #ffffff !important; font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; font-size: 12px;  }
  h5 {margin: 0 0 0.8em 0;}
    h5 {font-size: 18px; color: #444444 !important; font-family: Arial, Helvetica, sans-serif; }
  p {font-size: 12px; color: #444444 !important; font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; line-height: 1.5;}
   </style>
</head>
<body>
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="e4e4e4"><tr><td>
<table id="top-message" cellpadding="20" cellspacing="0" width="600" align="center">
    <tr>
      <td align="center">
        <p><a href="#">View in Browser</a></p>
      </td>
    </tr>
  </table>
 
<table id="main" width="600" align="center" cellpadding="0" cellspacing="15" bgcolor="ffffff">
    <tr>
      <td>
        <table id="header" cellpadding="10" cellspacing="0" align="center" bgcolor="8fb3e9">
          <tr>
            <td width="570" align="center"  bgcolor="#d80a3e"><h1>TV Show release dates</h1></td>
          </tr>
        </table>
      </td>
    </tr>
    
    
    
    <tr>
      <td>
        <table id="content-3" cellpadding="0" cellspacing="0" align="left">"""

email_content_end = """</table></td></table>
  <table id="bottom" cellpadding="20" cellspacing="0" width="600" align="center">
    <tr>
      <td>
      </td>
    </tr>
  </table>
</td>
</tr>
</table> 
</body>
</html>"""

# CREATE THE HTML PAGE TO BE SENT VIA EMAIL
email_content = email_content_top 
for x in body:
    email_content += x
email_content += email_content_end

# INSTANCE OF MESSAGE - enter the password of the 'FROM' email in the 'password' variable
server = smtplib.SMTP('smtp.gmail.com:587')
msg = email.message.Message()
msg['Subject'] = '[SCRIPT] Release Dates are here!'
msg['From'] = ''
msg['To'] = to_email_id
password = ''

# SETTING UP THE PAYLOAD AND STARTING THE SERVICE
msg.add_header('Content-Type', 'text/html')
msg.set_payload(email_content)
s = smtplib.SMTP('smtp.gmail.com: 587')
s.starttls()

# LOGIN USING THE CREDENTIALS
s.login(msg['From'], password)
s.sendmail(msg['From'], [msg['To']], msg.as_string())

# SAVE INPUT DETAILS IN SQL
url = ', '.join(base_urls)
saveSQL(to_email_id, tv_show, url, current_date)
