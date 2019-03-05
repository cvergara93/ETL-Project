#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup as bs
from splinter import Browser
import time
import pandas as pd
import requests

def init_browser():
    """ Connects path to chromedriver """

    # In[ ]:


    # WINDOWS/PC - Import splinter and set the cromedriver path
    # executable_path = {'executable_path': 'chromedriver.exe'}
    # browser = Browser('chrome', **executable_path, headless=False)

    # MAC - Import splinter and set the cromedriver path
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=True)


# # Scraping Subreddits for Subscriber Count

# In[ ]:

def scrape():
    """ Scrapes all websites for NFL data """

    subreddits = ["AZCardinals", "falcons", "ravens", "buffalobills", "panthers","CHIBears", "bengals", "Browns",
                "cowboys", "DenverBroncos", "detroitlions", "GreenBayPackers", "Texans", "Colts", "Jaguars",
                "KansasCityChiefs", "miamidolphins", "minnesotavikings", "Patriots", "Saints", "NYGiants", "nyjets",
                "oaklandraiders", "eagles", "steelers", "LosAngelesRams", "Chargers", "49ers", "Seahawks", 
                "buccaneers", "Tennesseetitans", "Redskins"]

    subcounts = []

    # Call on chromedriver function to use for splinter
    browser = init_browser()

    # In[ ]:


    for sub in subreddits:
        time.sleep(1)
        url = f"https://www.reddit.com/r/{sub}"
        browser.visit(url)
        time.sleep(1)
        html = browser.html
        soup = bs(html, "html.parser")
        subscribers = int(float(soup.find("p", class_="s1bd5ppi-10").text.split("k")[0])*1000)
        dictionary = {"Subreddit URL (https://www.reddit.com/r/)":sub, "Subs":subscribers}
        subcounts.append(dictionary)


    # In[ ]:


    df = pd.DataFrame(subcounts)
    teams = pd.read_csv("Teams.csv")


    # In[ ]:


    combined = pd.merge(df, teams, on="Subreddit URL (https://www.reddit.com/r/)")
    combined = combined.drop(["Subreddit URL (https://www.reddit.com/r/)"], axis=1)
    combined.head(32)


    # In[ ]:


    combined.to_csv("TeamsSubs.csv", index=False, header=True)


    # # Scraping Team Values

    # In[ ]:


    values_url = "https://www.reddit.com/r/nfl/comments/9hflml/forbes_nfl_2018_team_valuations_most_valuable/"


    # In[ ]:


    tables = pd.read_html(values_url)
    tables


    # In[ ]:


    values_df = tables[0]
    values_df.columns = ["Team", "Value ($B)", "Revenue ($M)", "Operating Income ($M)"]


    # In[ ]:


    values_combined = pd.merge(combined, values_df, on="Team")
    values_combined.head(32)


    # In[ ]:


    values_combined.to_csv("TeamsSubsValues.csv", index=False, header=True)


    # # Scraping City Populations

    # In[ ]:


    cities = values_combined["Real City"].tolist()
    cities


    # In[ ]:


    cities = [item.replace(", ", "-") for item in cities]
    cities = [item.replace("New York City", "New York") for item in cities]
    cities = [item.replace(" ", "-") for item in cities]
    cities = [item.replace("Nashville-Tennessee", "Nashville-Davidson-Tennessee") for item in cities]
    cities = [item.replace("Washington-DC", "Washington-District-of-Columbia") for item in cities]
    cities_urls = [item + ".html" for item in cities]
    cities_urls


    # In[ ]:


    values_combined['City URL'] = pd.Series(cities_urls)
    values_combined.head(32)


    # In[ ]:


    populations = []

    for city in cities_urls:
        pop_url = f"http://www.city-data.com/city/{city}"
        browser.visit(pop_url)
        time.sleep(1)
        pop_html = browser.html
        pop_soup = bs(pop_html, "html.parser")
        population = int(float(pop_soup.find("section", class_="city-population").text.split(":")[1].strip().replace(",","")))
        pop_dictionary = {"City URL":city, "Population (2016)":population}
        populations.append(pop_dictionary)


    # In[ ]:


    pop_df = pd.DataFrame(populations)
    final_df = pd.merge(values_combined, pop_df, on="City URL")
    values_pop_df = final_df.drop(["City URL"], axis=1)
    values_pop_df.head(32)


    # In[ ]:


    values_pop_df.to_csv("TeamsSubsValuesPops.csv", index=False, header=True)


    # # Scraping Team Ages

    # In[ ]:


    ages_url = "https://en.wikipedia.org/wiki/National_Football_League"


    # In[ ]:


    ages_tables = pd.read_html(ages_url)
    ages_tables


    # In[ ]:


    ages_df = ages_tables[2]
    ages_df = ages_df[["Club[57]", 'First season[59]']]
    ages_df.columns = ["Team", "Founded"]
    years = ages_df["Founded"].tolist()
    years = [item[:4] for item in years]
    del years[16]
    years = years[:-1]
    years = [int(item) for item in years]


    # In[ ]:


    teams = ages_df["Team"].tolist()
    del teams[16]
    del teams[32]


    # In[ ]:


    cleanteams = []

    for foo in teams:
        try:
            team = foo.split("*")[0]
            cleanteams.append(team)
        except:
            cleanteams.append(foo)


    # In[ ]:


    import datetime
    currentyear = datetime.date.today().year

    teamages = []

    for x in years:
        teamage = currentyear - x
        teamages.append(teamage)


    # In[ ]:


    ages_df = pd.DataFrame({
        "Team": cleanteams,
        "Team Age": teamages
    })


    # In[ ]:


    ages_df.head(32)


    # In[ ]:

    final_df = pd.merge(values_pop_df, ages_df, on="Team")
    final_df.head(32)

    return final_df
