import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.hltv.org"
RESULTS_URL = "https://www.hltv.org/stats/matches"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.hltv.org/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive"
}


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    time.sleep(1.5)
    return BeautifulSoup(r.text, "html.parser")

def parse_match_card(card):
    match = {}
    link = card.find("a", class_="a-reset")
    if not link:
        return None

    match["match_url"] = BASE_URL + link["href"]
    teams = card.find_all("div", class_="team")
    if len(teams) == 2:
        match["team1"] = teams[0].text.strip()
        match["team2"] = teams[1].text.strip()

    event = card.find("span", class_="event-name")
    if event:
        match["event"] = event.text.strip()

    date = card.find("div", class_="date")
    if date:
        match["date"] = date.text.strip()

    return match

def parse_match_details(match):
    soup = get_soup(match["match_url"])

    # Match format (e.g., Best of 3)
    format_tag = soup.find("div", class_="standard-box veto-box")
    if format_tag and "Best of" in format_tag.text:
        match["format"] = [line for line in format_tag.text.split("\n") if "Best of" in line][0].strip()
    else:
        match["format"] = "Unknown"

    # Maps & scores
    maps = []
    map_rows = soup.find_all("div", class_="mapholder")
    for row in map_rows:
        map_name_tag = row.find("div", class_="mapname")
        score_tag = row.find("div", class_="results-center")
        if not map_name_tag or not score_tag:
            continue
        map_name = map_name_tag.text.strip()
        scores = score_tag.find_all("div", class_="results-team-score")
        if len(scores) == 2:
            team1_score = int(scores[0].text.strip())
            team2_score = int(scores[1].text.strip())
            maps.append({
                "map": map_name,
                "team1_score": team1_score,
                "team2_score": team2_score
            })

    match["maps"] = maps
    return match

def scrape_matches(pages=1):
    all_matches = []
    for i in range(pages):
        print(f"Scraping page {i+1}/{pages} ...")
        soup = get_soup(f"{RESULTS_URL}?offset={i*100}")
        cards = soup.find_all("div", class_="result-con")
        for card in cards:
            m = parse_match_card(card)
            if m:
                try:
                    m = parse_match_details(m)
                except Exception as e:
                    print(f"Error parsing {m['match_url']}: {e}")
                all_matches.append(m)
                time.sleep(2)  # be nice to HLTV (don't get blocked)
    return all_matches

if __name__ == "__main__":
    matches = scrape_matches(pages=1)  # scrape 100 matches
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(matches)} matches to matches.json")
