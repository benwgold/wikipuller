from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch
from main import app  

client = TestClient(app)

# Mock the external API calls
def mock_article_request_with_url(url):
    return {
            "items": [
                {"views": 50, "timestamp": "20230101"},
                {"views": 60, "timestamp": "20230102"},
            ]
        }

def mock_most_viewed_request_with_url(url):
    return {
        "items": [
            {
                "articles": [
                    {"article": "Article1", "views": 100},
                    {"article": "Article2", "views": 200},
                ]
            }
        ]
    }

# Test root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Add an API endpoint to the url: a) /most-viewed-articles b) /article-view-count or c) /article-view-count-top-day"}

# Test most-viewed-articles endpoint
@patch("main.make_request_with_url", side_effect=mock_most_viewed_request_with_url)
def test_most_viewed_articles(mock_request):
    response = client.get("/most-viewed-articles?year=2023&month=1")
    assert response.status_code == 200
    assert response.json() == '{"top_articles": {"Article1": 100, "Article2": 200}}'

# Test article-view-count endpoint
@patch("main.make_request_with_url", side_effect=mock_article_request_with_url)
def test_article_view_count(mock_request):
    response = client.get("/article-view-count?article=TestArticle&year=2023&month=1")
    assert response.status_code == 200
    assert response.json() == '{"view_count": 110, "article_name": "TestArticle", "date_range": "2023-01-01 to 2023-02-01"}'

# Test article-view-count-top-day endpoint
@patch("main.make_request_with_url", side_effect=mock_article_request_with_url)
def test_article_view_count_top_day(mock_request):
    response = client.get("/article-view-count-top-day?article=TestArticle&year=2023&month=1")
    assert response.status_code == 200
    assert response.json() == '{"view_count": 60, "article_name": "TestArticle", "date": "20230102"}'