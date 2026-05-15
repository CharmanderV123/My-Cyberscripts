from bs4 import BeautifulSoup
import requests, requests.exceptions, urllib.parse, re, csv, email_scraper_fn
from collections import deque

# Prompt scan level for CSV-driven runs
level = input('[c:] Select scan level for CSV run (1 = site-only, 2 = deep scan) [1/2]: ').strip()
if level not in ('1', '2'):
    level = '2'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Max emails per site for CSV run (0 = no limit)
email_limit_input = input('[c:] Max emails per site (0 = no limit) [default 0]: ').strip()
try:
    email_limit = int(email_limit_input)
    if email_limit <= 0:
        email_limit = None
except:
    email_limit = None

with open('Sponsor Mastersheet - Sheet1.csv', 'r', newline='')as file:
    url_list=[]
    company_list=[]
    reader = csv.DictReader(file)
    row_count = 0
    for row in reader:
        row_count += 1
        if row['Website'] != '':
            # show processing line for each website
            print('[%d] Processing %s' % (row_count, row['Website']))
            # keep original behavior but pass level, headers and email_limit
            url_list.append(email_scraper_fn.email_scraper(row['Website'], level=level, headers=headers, email_limit=email_limit))
            company_list.append(row['Companies'])
        else:
            print('[%d] No website for %s' % (row_count, row.get('Companies','(unknown)')))
            url_list.append('No Website')
            company_list.append(row['Companies'])
    
    for i in range(len(url_list)):
        if ('wix' in url_list[i]):
            url_list[i] = 'Wix Website'
        print(f'{company_list[i]}: {url_list[i]}')

# target_url = str(input('[c:] Provide URL of Target to Scan: '))
# urls = deque([target_url])

# scraped_urls = set()
# emails = set()

# count = 0

# try:
    
#     while len(urls):
#         count+=1
       
#         if count == 100:
           
#             break
#         url= urls.popleft()
#         scraped_urls.add(url)

#         parts = urllib.parse.urlsplit(url)
#         base_url = '{0.scheme}://{0:netloc}'.format(parts)

#         path = url[:url.rfind('/')+1] if '/' in parts.path else url

#         print('[%d] Processing  %s' % (count, url))

#         try:
#             response = requests.get(url)
        
#         except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
           
#             continue

#         new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
#         emails.update(new_emails)

#         soup = BeautifulSoup(response.text, features="lxml")

#         for anchor in soup.find_all("a"):
#             link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            
#             if link.startswith('/'):
#                 link = base_url + link
           
#             elif not link.startswith('http'):
#                 link = path + link
           
#             if not link in urls and not link in scraped_urls:
#                 urls.append(link)

# except KeyboardInterrupt:
#     print('[:c] Closing!')

# for mail in emails:
#     print(mail)
