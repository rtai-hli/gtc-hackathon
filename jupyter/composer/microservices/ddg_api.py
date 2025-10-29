"""
api.py - Fixed FastAPI service for DDG cache system
Improvements:
- Better error handling and logging
- Proper async/await patterns
- Fixed response models
- Better validation
"""
import os
import sys
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from ddg_cache import (
    cached_ddg_search, quick_search, search_and_summarize,
    get_cache_stats, clear_cache, get_cached_result
)

sys.path.append('/dli/task/composer/microservices')
from observability import get_observability
logger, tracer, _, traced = get_observability("ddg-api")

# ============================================================================
# Request/Response Models
# ============================================================================

class SearchRequest(BaseModel):
    """Main search request with validation"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    max_results: int = Field(10, ge=1, le=50, description="Maximum results to return")
    use_cache: bool = Field(True, description="Enable cache lookup")
    similarity_threshold: float = Field(0.95, ge=0.5, le=1.0, description="Semantic similarity threshold")
    scrape_content: bool = Field(False, description="Scrape full content from URLs")
    summarize_each: bool = Field(False, description="Generate summary for each result")
    summarize_all: bool = Field(False, description="Generate aggregate summary")
    use_llm_summary: bool = Field(False, description="Use LLM for summarization")
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class QuickSearchRequest(BaseModel):
    """Quick search with minimal options"""
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: int = Field(5, ge=1, le=20)
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class SearchResult(BaseModel):
    """Individual search result"""
    title: str
    body: str
    href: str
    scraped_content: Optional[str] = None
    summary: Optional[str] = None

class SearchResponse(BaseModel):
    """Standardized search response"""
    source: str = Field(..., description="Result source: live, cache-exact, cache-similarity, mixed, etc.")
    query: str
    results: List[Dict[str, Any]]
    summary: Optional[str] = None
    scraped_count: int = 0
    cached: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StatsResponse(BaseModel):
    """Cache statistics response"""
    total_queries: int
    last_cached: Optional[str]
    database_url: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    total_queries: int
    last_cached: Optional[str]

class BatchSearchRequest(BaseModel):
    """Batch search multiple queries"""
    queries: List[str] = Field(..., min_items=1, max_items=10, description="List of queries to search")
    max_results_per_query: int = Field(5, ge=1, le=20, description="Max results per query")
    use_cache: bool = Field(True, description="Use cache for searches")
    summarize: bool = Field(False, description="Generate summaries")

class BatchSearchResponse(BaseModel):
    """Batch search response"""
    batch_size: int
    results: List[Dict[str, Any]]
    successful: int
    failed: int = 0

# ============================================================================
# Application Setup
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown"""
    logger.info("🚀 Starting DDG Cache API...")
    
    try:
        from ddg_cache import init_database
        await init_database()
        stats = await get_cache_stats()
        logger.info(f"✓ Database ready: {stats['total_queries']} cached queries")
    except Exception as e:
        logger.error(f"✗ Database init failed: {e}", exc_info=True)
    
    yield
    
    logger.info("👋 Shutting down DDG Cache API")

app = FastAPI(
    title="DDG Cache API",
    description="Intelligent DuckDuckGo search cache with semantic similarity and LLM summarization",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Error Handling
# ============================================================================

class APIError(Exception):
    """Base API exception"""
    def __init__(self, message: str, status_code: int = 500, details: Dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors"""
    logger.error(f"API Error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url)
        }
    )

# ============================================================================
# Health & Stats Endpoints
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API root - service info"""
    return {
        "service": "DDG Cache API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "stats": "/stats"
    }

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health():
    """Health check with cache statistics"""
    try:
        stats = await get_cache_stats()
        return HealthResponse(
            status="healthy",
            service="ddg-cache-api",
            total_queries=stats['total_queries'],
            last_cached=stats['last_cached']
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "ddg-cache-api",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )

@app.get("/stats", response_model=StatsResponse, tags=["Monitoring"])
async def stats():
    """Detailed cache statistics"""
    try:
        stats_data = await get_cache_stats()
        return StatsResponse(**stats_data)
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}", exc_info=True)
        raise APIError(f"Failed to retrieve stats: {str(e)}", status_code=500)

# ============================================================================
# Search Endpoints
# ============================================================================

@app.post("/search", response_model=SearchResponse, tags=["Search"])
@traced("search")
async def search(req: SearchRequest):
    """
    Main search endpoint with full configuration
    
    Strategy:
    - Check cache (exact or semantic match)
    - Fall back to live DuckDuckGo search
    - Optionally scrape full content
    - Optionally generate summaries (extractive or LLM)
    - Cache results for future queries
    """
    try:
        logger.info(f"Search request: query='{req.query}', max_results={req.max_results}, use_cache={req.use_cache}")
        
        result = await cached_ddg_search(
            query=req.query,
            max_results=req.max_results,
            use_cache=req.use_cache,
            similarity_threshold=req.similarity_threshold,
            scrape_content=req.scrape_content,
            summarize_each=req.summarize_each,
            summarize_all=req.summarize_all,
            use_llm_summary=req.use_llm_summary
        )
        
        # Add metadata
        result['metadata'] = {
            'cache_enabled': req.use_cache,
            'scraping_enabled': req.scrape_content,
            'llm_summary_enabled': req.use_llm_summary,
            'similarity_threshold': req.similarity_threshold
        }
        
        logger.info(f"Search completed: source={result['source']}, results={len(result['results'])}")
        
        return SearchResponse(**result)
    
    except Exception as e:
        logger.error(f"Search failed for query '{req.query}': {e}", exc_info=True)
        raise APIError(
            f"Search failed: {str(e)}", 
            status_code=500, 
            details={"query": req.query, "error_type": type(e).__name__}
        )

@app.post("/search/quick", tags=["Search"])
@traced("quick_search")
async def search_quick_endpoint(req: QuickSearchRequest):
    """
    Quick search - fast results without scraping or summarization
    
    Perfect for: autocomplete, quick lookups, low-latency scenarios
    """
    try:
        logger.info(f"Quick search: query='{req.query}', max_results={req.max_results}")
        
        results = await quick_search(req.query, req.max_results)
        
        return {
            "query": req.query,
            "results": results,
            "count": len(results),
            "mode": "quick"
        }
    except Exception as e:
        logger.error(f"Quick search failed: {e}", exc_info=True)
        raise APIError(
            f"Quick search failed: {str(e)}", 
            status_code=500,
            details={"query": req.query, "error_type": type(e).__name__}
        )

@app.post("/search/deep", response_model=SearchResponse, tags=["Search"])
@traced("deep_search")
async def search_deep_endpoint(req: QuickSearchRequest):
    """
    Deep search - comprehensive with full scraping and LLM summarization
    
    Perfect for: research, detailed analysis, comprehensive reports
    """
    try:
        logger.info(f"Deep search: query='{req.query}', max_results={req.max_results}")
        
        result = await search_and_summarize(req.query, req.max_results)
        result['metadata'] = {
            'mode': 'deep',
            'scraping_enabled': True,
            'llm_summary_enabled': True
        }
        
        logger.info(f"Deep search completed: results={len(result['results'])}, scraped={result.get('scraped_count', 0)}")
        
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Deep search failed: {e}", exc_info=True)
        raise APIError(
            f"Deep search failed: {str(e)}", 
            status_code=500,
            details={"query": req.query, "error_type": type(e).__name__}
        )

# ============================================================================
# Cache Management Endpoints
# ============================================================================

@app.get("/cache/lookup", tags=["Cache"])
@traced("cache_lookup")
async def cache_lookup(
    query: str = Query(..., min_length=1, description="Query to look up"),
    similarity_threshold: float = Query(0.95, ge=0.5, le=1.0, description="Similarity threshold")
):
    """
    Check if query exists in cache (exact or semantic match)
    Returns cached result or 404
    """
    try:
        logger.info(f"Cache lookup: query='{query}', threshold={similarity_threshold}")
        
        result = await get_cached_result(query, similarity_threshold)
        
        if result is None:
            logger.info(f"Cache miss for query: '{query}'")
            raise HTTPException(
                status_code=404, 
                detail={
                    "message": "Query not found in cache",
                    "query": query,
                    "threshold": similarity_threshold
                }
            )
        
        logger.info(f"Cache hit: source={result['source']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache lookup failed: {e}", exc_info=True)
        raise APIError(
            f"Cache lookup failed: {str(e)}", 
            status_code=500,
            details={"query": query, "error_type": type(e).__name__}
        )

@app.delete("/cache/clear", tags=["Cache"])
@traced("clear_cache")
async def clear_cache_endpoint():
    """
    Clear all cache entries
    
    ⚠️ Use with caution - this cannot be undone!
    """
    try:
        logger.warning("Cache clear requested")
        
        count = await clear_cache()
        
        logger.info(f"Cache cleared: {count} entries deleted")
        
        return {
            "success": True,
            "deleted": count,
            "message": f"Successfully cleared {count} cache entries"
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}", exc_info=True)
        raise APIError(
            f"Failed to clear cache: {str(e)}", 
            status_code=500,
            details={"error_type": type(e).__name__}
        )

# ============================================================================
# Batch Operations
# ============================================================================

@app.post("/search/batch", response_model=BatchSearchResponse, tags=["Search"])
@traced("batch_search")
async def batch_search(req: BatchSearchRequest):
    """
    Search multiple queries in parallel
    
    Useful for: comparison searches, multi-topic research
    Limit: 10 queries per batch
    """
    try:
        import asyncio
        
        logger.info(f"Batch search: {len(req.queries)} queries, max_results={req.max_results_per_query}")
        
        async def search_one(query: str) -> Dict[str, Any]:
            try:
                result = await cached_ddg_search(
                    query=query,
                    max_results=req.max_results_per_query,
                    use_cache=req.use_cache,
                    summarize_all=req.summarize,
                    use_llm_summary=req.summarize
                )
                result['success'] = True
                return result
            except Exception as e:
                logger.error(f"Batch search failed for '{query}': {e}")
                return {
                    "query": query, 
                    "error": str(e), 
                    "error_type": type(e).__name__,
                    "results": [],
                    "success": False
                }
        
        results = await asyncio.gather(*[search_one(q) for q in req.queries], return_exceptions=False)
        
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        logger.info(f"Batch search completed: {successful} successful, {failed} failed")
        
        return BatchSearchResponse(
            batch_size=len(req.queries),
            results=results,
            successful=successful,
            failed=failed
        )
    
    except Exception as e:
        logger.error(f"Batch search failed: {e}", exc_info=True)
        raise APIError(
            f"Batch search failed: {str(e)}", 
            status_code=500,
            details={"queries_count": len(req.queries), "error_type": type(e).__name__}
        )

# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    DEBUG_MODE = os.getenv("DEBUG", "0") == "1"
    PORT = int(os.getenv("PORT", "7861"))
    
    logger.info(f"Starting server on port {PORT} (debug={'ON' if DEBUG_MODE else 'OFF'})")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG_MODE,
        log_level="debug" if DEBUG_MODE else "info",
        access_log=True
    )