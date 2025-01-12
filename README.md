# Scraper Toolkit
This project contains a set of scrapers to tracking prices of products of my interest and send messages in Telegram abot the price

## STRUCTURE

- `abstract.py`: Contains the Scraper abstract class with the common structure that all scrapers must comply: getting data from HTML and saving them to Postgres;
- `dell_scrape.py`: Dell scraper implementation, extracts product name, price and url;
- `amazon_scraper.py`: Amazon scraper implementation, extracts product name, price and url;
- `main.py`: Executes the scrapers and messaging to Telegram;
- `logger.py`: Logging setup file;
- `postgres_con.py`: Contains the PostgresClient that manages the database connection and SQL query execution;
- `queries.py`: Contains the query to retrieve data for the Telegram message;

## HOW TO USE IT
1. Clone repo:
`git clone https://github.com/lksprado/webscraping-product-bot.git` 
2. Create .env file with the following variable
```
PG_HOST=localhost
PG_PORT=5432 # default port for Postgres
PG_DATABASE=your_database_name
PG_USER=your_database_user
PG_PASSWORD=your_database_password
PG_SCHEMA=your_database_schema
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chatid_in_telegram
```
3. Spawn poetry virtual environemnt and install dependencies
`poetry shell && poetry install`
4. Install playwright
`playwright install` 
5. Modify or insert amazon/dell product page urls in the source files for each scraper
6. Create a DB table:
```
CREATE TABLE <your_database_schema>.wish_list (
	id serial4 NOT NULL,
	created_at timestamp NOT NULL,
	product_name text NOT NULL,
	product_price int4 NOT NULL,
	url text NOT NULL,
	source_scraper text NULL,
	CONSTRAINT wish_list_pkey PRIMARY KEY (id)
);
```
7. Execute `main.py`

## LEARNING
It is always a challenge to build a robust scraper due the unstable nature of the webpages in which data is collected. The hardest part in this project was to get data from Amazon website. It is known they have strong anti-scrap systems builts and this is why it is not possible to collect data from the html fetched via requests or headless selenium browsers.
The best way to scrap in "headless" is with the Playwright lib and get the data through JavaScript commands.






