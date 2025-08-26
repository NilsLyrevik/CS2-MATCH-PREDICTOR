from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time

RESULTS_URL = "https://www.hltv.org/stats/matches?csVersion=CS2"

def get_soup(url: str) -> BeautifulSoup:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)  # headless=False to see it
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Wait for network to be idle (no XHR in flight)
        page.wait_for_load_state("networkidle")

        # Save screenshot + page content for inspection
        page.screenshot(path="debug.png", full_page=True)
        html = page.content()
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Saved debug.png and debug.html")
        # keep browser open a bit so you can look
        time.sleep(5)

        browser.close()

    return BeautifulSoup(html, "html.parser")


def parse_matches(soup):
    matches = []
    rows = soup.select("table.stats-table tbody tr")
    for row in rows:
        try:
            date = row.select_one("td.date-col div.time").get_text(strip=True)

            team1_col, team2_col = row.select("td.team-col")
            team1 = team1_col.select_one("a").get_text(strip=True)
            team1_score = int(team1_col.select_one("span.score").get_text(strip=True).strip("()"))

            team2 = team2_col.select_one("a").get_text(strip=True)
            team2_score = int(team2_col.select_one("span.score").get_text(strip=True).strip("()"))

            map_played = row.select_one("td.statsDetail div.dynamic-map-name-full").get_text(strip=True)
            event = row.select_one("td.event-col a").get_text(strip=True)

            matches.append({
                "date": date,
                "team1": team1,
                "team1_score": team1_score,
                "team2": team2,
                "team2_score": team2_score,
                "map": map_played,
                "event": event,
            })
        except Exception as e:
            print(f"Skipping row due to parse error: {e}")
            continue
    return matches

def scrape_matches(pages=1):
    all_matches = []
    for i in range(pages):
        print(f"Scraping page {i+1}/{pages} ...")
        url = f"{RESULTS_URL}&offset={i * 50}"
        soup = get_soup(url)
        batch = parse_matches(soup)
        print(f"  Found {len(batch)} matches on page {i+1}.")
        all_matches.extend(batch)
        time.sleep(2)
    return all_matches

if __name__ == "__main__":
    matches = scrape_matches(pages=2)
    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(matches)} matches to matches.json")
