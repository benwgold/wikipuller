# Wikipedia Article Analytics API

## Overview
This is a FastAPI application that serves analytics data for Wikipedia articles. It has three main functionalities:
1. Retrieve the most viewed articles for a specific month or week.
2. Get the total views for a specific article over a specific month or week
3. Find the day an article was most viewed over a month or week.

## Python Dependencies
- FastAPI
- requests
- datetime
- enum
- json
- pytest (for testing)

## Endpoints

### `GET /`
- Returns a welcome message and hints at available operations.

---

### `GET /most-viewed-articles`
**Params**: 
  - `year`: The year for which to fetch data (in integer form).
  - `month`: The month for which to fetch data (in integer form).
  - `optional_week_start_day`: Start day of the week if you want weekly data (in integer form).
  
**Response**: JSON object containing most viewed articles.

---

### `GET /article-view-count`
**Params**: 
  - `article`: Wikipedia article name (case sensitive with '_' delimiter for spaces).
  - `year`: The year for which to fetch data (in integer form).
  - `month`: The month for which to fetch data (in integer form)
  - `optional_week_start_day`: Start day of the week if you want weekly data (in integer form).
  
**Response**: JSON object containing view count for the specified article.

---

### `GET /article-view-count-top-day`
**Params**: 
  - `article`: Wikipedia article name (case sensitive with '_' delimiter for spaces).
  - `year`: The year for which to fetch data (in integer form).
  - `month`: The month for which to fetch data (in integer form).
  - `optional_week_start_day`: Start day of the week if you want weekly data (in integer form).
  
**Response**: JSON object containing the day the article was most viewed.

## Setup
1. Install required packages:
    ```bash
    pip install fastapi
    pip install requests
    ```
2. Run the app:
    ```bash
    uvicorn filename:app --reload
    ```

## Testing Setup
1. Install required packages:
    ```bash
    pip install pytest
    ```
2. Run the tests:
    ```bash
    pytest main_test.py
    ```

## Notes
- The app uses Wikimedia's API for data fetching.
- Make sure to include a valid User-Agent in API requests to avoid blocking.

## Future Improvements
- Improve input validation. Certain invalid inputs may cause internal server errors.
- Add Frontend to initiate requests and render responses
- Add basic rate throttling and usage tracking to protect against overloading our endpoint or Wikipedia API limits.
- Improve article matching (punctuation, case sensitivity, etc.)