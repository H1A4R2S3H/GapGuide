import requests
from bs4 import BeautifulSoup
import math
import json
import os
import time   
import random 

#List of User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

l = []
k = []

#Get Job IDs
id_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=software%20engineer&location=Bengaluru%2C%20Karnataka%2C%20India&geoId=105214831&start={}'

for i in range(0, 2):
    res = requests.get(id_url.format(i * 25), headers={"User-Agent": random.choice(USER_AGENTS)})
    soup = BeautifulSoup(res.text, 'html.parser')
    alljobs_on_this_page = soup.find_all("li")
    print(f"Found {len(alljobs_on_this_page)} jobs on page {i+1}")
    for x in range(0, len(alljobs_on_this_page)):
        base_card = alljobs_on_this_page[x].find("div", {"class": "base-card"})
        if base_card and base_card.get('data-entity-urn'):
            jobid = base_card.get('data-entity-urn').split(":")[3]
            l.append(jobid)
    
    #Add a delay after scraping each page of IDs
    time.sleep(random.uniform(2, 5))

print(f"Collected {len(l)} job IDs.")

#Get Job Details
detail_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'

for j in range(0, len(l)):
    o = {}
    
    #Pick a random user-agent for each request ---
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    resp = requests.get(detail_url.format(l[j]), headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    print(f"Scraping details for job {j+1}/{len(l)}")

    try:
        o["company"] = soup.find("div", {"class": "top-card-layout__card"}).find("a").find("img").get('alt')
    except:
        o["company"] = None

    try:
        o["job-title"] = soup.find("div", {"class": "top-card-layout__entity-info"}).find("a").text.strip()
        o["description"] = soup.find("div", {"class": "description__text"}).text.strip()
    except:
        o["job-title"] = None
        o["description"] = None

    try:
        o["level"] = soup.find("ul", {"class": "description__job-criteria-list"}).find("li").text.replace("Seniority level", "").strip()
    except:
        o["level"] = None
    
    k.append(o)
    
    # Add a random delay after each job detail request
    time.sleep(random.uniform(1, 4)) # Wait 1-4 seconds

#Save to JSON in the correct folder
output_path = os.path.join('..', 'data', 'scraped', 'job_postings.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(k, f, indent=4, ensure_ascii=False)

print(f"\nSuccessfully scraped {len(k)} jobs and saved to {output_path}")