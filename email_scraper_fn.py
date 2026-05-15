from bs4 import BeautifulSoup
import requests, requests.exceptions, urllib.parse, re
from collections import deque

def email_scraper(data, level='2', headers=None, timeout=15, email_limit=None):
    """Crawl a single target URL and return a list of discovered email addresses.

    Parameters:
    - data: target URL (string)
    - level: '1' restricts crawl to the same domain, '2' follows external links
    - headers: optional dict of headers to send with requests
    - timeout: request timeout in seconds
    - email_limit: maximum number of emails to return for this target (None = no limit)

    Backwards-compatible: callers that pass only the URL will get previous behavior.
    """
    url_list = []
    filter = ['info','contact','support','help','admin','sales','enquiries','enquiry','contactus','contact-us','contactus','contact_us','mail','email']
    urls = deque([data])

    scraped_urls = set()
    emails = set()

    count = 0

    # per-run discovered emails (preserve order) for enforcing email_limit
    found_list = []
    found_set = set()

    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    initial_netloc = urllib.parse.urlsplit(data).netloc

    try:
        while len(urls):
            count += 1

            if count == 100:
                break

            url = urls.popleft()
            print('[%d] Processing  %s' % (count, url))
            scraped_urls.add(url)

            parts = urllib.parse.urlsplit(url)
            try:
                base_url = '{0.scheme}://{0.netloc}'.format(parts)
            except:
                continue

            path = url[:url.rfind('/')+1] if '/' in parts.path else url


            try:
                response = requests.get(url, headers=headers, timeout=timeout)

            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                continue

            # skip non-text responses
            if not response.headers.get('content-type','').lower().startswith('text'):
                continue

            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))

            # collect discovered emails (preserve order)
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

            # if limit reached, stop crawling this target
            if email_limit and len(found_list) >= email_limit:
                break

            soup = BeautifulSoup(response.text, features="lxml")

            for anchor in soup.find_all("a"):
                link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                if not isinstance(link, str):
                    continue

                # ignore mailto and javascript links
                if link.startswith('mailto:') or link.startswith('javascript:'):
                    continue

                if link.startswith('/'):
                    link = base_url + link

                elif not link.startswith('http'):
                    link = path + link

                # strip fragment
                link = link.split('#')[0]

                # if level 1, restrict to initial domain
                parsed_link = urllib.parse.urlsplit(link)
                if level == '1' and parsed_link.netloc and parsed_link.netloc != initial_netloc:
                    continue

                if not link in urls and not link in scraped_urls:
                    urls.append(link)

    except KeyboardInterrupt:
        return('[:c] Closing!')

    for mail in emails:
        if (mail.split('@')[0] in filter):
            pass
        else:
            url_list.append(str(mail))
    return(url_list)
