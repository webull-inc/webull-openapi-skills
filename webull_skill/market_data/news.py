"""News data tools for Webull OpenAPI Skill.

Provides: search_news, get_news_detail, get_stock_news (US only).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_news_search,
    format_news_detail,
    format_stock_news,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient

# Keyword length cap matches the Webull OpenAPI news-search contract.
MAX_NEWS_KEYWORD_LENGTH = 100
VALID_STOCK_NEWS_SENTIMENTS = frozenset({"POSITIVE", "NEGATIVE", "NEUTRAL"})


def search_news(
    sdk: "SDKClient",
    config: "SkillConfig",
    keyword: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Search US market news by keyword.

    US market only.

    :param keyword: Search keyword, max 100 characters, required.
    :param start_date: Start date in yyyy-MM-dd format, None defaults to 7 days ago.
    :param end_date: End date in yyyy-MM-dd format, None defaults to today.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: news list with news_id, title, summary, source, url,
        publish_time, sentiment, related_symbols.
    """
    if not keyword:
        return "Parameter error: keyword must not be empty"
    if len(keyword) > MAX_NEWS_KEYWORD_LENGTH:
        return f"Parameter error: keyword must not exceed {MAX_NEWS_KEYWORD_LENGTH} characters"
    try:
        data = extract_response_data(
            sdk.data.news.get_news_search(keyword, start_date, end_date, pagination_key)
        )
        return prepend_disclaimer(format_news_search(data))
    except Exception as e:
        return handle_sdk_exception(e, "search_news", config.region_id)


def get_news_detail(
    sdk: "SDKClient",
    config: "SkillConfig",
    news_id: str,
) -> str:
    """Query the full content of a US market news article by its ID.

    US market only.

    :param news_id: News unique identifier, required.
    Returns: news detail with title, summary, source, url, publish_time,
        sentiment, related_symbols, content.
    """
    try:
        data = extract_response_data(sdk.data.news.get_news_detail(news_id))
        return prepend_disclaimer(format_news_detail(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_news_detail", config.region_id)


def get_stock_news(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    sentiment: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Query stock-related news list with optional sentiment filter.

    US market only.

    :param symbol: Stock symbol, e.g. TSLA, required.
    :param sentiment: Sentiment filter: POSITIVE, NEGATIVE or NEUTRAL,
        None to return all.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: news list with news_id, title, summary, source, url,
        publish_time, sentiment, related_symbols.
    """
    if sentiment is not None:
        if not isinstance(sentiment, str):
            return "Parameter error: sentiment must be one of POSITIVE, NEGATIVE, NEUTRAL"
        sentiment = sentiment.strip().upper() or None
        if sentiment is not None and sentiment not in VALID_STOCK_NEWS_SENTIMENTS:
            return "Parameter error: sentiment must be one of POSITIVE, NEGATIVE, NEUTRAL"
    try:
        data = extract_response_data(
            sdk.data.news.get_stock_news(
                symbol,
                category="US_STOCK",
                sentiment=sentiment,
                pagination_key=pagination_key,
            )
        )
        return prepend_disclaimer(format_stock_news(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_news", config.region_id)
