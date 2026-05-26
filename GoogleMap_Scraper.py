import csv
import os
import time
from datetime import datetime
import shutil
import zipfile
import pyexcel as pe
import scrapy
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class GoogleMapScraper:

    def __init__(self):
        self.base_url = 'https://www.google.com/maps/'
        self.current_timestamp = datetime.now().strftime("Date %Y_%m_%d Time %Hh_%Mm")
        self.records = []
        self.count = 0
        self.record_number = 0
        self.output_dir = 'output'
        self.input_file = 'input_files/input.csv'
        self.ext =  "input_files/Emails_ext.crx"
        self.extracted_folder =  "extracted_extension"

    def scrape_data(self):
        records = pe.get_records(file_name=self.input_file)
        current_directory = os.getcwd()
        crx_path = os.path.join(current_directory, self.ext)
        extracted_extension_path = os.path.abspath(
            os.path.join(current_directory, self.extracted_folder)
        )
        if not os.path.exists(extracted_extension_path) or not os.listdir(extracted_extension_path):

            if os.path.exists(crx_path):
                print(f"Extracting {crx_path} to {extracted_extension_path}...")

                # clean old broken extraction (optional but safe)
                if os.path.exists(extracted_extension_path):
                    shutil.rmtree(extracted_extension_path)

                os.makedirs(extracted_extension_path, exist_ok=True)

                with zipfile.ZipFile(crx_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_extension_path)

            else:
                raise FileNotFoundError(f"Could not find the CRX file at: {crx_path}")
        else:
            print("Extension already extracted. Skipping unzip step.")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=os.path.abspath("playwright_data"),
                channel="chromium",
                headless=False,
                no_viewport=True,
                args=[
                    f"--disable-extensions-except={extracted_extension_path}",
                    f"--load-extension={extracted_extension_path}",
                    "--start-maximized",
                    "--no-first-run",
                    "--no-default-browser-check"
                ],
            )

            # Use the auto-opened first page to avoid overlapping tabs
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(90000)
            try:

                for record in records:
                    search_keyword = record.get('keyword') or record.get('\ufeffkeyword')
                    business_type = record.get('business_type')
                    city = record.get('city', '')
                    state = record.get('state', '')
                    country = record.get('country', '')
                    query =  f'{search_keyword} {business_type }in {city}, {state}, {country}'
                    try:
                        if search_keyword:
                            self.record_number += 1
                            print(
                                f"Processing record: {query} ========> {self.record_number}"
                            )
                            page.goto(self.base_url)
                            search_box = page.wait_for_selector(
                                '//input[contains(@class,"UGojuc")]'
                            )
                            search_box.fill(query)
                            search_box.press("Enter")

                            self.wait_for_element(
                                page,
                                'div[role="main"] div[role="feed"]',
                                secondary_selector='//span/parent::h1'
                            )
                            response = scrapy.Selector(text=page.content())

                            list_urls = response.xpath(
                                '//div[contains(@aria-label,"esult")]//a[@class="hfpxzc"]/@href'
                            ).getall()
                            if not list_urls:
                                self.extract_data(page, search_keyword)
                            else:
                                element = page.wait_for_selector(
                                    'div[role="main"] div[role="feed"]'
                                )
                                self.scroll_inside_element(page, element)

                                time.sleep(2)

                                response = scrapy.Selector(text=page.content())

                                list_urls = response.xpath(
                                    '//div[contains(@aria-label,"esult")]//a[@class="hfpxzc"]/@href'
                                ).getall()

                                print(list_urls)
                                print(len(list_urls))

                                for list_url in list_urls:

                                    if list_url:

                                        print(list_url)

                                        try:

                                            page.goto(list_url)

                                            self.extract_data(
                                                page,
                                                search_keyword
                                            )

                                        except PlaywrightTimeoutError:

                                            print(
                                                f"Timeout while processing URL: {list_url}"
                                            )

                                        time.sleep(2)

                    except Exception as e:

                        print(f'Error processing {query}: {e}')

            finally:
                page.close()

    def wait_for_element(
            self,
            page,
            selector,
            retries=1,
            secondary_selector=None
    ):

        for attempt in range(retries + 1):

            try:

                page.wait_for_selector(selector, timeout=20000)

                return True

            except PlaywrightTimeoutError:

                if secondary_selector:

                    try:

                        page.wait_for_selector(
                            secondary_selector,
                            timeout=20000
                        )

                        return True

                    except PlaywrightTimeoutError:

                        print(
                            f"Secondary selector {secondary_selector} not found"
                        )

                        raise Exception(
                            f"Element {selector} not found"
                        )

                else:

                    print(f"Attempt {attempt + 1} failed")

                    raise Exception(
                        f"Element {selector} not found"
                    )

    def scroll_inside_element(self, page, element):

        try:

            last_height = element.evaluate("el => el.scrollHeight")

            flag = True

            while flag:

                time.sleep(2)

                element.evaluate(
                    "el => el.scrollTop = el.scrollHeight"
                )

                new_height = element.evaluate(
                    "el => el.scrollHeight"
                )

                scroll_count = 0
                same = True

                while scroll_count < 10:

                    new_height = element.evaluate(
                        "el => el.scrollHeight"
                    )

                    if new_height != last_height:

                        scroll_count = 10
                        last_height = new_height
                        same = False

                    else:

                        element.evaluate(
                            "el => el.scrollTop = el.scrollHeight"
                        )

                        time.sleep(1)

                        scroll_count += 1

                last_height = new_height

                if same:
                    flag = False

        except Exception as e:

            print(f"Error scrolling inside element: {e}")

    def extract_data(self, page, search_keyword):

        try:

            flag = True
            count = 0

            while flag and count < 1:

                try:

                    page.wait_for_selector(
                        '//span/parent::h1',
                        timeout=20000
                    )

                    flag = False

                except PlaywrightTimeoutError:

                    count += 1

                    print(
                        f"Attempt {count}: Waiting for business heading..."
                    )

                    if count == 1:
                        page.wait_for_selector(
                            '//span/parent::h1',
                            timeout=20000
                        )

                        flag = False

        except Exception as e:

            print(
                f"Error waiting for data to load for {search_keyword}: {e}"
            )

            return

        response = scrapy.Selector(text=page.content())

        exact_name = response.xpath(
            '//span/parent::h1/text()'
        ).get('')

        business = response.xpath(
            '//button[contains(@jsaction,"category")]/text()'
        ).get('')

        rating = response.xpath(
            '//span[@class="ceNzKf"]/preceding-sibling::span/text()'
        ).get('')

        review_count = response.xpath(
            '//span[contains(@aria-label,"review")]/text()'
        ).get('').replace(')', '').replace('(', '').strip()

        complete_address = response.xpath(
            '//button[contains(@aria-label,"Address")]/@aria-label'
        ).get('').strip().split(':')[-1]

        country = response.xpath(
            '//button[contains(@aria-label,"Address")]/@aria-label'
        ).get('').strip().split(',')[-1]

        street = response.xpath(
            '//button[contains(@aria-label,"Address")]/@aria-label'
        ).get('').strip().split(',')[0].split(':')[-1]

        phone = response.xpath(
            '//button[contains(@data-item-id,"phone")]/@aria-label'
        ).get('').strip()

        website = response.xpath(
            '//a[contains(@data-item-id,"authority")]/@href'
        ).get('').strip()

        # scrap_io_website = response.xpath(
        #     "//div[@class='scrapio-card-main__rows']/div[@data-type='website']/a/@href").get('').strip()
        scrap_io_phone = response.xpath(
            "//div[@class='scrapio-card-main__rows']/div[@data-type='phone_international']/a/@href").get('').replace(
            "tel:", "").strip()
        scrap_io_email = response.xpath("//div[@class='scrapio-card-main__rows']/div[@data-type='emails']/a/@href").get(
            '').replace("mailto:", "").strip()
        facebook = response.xpath("//div[@class='scrapio-card-main__rows']/div[@data-type='facebook']/a/@href").get(
            '').strip()
        instagram = response.xpath("//div[@class='scrapio-card-main__rows']/div[@data-type='instagram']/a/@href").get(
            '').strip()
        youtube = response.xpath("//div[@class='scrapio-card-main__rows']/div[@data-type='youtube']/a/@href").get(
            '').strip()

        item = {
            'name': exact_name,
            'website': website,
            'Phone': phone,
            # 'phone 2': scrap_io_phone,
            "email": scrap_io_email,
            "facebook": facebook,
            "instagram": instagram,
            "youtube": youtube,
            'Address': complete_address,
            'category': business,
            'rating': rating,
            'no of reviews': review_count,
            'business url': page.url
        }

        self.write_csv(item)

        self.count += 1

        print('total scraped data', self.count)

    def write_csv(self, item):
        print(item)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        filename = (
            f'{self.output_dir}/scraped_records_{self.current_timestamp}.csv'
        )
        file_exists = os.path.isfile(filename)
        with open(
                filename,
                mode='a',
                newline='',
                encoding='utf-8'
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=item.keys()
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow(item)
            print(f"Data written to {filename}")


scraper = GoogleMapScraper()
scraper.scrape_data()
