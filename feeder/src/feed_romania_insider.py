import random
import time
import typing as t
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from config import Config
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

MAX_ARTICLES_TO_SCRAPE = 15


def get_qdrant_client():
    client = QdrantClient(Config.QDRANT_HOST)
    vector_size = len(Config.EMBEDDINGS.embed_query("some random text"))

    if not client.collection_exists(Config.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=Config.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        client.create_payload_index(
            collection_name=Config.QDRANT_COLLECTION,
            field_name="source",
            field_schema="keyword",
        )
    return client


client = get_qdrant_client()


@dataclass
class NewsArticle:
    source: str
    title: str
    publish_date: str
    body: str | None = None


def load() -> list[Document]:
    scraped = 0
    articles = []
    news = get_latest_news()
    for article in news:
        if url_already_exists(article.source):
            print(f"url {article.source} already exists")
            continue

        if scraped >= MAX_ARTICLES_TO_SCRAPE:
            break

        time.sleep(random.uniform(0.2, 2))
        article.body = extract_news_body(article.source)
        if not article.body:
            continue

        articles.append(
            Document(
                page_content=article.body,
                metadata={
                    "source": article.source,
                    "title": article.title,
                    "publish_date": article.publish_date,
                },
            )
        )
        scraped += 1

    return articles


def split(articles: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    return splitter.split_documents(articles)


def store(articles: list[Document]) -> None:
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=Config.QDRANT_COLLECTION,
        embedding=Config.EMBEDDINGS,
    )
    vector_store.add_documents(documents=articles)


def get_latest_news() -> t.Generator[NewsArticle, None, None]:
    base_url = "https://www.romania-insider.com"
    url = f"{base_url}/latest/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    articles = soup.select("article")
    for article in articles:
        publish_date = article.select_one(
            "div .date-and-category > div:first-child"
        ).text
        link = article.select_one("div .article-data > div:nth-of-type(2) > a")
        yield NewsArticle(
            source=f"{base_url}/{link['href'].strip('/')}",
            title=link.text,
            publish_date=publish_date,
        )


def url_already_exists(url: str) -> bool:
    existing_points, _ = client.scroll(
        collection_name=Config.QDRANT_COLLECTION,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="source", match=models.MatchValue(value=url)),
            ]
        ),
        limit=1,
        with_payload=False,
        with_vectors=False,
    )
    return len(existing_points) > 0


def extract_news_body(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    article_p = soup.select("article p")
    return "\n".join(p.text for p in article_p)


if __name__ == "__main__":
    articles = load()
    print(f"Loaded {len(articles)} articles")

    articles = split(articles)
    print(f"Split into {len(articles)} chunks")

    store(articles)
    print("Stored articles")
