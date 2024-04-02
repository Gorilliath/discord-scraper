# discord-scraper

_I want some things from you Discord..._

## Prerequisites

- [Node and NPM](https://nodejs.org/en/download/)

## Installation

- `npm i`

## Usage

- `npm run scrape`
- Might need to press `step-over` button in the Playwright debugging window so the Discord login page is opened
- Login to Playwright's browser window
- Go to the desired DM
- Set up search filter to have `mentions:` for both users
- Look at `Old` entries first to have consistent IDs with subsequent runs
- Press the `Resume execution` button to proceed with the scraping

## Results

- Results will be in `./output`
