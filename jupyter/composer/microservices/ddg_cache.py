"""
ddg_cache.py - DuckDuckGo search cache with semantic similarity and LLM summarization

Usage:
    from ddg_cache import cached_ddg_search
    result = await cached_ddg_search("NVIDIA DIGITS", max_results=5, summarize_all=True)
"""
import os, json, hashlib, asyncio, numpy as np, sys
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

# External dependencies
from ddgs import DDGS
import httpx, trafilatura
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Observability
sys.path.append('/dli/task/composer/microservices')
from observability import get_observability
logger, tracer, _, traced = get_observability("ddg-cache")

Base = declarative_base()

# ============================================================================
# Database Model & Management
# ============================================================================

class CacheEntry(Base):
    """Single table: query → results + embeddings + summary"""
    __tablename__ = "ddg_cache"
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True, index=True, nullable=False)
    query_text = Column(String(1000), nullable=False)
    results = Column(JSON, nullable=False)
    embeddings = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    last_accessed = Column(DateTime, default=datetime.utcnow)

def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/ddg_cache")

async def init_database(database_url: Optional[str] = None):
    """Initialize database schema"""
    url = database_url or get_database_url()
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    return True

@asynccontextmanager
async def get_session(database_url: Optional[str] = None):
    """Database session context manager"""
    url = database_url or get_database_url()
    engine = create_async_engine(url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await engine.dispose()

# ============================================================================
# Search & Scraping
# ============================================================================

def hash_query(query: str) -> str:
    """Generate consistent hash for deduplication"""
    return hashlib.sha256(query.lower().strip().encode()).hexdigest()

async def search_duckduckgo(query: str, max_results: int = 10) -> List[Dict]:
    """Live DDG search. Returns: [{title, body, href}]"""
    try:
        results = DDGS().text(query, max_results=max_results)
        return [{"title": r.get("title", ""), "body": r.get("body", ""), "href": r.get("href", "")} 
                for r in results]
    except Exception as e:
        logger.error(f"DDG search failed: {e}")
        return []

async def scrape_url(url: str, timeout: int = 10) -> str:
    """Scrape and extract text from URL"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)
            response.raise_for_status()
        return trafilatura.extract(response.text, include_comments=False, include_tables=True) or ""
    except Exception as e:
        logger.warning(f"Scraping failed for {url}: {e}")
        return ""

# ============================================================================
# Embeddings
# ============================================================================

def get_embedder():
    """Get or create sentence transformer"""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        logger.warning(f"Embeddings unavailable: {e}")
        return None

def embed_text(text: str, embedder=None) -> Optional[List[float]]:
    """Generate embedding for text"""
    if embedder is None: embedder = get_embedder()
    if embedder is None: return None
    try:
        return embedder.encode(text, convert_to_numpy=True).tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between vectors"""
    a, b = np.array(vec1), np.array(vec2)
    dot_product, norm_product = np.dot(a, b), np.linalg.norm(a) * np.linalg.norm(b)
    return float(dot_product / norm_product) if norm_product > 0 else 0.0

# ============================================================================
# Summarization
# ============================================================================

def summarize_text(text: str, max_length: int = 500) -> str:
    """Extractive summarization via sentence truncation"""
    if not text or len(text) <= max_length: return text
    sentences, summary, current_length = text.replace('\n', ' ').split('. '), [], 0
    for sentence in sentences:
        if current_length + len(sentence) <= max_length:
            summary.append(sentence)
            current_length += len(sentence)
        else:
            break
    return '. '.join(summary) + ('.' if summary else '')

async def summarize_with_llm(
    text: str,
    model: str = "meta/llama-3.1-8b-instruct",
    base_url: str = "http://llm_client:9000/v1"
) -> Optional[str]:
    """LLM-based executive summary with strong prompt"""
    try:
        from langchain_nvidia import ChatNVIDIA
        llm = ChatNVIDIA(model=model, base_url=base_url, max_tokens=1024)
        
        prompt = """You are an expert research analyst creating an executive summary.

REQUIREMENTS:
- Synthesize ALL key information into a cohesive narrative
- Cite sources naturally: "According to [Source]..." or "Research shows..."
- Use clear topic transitions between ideas
- Include specific facts, data points, and actionable insights
- Write in professional prose (NO bullet points or lists)
- Create substantial paragraphs that tell a complete story
- Be thorough - the reader should understand the full picture from this alone

SOURCES:
{text}

EXECUTIVE SUMMARY:"""
        
        response = await llm.ainvoke([("user", prompt.format(text=text[:8000]))])
        return response.content
    except Exception as e:
        logger.warning(f"LLM summarization failed: {e}")
        return None

# ============================================================================
# Cache Operations
# ============================================================================

def extract_sorted_hrefs(results: List[Dict]) -> List[str]:
    return sorted([r.get("href", "") for r in results if r.get("href")])

async def get_cached_result(
    query: str,
    similarity_threshold: float = 0.95,
    database_url: Optional[str] = None
) -> Optional[Dict]:
    """Retrieve by exact match or semantic similarity"""
    query_hash = hash_query(query)
    
    async with get_session(database_url) as session:
        # Exact match
        result = await session.execute(select(CacheEntry).where(CacheEntry.query_hash == query_hash))
        entry = result.scalars().first()
        
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            return {
                "source": "cache-exact", "query": entry.query_text, "results": entry.results,
                "summary": entry.summary, "cached_at": entry.created_at.isoformat(),
                "access_count": entry.access_count
            }
        
        # Semantic similarity
        query_emb = embed_text(query)
        if query_emb:
            result = await session.execute(select(CacheEntry).where(CacheEntry.embeddings.isnot(None)))
            for entry in result.scalars():
                cached_emb = entry.embeddings.get("query") if entry.embeddings else None
                if cached_emb and cosine_similarity(query_emb, cached_emb) >= similarity_threshold:
                    entry.access_count += 1
                    entry.last_accessed = datetime.utcnow()
                    return {
                        "source": "cache-similarity", "query": entry.query_text, "results": entry.results,
                        "summary": entry.summary, "cached_hrefs": extract_sorted_hrefs(entry.results),
                        "cached_at": entry.created_at.isoformat(), "access_count": entry.access_count
                    }
        return None

async def save_to_cache(
    query: str, results: List[Dict], summary: Optional[str] = None, database_url: Optional[str] = None
) -> bool:
    """Save search results to cache"""
    query_hash, query_emb = hash_query(query), embed_text(query)
    embeddings = {"query": query_emb} if query_emb else None
    
    async with get_session(database_url) as session:
        try:
            result = await session.execute(select(CacheEntry).where(CacheEntry.query_hash == query_hash))
            entry = result.scalars().first()
            if entry:
                entry.results, entry.summary, entry.embeddings = results, summary, embeddings
                entry.last_accessed = datetime.utcnow()
            else:
                entry = CacheEntry(query_hash=query_hash, query_text=query, results=results, 
                                   embeddings=embeddings, summary=summary)
                session.add(entry)
            return True
        except Exception as e:
            logger.error(f"Cache save failed: {e}")
            return False

async def get_cache_stats(database_url: Optional[str] = None) -> Dict:
    """Get cache statistics"""
    async with get_session(database_url) as session:
        total = await session.scalar(select(func.count(CacheEntry.id)))
        result = await session.execute(select(CacheEntry).order_by(CacheEntry.created_at.desc()).limit(1))
        recent = result.scalars().first()
        return {
            "total_queries": total or 0,
            "last_cached": recent.created_at.isoformat() if recent else None,
            "database_url": database_url or get_database_url()
        }

async def clear_cache(database_url: Optional[str] = None) -> int:
    """Clear all cache entries"""
    async with get_session(database_url) as session:
        count = await session.scalar(select(func.count(CacheEntry.id))) or 0
        await session.execute(CacheEntry.__table__.delete())
        return count

# ============================================================================
# Main Aggregation Function
# ============================================================================

async def cached_ddg_search(
    query: str, *, max_results: int = 10, use_cache: bool = True,
    similarity_threshold: float = 0.95, scrape_content: bool = False,
    summarize_each: bool = False, summarize_all: bool = False,
    use_llm_summary: bool = False, return_cached_scraped: bool = True,
    return_cached_summary: bool = True, database_url: Optional[str] = None
) -> Dict:
    """
    Main DDG cache search: cache → live → scrape → summarize → save
    
    Strategy:
    - Exact match: Return full cached results including summary
    - Semantic match: Return cached results, but regenerate summary
    - Cache insufficient: Mix cached + live results
    - Live failure: Fall back to cached results only
    
    Returns: {source, query, results, summary, scraped_count, cached}
    """
    
    cached_results = []
    cache_source = None
    
    # Check cache
    if use_cache:
        with tracer.start_as_current_span("check_cache") as span:
            span.set_attribute("query", query)
            span.set_attribute("max_results", max_results)
            cached = await get_cached_result(query, similarity_threshold, database_url)
            
            if cached:
                cache_source = cached.get("source")
                span.set_attribute("cache_hit", True)
                span.set_attribute("cache_type", cache_source)
                span.set_attribute("cached_results_count", len(cached.get("results", [])))
                
                # EXACT MATCH: Return everything including summary
                if cache_source == "cache-exact":
                    # Filter based on flags
                    if not return_cached_scraped:
                        for r in cached.get("results", []):
                            r.pop("scraped_content", None)
                            r.pop("summary", None)
                    if not return_cached_summary:
                        cached["summary"] = None
                    else:
                        # Compare against self if cached_hrefs not stored
                        current_hrefs = extract_sorted_hrefs(cached.get("results", []))
                        cached_hrefs = cached.get("cached_hrefs") or current_hrefs
                        span.set_attribute("current_hrefs", current_hrefs)
                        span.set_attribute("cached_hrefs", cached_hrefs)
                        if current_hrefs != cached_hrefs:
                            logger.info("Cached summary ignored due to href mismatch.")
                            cached["summary"] = None
                    
                    # Check if sufficient results
                    cached_count = len(cached.get("results", []))
                    logger.info(f"Cache Hit Exactly. {cached_count = } found, {max_results = } needed")
                    if cached_count >= max_results:
                        return {**cached, "scraped_count": 0, "cached": True}
                    
                    # Not enough results - save what we have and supplement with live
                    cached_results = cached.get("results", [])
                    span.set_attribute("cache_insufficient", True)
                    span.set_attribute("cache_shortfall", max_results - cached_count)
                
                # SEMANTIC MATCH: Use cached results but regenerate summary
                elif cache_source == "cache-similarity":
                    cached_results = cached.get("results", [])
                    cached_count = len(cached_results)
                    span.set_attribute("semantic_match_count", cached_count)
                    
                    # Filter scraped content if not wanted
                    if not return_cached_scraped:
                        for r in cached_results:
                            r.pop("scraped_content", None)
                            r.pop("summary", None)
                    
                    # If we have enough results, skip live search but regenerate summary
                    logger.info(f"Cache Hit with Semantic Similarity. {cached_count = } found, {max_results = } needed")
                    if cached_count >= max_results:
                        span.set_attribute("using_cached_only", True)
                        # Continue to regenerate summary (don't return early)
                    else:
                        span.set_attribute("cache_insufficient", True)
                        span.set_attribute("cache_shortfall", max_results - cached_count)
            else:
                span.set_attribute("cache_hit", False)
    
    # Live search (skip if we have enough cached results from semantic match)
    live_results = []
    if not cached_results or len(cached_results) < max_results:
        with tracer.start_as_current_span("live_search") as span:
            span.set_attribute("query", query)
            span.set_attribute("max_results", max_results - len(cached_results))
            span.set_attribute("supplementing_cache", len(cached_results) > 0)

            logger.info(f"Starting Live Search: search_duckduckgo({query = }, max_results = {max_results - len(cached_results)})")
            try:
                live_results = await search_duckduckgo(query, max_results - len(cached_results))
                span.set_attribute("results_count", len(live_results))
                
                if not live_results and not cached_results:
                    span.set_attribute("no_results", True)
                    return {"source": "none", "query": query, "results": [], "summary": None,  "scraped_count": 0, "cached": False}
                
                # Filter out duplicates (by URL)
                cached_urls = {r.get("href") for r in cached_results}
                live_results = [r for r in live_results if r.get("href") not in cached_urls]
                span.set_attribute("unique_live_results", len(live_results))
                
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("error", str(e))
                
                logger.warning(f"Exception Encountered. Trying to fallback to cached entries")
                # FALLBACK: Use cached results if live search fails
                if cached_results:
                    span.set_attribute("falling_back_to_cache", True)
                    results = cached_results[:max_results]
                    
                    # For semantic matches, regenerate summary even on fallback
                    if cache_source == "cache-similarity" and summarize_all:
                        with tracer.start_as_current_span("regenerate_summary_fallback") as sum_span:
                            all_text = f"Original Query Request: {query}\n\n" + "\n\n".join(
                                f"Title: {r.get('title', 'N/A')}\nContent: {r.get('scraped_content') or r.get('body', 'N/A')}"
                                for r in results
                            )
                            logger.warning(f"Summarizing in fallback phase based on {len(results)} cache hits")
                            if use_llm_summary:
                                summary = await summarize_with_llm(all_text) or summarize_text(all_text, max_length=1000)
                            else:
                                summary = summarize_text(all_text, max_length=1000)
                            sum_span.set_attribute("regenerated", True)
                    else:
                        summary = None
                    
                    return {"source": "cache-fallback", "query": query, "results": results, 
                            "summary": summary, "scraped_count": 0, "cached": False, "error": str(e)}
                else:
                    return {"source": "error", "query": query, "results": [], "summary": None, 
                            "error": str(e), "scraped_count": 0, "cached": False}
    
    # Combine cached + live results
    results = cached_results + live_results
    
    # Scrape content
    scraped_count = 0
    if scrape_content:
        with tracer.start_as_current_span("scrape_content") as span:
            # Only scrape new (live) results that don't already have content
            to_scrape = [r for r in live_results if not r.get("scraped_content")]
            span.set_attribute("urls_to_scrape", len(to_scrape))
            
            async def scrape_and_attach(result: Dict) -> Dict:
                nonlocal scraped_count
                url = result.get("href", "")
                if url:
                    content = await scrape_url(url)
                    if content:
                        result["scraped_content"] = content
                        scraped_count += 1
                return result

            logger.info(f"Reading source of {len(to_scrape)} sources")
            scraped = await asyncio.gather(*[scrape_and_attach(r) for r in to_scrape], return_exceptions=True)
            scraped = [r for r in scraped if isinstance(r, dict)]
            span.set_attribute("scraped_count", scraped_count)
            span.set_attribute("scrape_success_rate", scraped_count / len(to_scrape) if to_scrape else 0)
    
    # Summarize each (batched concurrency)
    if summarize_each:
        with tracer.start_as_current_span("summarize_each") as span:
            to_summarize = [r for r in results if not r.get("summary")]
            total = len(to_summarize)
            span.set_attribute("results_to_summarize", total)
            logger.info(f"Summarizing each of {total} sources for pre-final result")

            if total == 0:
                span.add_event("No results require summarization")
            else:
                semaphore = asyncio.Semaphore(4)
                completed = 0

                async def summarize_single(idx, result):
                    nonlocal completed
                    async with semaphore:
                        text = result.get("scraped_content") or result.get("body", "")
                        if not text.strip():
                            result["summary"] = ""
                            completed += 1
                            return result
                        try:
                            if use_llm_summary:
                                llm_summary = await summarize_with_llm(text)
                                result["summary"] = llm_summary if llm_summary else summarize_text(text)
                            else:
                                result["summary"] = summarize_text(text)
                        except Exception as e:
                            logger.warning(f"Summarization failed for idx={idx}: {e}")
                            result["summary"] = ""
                        finally:
                            completed += 1
                            if completed % 2 == 0 or completed == total:
                                span.add_event(
                                    f"Summarized {completed}/{total}",
                                    {"completed": completed, "total": total}
                                )
                    return result

                summarized_results = await asyncio.gather(
                    *[summarize_single(i, r) for i, r in enumerate(to_summarize)]
                )

                # Merge summaries back into original results
                for s in summarized_results:
                    idx = results.index(next(r for r in results if r.get("href") == s.get("href")))
                    results[idx] = s

                span.set_attribute("summaries_generated", sum(1 for r in results if r.get("summary")))
                span.add_event("All summaries generated")

    # Summarize all - ALWAYS regenerate for semantic matches or mixed results
    summary = None
    if summarize_all:
        with tracer.start_as_current_span("summarize_all") as span:
            all_text = f"Original Query Request: {query}\n\n" + "\n\n".join(
                f"Title: {r.get('title', 'N/A')}\nContent: {r.get('scraped_content') or r.get('body', 'N/A')}"
                for r in results
            )
            logger.info(f"Summarizing all {len(results)} sources for final result")
            span.set_attribute("total_text_length", len(all_text))
            span.set_attribute("regenerating", cache_source != "cache-exact")
            
            if use_llm_summary:
                llm_summary = await summarize_with_llm(all_text)
                summary = llm_summary if llm_summary else summarize_text(all_text, max_length=1000)
            else:
                summary = summarize_text(all_text, max_length=1000)
            
            span.set_attribute("summary_length", len(summary) if summary else 0)
            span.set_attribute("used_llm", use_llm_summary and summary is not None)
    
    # Save to cache - save mixed or new results
    cached = False
    if use_cache and live_results:  # Only save if we got new results
        with tracer.start_as_current_span("save_cache") as span:
            span.set_attribute("query", query)
            span.set_attribute("results_count", len(results))
            span.set_attribute("has_summary", summary is not None)
            span.set_attribute("mixed_results", len(cached_results) > 0)
            cached = await save_to_cache(query, results, summary, database_url)
            span.set_attribute("saved", cached)
    
    # Determine final source
    if cached_results and live_results:
        source = "mixed"
    elif cached_results:
        source = cache_source or "cache"
    else:
        source = "live"
    
    return {"source": source, "query": query, "results": results, "summary": summary,
            "scraped_count": scraped_count, "cached": cached}

# ============================================================================
# Convenience Functions
# ============================================================================

async def quick_search(query: str, max_results: int = 5) -> List[Dict]:
    """Quick search - just results"""
    result = await cached_ddg_search(
        query, max_results=max_results, use_cache=True,
        scrape_content=False, summarize_each=False, summarize_all=False
    )
    return result.get("results", [])

async def search_and_summarize(query: str, max_results: int = 10) -> Dict:
    """Deep search - scraping + LLM summaries"""
    return await cached_ddg_search(
        query, max_results=max_results, use_cache=True,
        scrape_content=True, summarize_each=False, 
        summarize_all=True, use_llm_summary=True
    )

# ============================================================================
# Demo
# ============================================================================

async def demo():
    """Demo the system"""
    print("Initializing database...")
    await init_database()
    
    print("\n" + "="*60)
    print("First search (expecting live)...")
    r1 = await cached_ddg_search("NVIDIA DIGITS systems", max_results=3, summarize_all=True, use_llm_summary=True)
    print(f"Source: {r1['source']}, Results: {len(r1['results'])}")
    print(f"Summary: {r1.get('summary', 'N/A')[:300]}...")
    
    print("\n" + "="*60)
    print("Second search (expecting cache)...")
    r2 = await cached_ddg_search("NVIDIA DIGITS systems", max_results=3)
    print(f"Source: {r2['source']}, Results: {len(r2['results'])}")
    
    print("\n" + "="*60)
    stats = await get_cache_stats()
    print("Cache stats:", stats)

if __name__ == "__main__":
    asyncio.run(demo())