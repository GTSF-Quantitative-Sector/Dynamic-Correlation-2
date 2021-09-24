# Dynamic Correlation 2
## The purpose of this repo is to improve on the Original Correlation Matrix by adding some kind of Beta metric (looking at Treynor Ratio).

Currently the code is split into these parts:
### 1. Backend
The API is in Flask (python web framework) and it is hosted on Heroku.
All endpoints are located in app.py.
Heroku handles all configs and responses.
### 2. Frontend
Google Sheets has a script tool that is able to make API calls using JavaScript.
The received data is then added to the sheet and graphed.

### 3. Development Guideline
- Week 1 (09/27/2021)
  - Review/Study current implementation. We want to understand fundamentally the math and necessity of the matrix.
  - Researching Beta and Treynor ratio. Play around with the current matrix and come up with 2 improvements for the next meeting.
  - Divide work
    - Javascript & Google Sheets = Yoshi
    - Python & Flask = Bennett & Dylan
    - Github & Heroku = Dylan

- Week 2 (10/04/2021)
  - Have running prototype and testing.
  - Troubleshooting

- Week 3 (10/11/2021)
  - Completed and uploaded to the repo.
