"""
External data fetcher using Tavily Search API
Provides job market, industry news, and HR trend data
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.knowledge')


class ExternalDataFetcher:
    """Fetches external data via Tavily Search API"""

    def __init__(self):
        api_key = Config.TAVILY_API_KEY
        if api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=api_key)
                logger.info("Tavily client initialized")
            except ImportError:
                logger.warning("tavily-python not installed, external data fetching disabled")
                self.client = None
        else:
            logger.info("TAVILY_API_KEY not set, external data fetching disabled (will use LLM fallback)")
            self.client = None

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        topic: str = "general",
        max_results: int = 5,
        include_answer: bool = False
    ) -> List[Dict[str, Any]]:
        """Generic Tavily search

        Args:
            query: Search query
            search_depth: "basic" or "advanced" (deeper crawl)
            topic: "general" or "news"
            max_results: Max results to return
            include_answer: Include AI-generated answer

        Returns:
            List of search results with title, url, content
        """
        if not self.client:
            return []

        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                topic=topic,
                max_results=max_results,
                include_answer=include_answer
            )

            results = []
            if include_answer and response.get("answer"):
                results.append({
                    "type": "answer",
                    "content": response["answer"],
                    "title": "AI Summary",
                    "url": ""
                })

            for r in response.get("results", []):
                results.append({
                    "type": "result",
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0)
                })

            logger.info(f"Tavily search '{query[:50] + ('...' if len(query) > 50 else '')}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.warning(f"Tavily search failed for '{query[:50] + ('...' if len(query) > 50 else '')}': {e}")
            return []

    def fetch_job_market(self, profession: str, industry: str) -> List[Dict[str, Any]]:
        """Fetch job market data (postings, salary, hiring trends)"""
        queries = [
            f"{profession} {industry} 求人 年収 {datetime.now().year} {datetime.now().year + 1}",
            f"{profession} 転職市場 採用動向 最新",
        ]
        results = []
        for q in queries:
            results.extend(self.search(q, search_depth="advanced", max_results=5))
        return results

    def fetch_industry_news(self, industry: str, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch industry news"""
        query = f"{industry} 業界ニュース 最新動向"
        if keywords:
            query += " " + " ".join(keywords[:3])
        return self.search(query, topic="news", max_results=5)

    def fetch_hr_trends(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Fetch HR trends and skill demand data"""
        query = " ".join(keywords[:5]) + f" HR トレンド スキル需要 {datetime.now().year} {datetime.now().year + 1}"
        return self.search(query, search_depth="advanced", max_results=5, include_answer=True)
