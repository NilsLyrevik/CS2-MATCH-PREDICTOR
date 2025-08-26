# CS2 Match Predictor  

This project is the early stage of a Counter-Strike 2 match prediction tool.  
Currently, it focuses on scraping past CS2 match results from [HLTV.org](https://www.hltv.org/stats/matches?csVersion=CS2), storing them in a structured JSON format.  

Future steps will involve training a machine learning model on this data to predict match outcomes.  

## Features (so far)  
- Scrapes CS2 match history (teams, scores, maps, events, dates).  
- Saves the results into a `matches.json` file.  
- Built with Playwright to handle HLTV’s dynamic pages.  
- Clean, structured data ready for analysis or ML training.  

Example output (`matches.json`):
```json
[
  {
    "date": "12/12/12",
    "team1": "teamname1",
    "team1_score": 10,
    "team2": "teamname2",
    "team2_score": 13,
    "map": "Ancient",
    "event": "some tournament somewhere at sometime"
  }
]
```

## Installation
1. Clone the repo
```bash
git clone https://github.com/yourname/CS2-MATCH-PREDICTOR.git
cd CS2-MATCH-PREDICTOR
```

2. create and activate the virtual environment

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

3. isntall depedencies:


```bash
pip isntall -r requirements.txt
```
 4. install Playwright browser (once):
```bash
playwright install
```

## Usage
run the scraper (example scrapes 2 pages = 100 matches)

```bash
python src/scrape.py
```
