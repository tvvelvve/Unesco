import requests
from bs4 import BeautifulSoup
import pandas as pd
import pycountry_convert as pc

# --- Step 1: Scrape the UNESCO Data ---
url = "https://whc.unesco.org/en/list/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

data = []

countries = soup.find_all('h4')

for country_tag in countries:
    country_name = country_tag.get_text(strip=True)
    site_div = country_tag.find_next_sibling('div', class_='list_site')
    
    if not site_div:
        continue
    
    for li in site_div.find_all('li'):
        a_tag = li.find('a')
        if not a_tag:
            continue
        
        site_name = a_tag.get_text(strip=True)
        class_list = li.get('class', [])
        
        if 'cultural' in class_list or 'cultural_danger' in class_list:
            site_type = 'Cultural'
        elif 'natural' in class_list or 'natural_danger' in class_list:
            site_type = 'Natural'
        elif 'mixed' in class_list or 'mixed_danger' in class_list:
            site_type = 'Mixed'
        else:
            site_type = 'Unknown'

        if 'cultural_danger' in class_list or 'natural_danger' in class_list:
            endangered = 'Endangered'
        else:
            endangered = 'No'
        
        data.append({
            'Site Name': site_name,
            'Country': country_name,
            'Type': site_type,
            'Endangered': endangered
        })

df = pd.DataFrame(data)

# --- Step 2: Fix Country Names ---

def fix_country_name(country_name):
    # Fix special cases
    if country_name == "United Kingdom of Great Britain and Northern Ireland":
        return "United Kingdom"
    elif country_name == "United States of America":
        return "United States"
    elif country_name == "Republic of Korea":
        return "South Korea"
    elif country_name == "Democratic People's Republic of Korea":
        return "North Korea"
    elif country_name == "Russian Federation":
        return "Russia"
    elif country_name == "Syrian Arab Republic":
        return "Syria"
    elif country_name == "Iran (Islamic Republic of)":
        return "Iran"
    elif country_name == "Viet Nam":
        return "Vietnam"
    elif country_name == "Côte d'Ivoire":
        return "Ivory Coast"
    elif country_name == "Bolivia (Plurinational State of)":
        return "Bolivia"
    elif country_name == "Cabo Verde":
        return "Cape Verde"
    elif country_name == "Democratic Republic of the Congo":
        return "DR Congo"
    elif country_name == "Congo":
        return "Republic of the Congo"
    elif country_name == "Holy See":
        return "Vatican City (Holy See)"
    elif country_name == "Jerusalem (Site proposed by Jordan)":
        return "Jerusalem"
    elif country_name == "Lao People's Democratic Republic":
        return "Laos"
    elif country_name == "Micronesia (Federated States of)":
        return "Micronesia"
    elif country_name == "Netherlands (Kingdom of the)":
        return "Netherlands"
    elif country_name == "Republic of Moldova":
        return "Moldova"
    elif country_name == "State of Palestine":
        return "Palestine"
    elif country_name == "Türkiye":
        return "Turkey"
    elif country_name == "United Republic of Tanzania":
        return "Tanzania"
    elif country_name == "Venezuela (Bolivarian Republic of)":
        return "Venezuela"
    else:
        return country_name
    
df['Country'] = df['Country'].apply(fix_country_name)

# --- Step 3: Add Continent ---

def get_continent(country_name):
    try:
        code = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(code)
        return {
            'AF': 'Africa',
            'AS': 'Asia',
            'EU': 'Europe',
            'NA': 'North America',
            'SA': 'South America',
            'OC': 'Oceania',
            'AN': 'Antarctica'
        }.get(continent_code, None)
    except Exception:
        return None

df['Continent'] = df['Country'].apply(get_continent)

# --- Step 4: Add Flag ---

emoji = pd.read_csv('country_emojis.txt', sep='\t')
country_to_emoji = dict(zip(emoji['Country'], emoji['Emoji']))
df['Flag'] = df['Country'].apply(lambda x: country_to_emoji.get(x, ''))

# --- Step 5: Aggregate Sites ---

df = df.groupby(
    ['Site Name', 'Type', 'Endangered']
).agg({
    'Continent': lambda x: ', '.join(sorted(set(x.dropna().astype(str)))),
    'Country': lambda x: ', '.join(sorted(set(x.dropna().astype(str)))),
    'Flag': lambda x: ', '.join(sorted(set(x.dropna().astype(str))))
}).reset_index()

# --- Step 5: Save Result ---

df = df[['Site Name', 'Continent', 'Country', 'Flag', 'Type', 'Endangered']]
df.to_csv("unesco_world_heritage_sites.csv", index=False, encoding='utf-8')
print(df.head(10))
