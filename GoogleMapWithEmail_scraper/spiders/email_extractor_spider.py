import re
import csv
import scrapy
from scrapy.linkextractors import LinkExtractor
import os
import glob
from datetime import datetime

class EmailExtractorSpiderSpider(scrapy.Spider):
    name = "email_spider"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_URI': f'final_output/cleaned_emails_output{datetime.now().strftime("Date %Y_%m_%d Time %Hh_%Mm")}.csv',
        'ROBOTSTXT_OBEY': False,
        'RETRY_TIMES': 3,
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, *args, **kwargs):
        super(EmailExtractorSpiderSpider, self).__init__(*args, **kwargs)
        self.output_dir = 'output/'
        self.input_file_path = self.get_latest_csv()
        if self.input_file_path:
            self.logger.info(f"Successfully found latest input file: {self.input_file_path}")
        else:
            self.logger.error("No CSV files found in the output directory!")

    def get_latest_csv(self):
        print('AAAAAAA')
        search_pattern = os.path.join(self.output_dir, "*.csv")
        print(search_pattern)
        files = glob.glob(search_pattern)
        print(files)
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    def start_requests(self):
        with open(self.input_file_path, 'r', encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for record in reader:
                if not record.get('email'):
                    raw_website = record.get('website', '').strip()
                    if not raw_website:
                        continue

                    clean_domain = re.sub(r'^https?://', '', raw_website).replace('http//', '')
                    target_url = f"https://{clean_domain}"

                    yield scrapy.Request(
                        url=target_url,
                        callback=self.parse_site,
                        meta={
                            'record': record,
                            'emails': set(),
                            'link_stack': [],
                            'visited_home': False
                        },
                        errback=self.handle_error
                    )
                else:
                    yield record

    def parse_site(self, response):
        meta = response.meta
        record = meta['record']
        emails = meta['emails']
        emails.update(self.extract_emails(response))
        if not meta['visited_home']:
            meta['visited_home'] = True

            le = LinkExtractor(
                allow=('.*about.*', '.*contact.*', '.*info.*', '.*privacy.*', '.*impressum.*', '.*get-in-touch.*'),
                unique=True,
                canonicalize=True
            )
            domain = response.url.split('/')[2]
            found_links = []

            for link in le.extract_links(response):
                if domain in link.url:
                    clean_link = link.url.split('#')[0].rstrip('/')
                    if clean_link != response.url.rstrip('/') and clean_link not in found_links:
                        found_links.append(clean_link)

            meta['link_stack'] = found_links[:3]

        if meta['link_stack']:
            next_url = meta['link_stack'].pop(0)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_site,
                meta=meta,
                errback=self.handle_error
            )
        else:
            yield self.finalize_record(record, emails)

    def extract_emails(self, response):
        mailto_links = response.xpath("//a[contains(@href, 'mailto:')]/@href").getall()
        extracted = [m.replace('mailto:', '').split('?')[0].lower() for m in mailto_links]

        text_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}', response.text)
        extracted.extend(text_emails)

        clean_set = set()
        blacklist = [
            'your@email', 'email@email', 'example@', 'domain.com',
            'yourname', 'test@', 'support@yoursite', 'info@template',
            'wix', 'sentry', 'lodash', 'react', 'polyfill', 'template'
        ]

        for email in extracted:
            email = email.lower().strip().strip('.,')
            if not any(word in email for word in blacklist):
                if '.' in email.split('@')[-1] and len(email) > 7:
                    clean_set.add(email)
        return clean_set

    def finalize_record(self, record, emails):
        record['email'] = ', '.join(list(emails))
        return record

    def handle_error(self, failure):
        meta = failure.request.meta
        if meta.get('link_stack'):
            next_url = meta['link_stack'].pop(0)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_site,
                meta=meta,
                errback=self.handle_error
            )
        else:
            yield self.finalize_record(meta['record'], meta['emails'])
