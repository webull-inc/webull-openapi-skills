"""Community tools for Webull OpenAPI Skill.

Provides: create_post, create_comment, list_hot_stocks,
          list_posts_by_symbol, get_post, list_my_posts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_community_create_result,
    format_community_hot_stocks,
    format_community_post_detail,
    format_community_post_list,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient

# Text length limits mirror the Webull OpenAPI contract (same bounds enforced
# by webull-openapi-mcp-server CreatePostTool / CreateCommentTool).
MAX_POST_TEXT_LENGTH = 20000
MAX_COMMENT_TEXT_LENGTH = 10000


def create_post(
    sdk: "SDKClient",
    config: "SkillConfig",
    text: str,
    symbol: Optional[str] = None,
    category: Optional[str] = None,
) -> str:
    """Create a plain-text community post.

    This is a write operation that publishes content under the user's account.

    :param text: Post content, max 20000 characters, required.
    :param symbol: Optional ticker symbol. Must be provided together with category.
    :param category: Optional market category (e.g. US_STOCK). Must be provided
        together with symbol.
    Returns: post_id.
    """
    if not text:
        return "Parameter error: text must not be empty"
    if len(text) > MAX_POST_TEXT_LENGTH:
        return f"Parameter error: text must not exceed {MAX_POST_TEXT_LENGTH} characters"
    symbol = symbol or None
    category = category or None
    if bool(symbol) != bool(category):
        return "Parameter error: symbol and category must be provided together"
    try:
        data = extract_response_data(
            sdk.data.community.create_post(text, symbol=symbol, category=category)
        )
        return prepend_disclaimer(format_community_create_result(data))
    except Exception as e:
        return handle_sdk_exception(e, "create_post", config.region_id)


def create_comment(
    sdk: "SDKClient",
    config: "SkillConfig",
    post_id: str,
    text: str,
) -> str:
    """Create a plain-text comment on an existing community post.

    This is a write operation that publishes content under the user's account.

    :param post_id: Parent post identifier.
    :param text: Comment content, max 10000 characters, required.
    Returns: comment_id.
    """
    if not text:
        return "Parameter error: text must not be empty"
    if len(text) > MAX_COMMENT_TEXT_LENGTH:
        return f"Parameter error: text must not exceed {MAX_COMMENT_TEXT_LENGTH} characters"
    try:
        data = extract_response_data(
            sdk.data.community.create_comment(post_id, text)
        )
        return prepend_disclaimer(format_community_create_result(data))
    except Exception as e:
        return handle_sdk_exception(e, "create_comment", config.region_id)


def list_hot_stocks(
    sdk: "SDKClient",
    config: "SkillConfig",
) -> str:
    """List stocks ranked by community activity.

    Returns: rank, symbol, category.
    """
    try:
        data = extract_response_data(sdk.data.community.list_hot_stocks())
        return prepend_disclaimer(format_community_hot_stocks(data))
    except Exception as e:
        return handle_sdk_exception(e, "list_hot_stocks", config.region_id)


def list_posts_by_symbol(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str,
    keyword: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """List community posts associated with a symbol.

    :param symbol: Stock symbol.
    :param category: Market category (e.g. US_STOCK).
    :param keyword: Optional search keyword.
    :param pagination_key: Optional cursor from the previous response.
    Returns: post_id, text, publish_time, thumbs, comments, pagination_key.
    """
    try:
        data = extract_response_data(
            sdk.data.community.list_posts_by_symbol(
                symbol, category, keyword=keyword, pagination_key=pagination_key
            )
        )
        return prepend_disclaimer(format_community_post_list(data, title="Posts by Symbol"))
    except Exception as e:
        return handle_sdk_exception(e, "list_posts_by_symbol", config.region_id)


def get_post(
    sdk: "SDKClient",
    config: "SkillConfig",
    post_id: str,
) -> str:
    """Get detailed information for a community post.

    :param post_id: Post identifier.
    Returns: post_id, text, publish_time, thumbs, comments, tickers.
    """
    try:
        data = extract_response_data(sdk.data.community.get_post(post_id))
        return prepend_disclaimer(format_community_post_detail(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_post", config.region_id)


def list_my_posts(
    sdk: "SDKClient",
    config: "SkillConfig",
    pagination_key: Optional[str] = None,
) -> str:
    """List posts created by the current user.

    :param pagination_key: Optional cursor from the previous response.
    Returns: post_id, text, publish_time, thumbs, comments, pagination_key.
    """
    try:
        data = extract_response_data(
            sdk.data.community.list_my_posts(pagination_key=pagination_key)
        )
        return prepend_disclaimer(format_community_post_list(data, title="My Posts"))
    except Exception as e:
        return handle_sdk_exception(e, "list_my_posts", config.region_id)
