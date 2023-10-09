import datetime
import enum
import json
import requests

from fastapi import FastAPI, Query

app = FastAPI()

MOST_VIEWED_API_STUB = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access"
ARTICLE_VIEWS_API_STUB = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents"

def make_request_with_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Process the JSON data as you need
        return data
    else:
        return {"error": f"Failed to fetch data, status code: {response.status_code}"}
    
def fetch_top_articles(year: int, month: int, opt_week_start_day: int):
    article_counts = {}
    responses = []

    if opt_week_start_day != -1:
        start_date = datetime.date(year=year, month=month, day=opt_week_start_day)
        # There is no weekly API available, so make 7 requests (one for each day) and aggregate the result.
        for i in range(7):
            request_date = start_date + datetime.timedelta(days=i)
            response = make_request_with_url("{stub}/{year}/{month}/{day}".format(
                stub=MOST_VIEWED_API_STUB, 
                year=start_date.strftime("%Y"), 
                month=start_date.strftime("%m"),
                day=start_date.strftime("%d")))
            responses.append(response)
    else:
        start_date = datetime.date(year=year, month=month, day=1)
        response = make_request_with_url("{stub}/{year}/{month}/all-days".format(
                stub=MOST_VIEWED_API_STUB, 
                year=start_date.strftime("%Y"), 
                month=start_date.strftime("%m")))
        responses.append(response)

    # Find top articles by aggregating views over the date range.
    for response in responses:
        if 'items' in response and len(response['items']) > 0 and 'articles' in response['items'][0]:
            for article in response['items'][0]['articles']:
                if article['views']:
                    if article['article'] in article_counts:
                        article_counts[article['article']] += article['views']
                    else:
                        article_counts[article['article']] = article['views']
    return {"top_articles": article_counts}

class ArticleViewAggregationType(enum.Enum):
    SUM = 0
    TOP_DAY = 1

def fetch_article_views(article: str, year: int, month: int, aggregation_type: ArticleViewAggregationType, opt_week_start_day: int = -1):
    article_counts = {}
    responses = []
    
    start_date = datetime.date(year=year, month=month, day=opt_week_start_day if opt_week_start_day != -1 else 1)
    if opt_week_start_day != -1:
        # if week start day was specified assign end date to be a week in the future.
        end_date = start_date + datetime.timedelta(days=7)
    else:
        # else assign to one month in the future
        end_date = datetime.date(year=year if month != 12 else year+1, month=(month+1) % 12, day=1)


    response = make_request_with_url("{stub}/{article}/daily/{start_date_string}00/{end_date_string}00".format(
            stub=ARTICLE_VIEWS_API_STUB,
            article = article,
            start_date_string = start_date.strftime("%Y%m%d"),
            end_date_string = end_date.strftime("%Y%m%d")))
    print(response)

    if 'items' in response and len(response['items']) > 0 :
        if (aggregation_type == ArticleViewAggregationType.SUM):
            article_count = 0
            for article_data in response['items']:
                article_count += article_data['views']
            return {'view_count': article_count, 'article_name': article, 'date_range': f'{start_date} to {end_date}'.format(start_date=str(start_date), end_date=str(end_date))}
        elif (aggregation_type == ArticleViewAggregationType.TOP_DAY):
            top_article_views = -1
            top_article_day = None
            for article_data in response['items']:
                if article_data['views'] > top_article_views:
                    top_article_views = article_data['views']
                    top_article_day = article_data['timestamp']
            return {'view_count': top_article_views, 'article_name': article, 'date': top_article_day}
    return {'error': 'An article of that type was not found.'}

@app.get("/")
async def root():
    return {"message": "Add an API endpoint to the url: a) /most-viewed-articles b) /article-view-count or c) /article-view-count-top-day"}

@app.get("/most-viewed-articles")
async def most_viewed_articles(year: int = -1, month: int = -1, optionalweekstartday: int = -1):
    """
    Retrieve a list of the most viewed articles for a week or a month. 
    """
    # Validation
    if year == -1 or month == -1:
        return {"error": "Must supply valid week or month"}
    
    article_counts = fetch_top_articles(year, month, optionalweekstartday)
    return json.dumps(article_counts)


@app.get("/article-view-count")
async def article_view_count(article: str = "", year: int = -1, month: int = -1, optionalweekstartday: int = -1):
    """
    Retrieve the total views for an article over a provided date range.
    """
    # Validation
    if article == "":
        return {"error": "Must supply valid article string"}
    if year == -1 or month == -1:
        return {"error": "Must supply valid week or month"}
    
    view_count = fetch_article_views(article, year, month, ArticleViewAggregationType.SUM, optionalweekstartday)
    return json.dumps(view_count)


@app.get("/article-view-count-top-day")
async def article_view_count(article: str = "", year: int = -1, month: int = -1, optionalweekstartday: int = -1):
    """
    Retrieve the most popular day an article had over a given month.
    """
    # Validation
    if article == "":
        return {"error": "Must supply valid article string"}
    if year == -1 or month == -1:
        return {"error": "Must supply valid week or month"}
    
    view_count = fetch_article_views(article, year, month, ArticleViewAggregationType.TOP_DAY, optionalweekstartday)
    return json.dumps(view_count)
