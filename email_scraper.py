from bs4 import BeautifulSoup
import requests, requests.exceptions, urllib.parse, re
from collections import deque

target_url = str(input('[c:] Provide URL of Target to Scan: '))

# Scan level: 1 = site-only (same domain), 2 = deep scan (follow external links)
level = input('[c:] Select scan level (1 = site-only, 2 = deep scan) [1/2]: ').strip()
if level not in ('1', '2'):
    level = '2'

# Max emails per site (0 = no limit)
email_limit_input = input('[c:] Max emails per site (0 = no limit) [default 0]: ').strip()
try:
    email_limit = int(email_limit_input)
    if email_limit <= 0:
        email_limit = None
except:
    email_limit = None

initial_netloc = urllib.parse.urlsplit(target_url).netloc


urls = deque([target_url])

scraped_urls = set()
emails = set()

# per-run collected (filtered) emails and helpers
found_list = []
found_set = set()

count = 0

# simple filter for common generic inboxes (mirror of function version)
filter = ['info','contact','support','help','admin','sales','enquiries','enquiry','contactus','contact-us','contactus','contact_us','mail','email']

try:
    
    while len(urls):
        count+=1
       
        if count == 100:
           
            break
        url= urls.popleft()
        scraped_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)

        path = url[:url.rfind('/')+1] if '/' in parts.path else url

        print('[%d] Processing  %s' % (count, url))

        try:
            # Send common browser headers to avoid ModSecurity / 406 responses
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=15)

        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        # add discovered emails (preserve discovery order in found_list)
        for mail in new_emails:
            if mail in found_set:
                continue
            if (mail.split('@')[0] in filter):
                continue
            found_set.add(mail)
            found_list.append(mail)
            emails.add(mail)
            if email_limit and len(found_list) >= email_limit:
                break
        # if limit reached, stop crawling
        if email_limit and len(found_list) >= email_limit:
            break

        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            href = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            link = href if isinstance(href, str) else ''
            # ignore mailto and javascript links
            if link.startswith('mailto:') or link.startswith('javascript:'):
                continue

            if link.startswith('/'):
                link = base_url + link
           
            elif not link.startswith('http'):
                link = path + link
           
            # strip fragments
            link = link.split('#')[0]

            # If level 1, restrict to the initial target's domain
            parsed_link = urllib.parse.urlsplit(link)
            if level == '1' and parsed_link.netloc and parsed_link.netloc != initial_netloc:
                continue

            if not link in urls and not link in scraped_urls:
                urls.append(link)

except KeyboardInterrupt:
    print('[:c] Closing!')

if found_list:
    for mail in found_list:
        print(mail)
else:
    for mail in emails:
        print(mail)
