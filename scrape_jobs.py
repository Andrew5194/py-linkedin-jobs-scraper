import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
    OnSiteOrRemoteFilters,
)
import csv
import os

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)


# Fired once for each successfully processed job
def on_data(data: EventData):
    jobs_list = [data.query, data.title, data.company, data.company_link, data.date, data.link, data.insights]
    print(jobs_list)

    with open("jobs.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(jobs_list)


# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print("[ON_METRICS]", str(metrics))


def on_error(error):
    print("[ON_ERROR]", error)


def on_end():
    print("[ON_END]")


# Write CSV file with starting header
if not os.path.isfile("scrape_jobs.csv"):
    with open("scrape_jobs.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Query", "Title", "Company", "Company_Link", "Date", "Link", "Insights"])

scraper = LinkedinScraper(
    chrome_executable_path=None,  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_options=None,  # Custom Chrome options here
    headless=False,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=40,  # Page load timeout (in seconds)
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query="DevOps Engineer",
        options=QueryOptions(
            locations=["Remote"],
            apply_link=False,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page mus be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            page_offset=0,  # How many pages to skip
            limit=1000,
            filters=QueryFilters(
                # company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[TypeFilters.FULL_TIME],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE],
                experience=[ExperienceLevelFilters.MID_SENIOR],
            ),
        ),
    ),
]

scraper.run(queries)
