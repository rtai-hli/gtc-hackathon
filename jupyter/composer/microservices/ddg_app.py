"""
app.py - Gradio frontend for DDG cache system

Features:
- Search with manual cache control
- Aggregated cache entry management
- Individual result/chunk editing
- Real-time progress tracking
- Professional UI/UX
"""
import gradio as gr
import pandas as pd
import json
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from ddg_cache import (
    init_database, get_cache_stats, clear_cache,
    get_session, CacheEntry, hash_query,
    search_duckduckgo, scrape_url, summarize_text, summarize_with_llm,
    get_cached_result, save_to_cache
)
from sqlalchemy import select, desc, func
from sqlalchemy.orm.attributes import flag_modified

sys.path.append('/dli/task/composer/microservices')
from observability import get_observability
logger, _, _, _ = get_observability("ddg-gradio")

# ============================================================================
# Theme Configuration
# ============================================================================

THEME = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="slate",
    neutral_hue="gray",
    font=[gr.themes.GoogleFont("Inter"), "system-ui"],
).set(
    body_background_fill="white",
    button_primary_background_fill="#76b900",
    button_primary_background_fill_hover="#5a8f00",
)

# ============================================================================
# Global State for Manual Caching
# ============================================================================

_last_search_results = {
    "query": None,
    "results": None,
    "summary": None
}

# ============================================================================
# Helper Functions
# ============================================================================

def truncate_text(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis"""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text

def format_timestamp(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_table_click(evt: gr.SelectData, df: pd.DataFrame) -> str:
    """Extract ID from clicked row in dataframe"""
    if evt.index is not None and len(evt.index) >= 1:
        row_idx = evt.index[0]
        if not df.empty and row_idx < len(df):
            return str(df.iloc[row_idx, 0])
    return ""

def parse_chunk_table_click(evt: gr.SelectData, df: pd.DataFrame) -> Tuple[str, int]:
    """Extract Entry ID and Result Index from clicked chunk row"""
    if evt.index is not None and len(evt.index) >= 1:
        row_idx = evt.index[0]
        if not df.empty and row_idx < len(df):
            entry_id = str(df.iloc[row_idx, 0])
            result_idx = int(df.iloc[row_idx, 2])
            return entry_id, result_idx
    return "", 0

# ============================================================================
# Cache Operations - Aggregated View
# ============================================================================

async def load_cache_table(limit: int = 100) -> pd.DataFrame:
    """Load aggregated cache entries"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).order_by(desc(CacheEntry.last_accessed)).limit(limit)
            )
            entries = result.scalars().all()
            
            if not entries:
                return pd.DataFrame(columns=["Entry ID", "Query", "Results", "Has Summary", "Created", "Last Access", "Access Count"])
            
            data = []
            for e in entries:
                data.append({
                    "Entry ID": e.query_hash[:12],
                    "Query": truncate_text(e.query_text, 80),
                    "Results": len(e.results) if e.results else 0,
                    "Has Summary": "Yes" if e.summary else "No",
                    "Created": format_timestamp(e.created_at),
                    "Last Access": format_timestamp(e.last_accessed),
                    "Access Count": e.access_count
                })
            
            return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        return pd.DataFrame()

async def get_cache_stats_text() -> str:
    """Get formatted cache statistics"""
    try:
        stats = await get_cache_stats()
        db_display = stats['database_url'].split('@')[-1] if '@' in stats['database_url'] else stats['database_url']
        return f"""**Total Cached Queries:** {stats['total_queries']}  
**Last Cached:** {stats['last_cached'] or 'Never'}  
**Database:** `{db_display}`"""
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return f"**Error:** {str(e)}"

# ============================================================================
# Cache Operations - Chunk/Result Level View
# ============================================================================

async def load_chunk_cache_table(query_id: str = "") -> Tuple[pd.DataFrame, str]:
    """Load individual results/chunks from cache entries"""
    try:
        async with get_session() as session:
            if query_id.strip():
                result = await session.execute(
                    select(CacheEntry).where(CacheEntry.query_hash.like(f"{query_id.strip()}%"))
                )
                entries = [result.scalars().first()]
                if not entries[0]:
                    return pd.DataFrame(), f"Entry with ID '{query_id}' not found"
            else:
                result = await session.execute(
                    select(CacheEntry).order_by(desc(CacheEntry.last_accessed)).limit(50)
                )
                entries = result.scalars().all()
            
            if not entries or not any(entries):
                return pd.DataFrame(columns=["Entry ID", "Query", "Result Index", "Title", "URL", "Has Content", "Has Summary"]), "No cache entries found"
            
            data = []
            for entry in entries:
                if not entry or not entry.results:
                    continue
                    
                for idx, result_item in enumerate(entry.results):
                    data.append({
                        "Entry ID": entry.query_hash[:12],
                        "Query": truncate_text(entry.query_text, 60),
                        "Result Index": idx,
                        "Title": truncate_text(result_item.get('title', 'N/A'), 60),
                        "URL": truncate_text(result_item.get('href', 'N/A'), 50),
                        "Has Content": "Yes" if result_item.get('scraped_content') else "No",
                        "Has Summary": "Yes" if result_item.get('summary') else "No"
                    })
            
            return pd.DataFrame(data), f"Loaded {len(data)} individual results from {len([e for e in entries if e])} cache entries"
    except Exception as e:
        logger.error(f"Failed to load chunk cache: {e}")
        return pd.DataFrame(), f"Error: {str(e)}"

async def get_chunk_details(entry_id: str, result_index: int) -> Tuple[str, str, str, str, str, str]:
    """Get details of a specific chunk/result for editing"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return ("", "", "", "", "", f"Entry '{entry_id}' not found")
            
            if not entry.results or result_index >= len(entry.results):
                return ("", "", "", "", "", f"Result #{result_index} not found in entry")
            
            chunk = entry.results[result_index]
            
            info = f"""**Entry ID:** {entry.query_hash[:16]}...  
**Query:** {entry.query_text}  
**Result Index:** {result_index}  
**Created:** {format_timestamp(entry.created_at)}"""
            
            title = chunk.get('title', '')
            url = chunk.get('href', '')
            scraped_content = chunk.get('scraped_content', '')
            summary = chunk.get('summary', '')
            
            return (info, title, url, scraped_content, summary, "")
    except Exception as e:
        logger.error(f"Failed to get chunk details: {e}")
        return ("", "", "", "", "", f"Error: {str(e)}")

async def update_chunk(entry_id: str, result_index: int, title: str, url: str, 
                       scraped_content: str, summary: str) -> Tuple[str, pd.DataFrame]:
    """Update a specific chunk/result in cache"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return (f"Entry '{entry_id}' not found", pd.DataFrame())
            
            if not entry.results or result_index >= len(entry.results):
                return (f"Result #{result_index} not found", pd.DataFrame())
            
            entry.results[result_index]['title'] = title
            entry.results[result_index]['href'] = url
            if scraped_content.strip():
                entry.results[result_index]['scraped_content'] = scraped_content
            if summary.strip():
                entry.results[result_index]['summary'] = summary
            
            flag_modified(entry, "results")
            await session.commit()
            
            new_table, _ = await load_chunk_cache_table()
            return (f"Successfully updated result #{result_index} in entry {entry_id[:12]}", new_table)
    except Exception as e:
        logger.error(f"Failed to update chunk: {e}")
        return (f"Error: {str(e)}", pd.DataFrame())

async def delete_chunk(entry_id: str, result_index: int) -> Tuple[str, pd.DataFrame]:
    """Delete a specific chunk/result from cache entry"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return (f"Entry '{entry_id}' not found", pd.DataFrame())
            
            if not entry.results or result_index >= len(entry.results):
                return (f"Result #{result_index} not found", pd.DataFrame())
            
            del entry.results[result_index]
            
            if not entry.results:
                await session.delete(entry)
                msg = f"Deleted result #{result_index} and removed empty entry {entry_id[:12]}"
            else:
                flag_modified(entry, "results")
                msg = f"Deleted result #{result_index} from entry {entry_id[:12]}"
            
            await session.commit()
            
            new_table, _ = await load_chunk_cache_table()
            return (msg, new_table)
    except Exception as e:
        logger.error(f"Failed to delete chunk: {e}")
        return (f"Error: {str(e)}", pd.DataFrame())

# ============================================================================
# Aggregated Entry Operations
# ============================================================================

async def get_entry_details(entry_id: str) -> Tuple[str, str, str, str]:
    """Get full aggregated entry details for editing"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return ("", "", "", f"Entry '{entry_id}' not found")
            
            info = f"""**Query Hash:** {entry.query_hash[:16]}...  
**Query Text:** {entry.query_text}  
**Results Count:** {len(entry.results) if entry.results else 0}  
**Created:** {format_timestamp(entry.created_at)}  
**Last Accessed:** {format_timestamp(entry.last_accessed)}  
**Access Count:** {entry.access_count}"""
            
            results_json = json.dumps(entry.results, indent=2) if entry.results else "[]"
            summary_text = entry.summary or ""
            
            return (info, results_json, summary_text, "")
    except Exception as e:
        logger.error(f"Failed to get entry details: {e}")
        return ("", "", "", f"Error: {str(e)}")

async def update_entry(entry_id: str, results_json: str, summary: str) -> Tuple[str, pd.DataFrame]:
    """Update aggregated entry (all results + summary)"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return (f"Entry '{entry_id}' not found", pd.DataFrame())
            
            if results_json.strip():
                try:
                    new_results = json.loads(results_json)
                    if not isinstance(new_results, list):
                        return ("Results must be a JSON array", pd.DataFrame())
                    entry.results = new_results
                except json.JSONDecodeError as e:
                    return (f"Invalid JSON: {str(e)}", pd.DataFrame())
            
            if summary.strip():
                entry.summary = summary
            
            await session.commit()
            
            new_table = await load_cache_table()
            return (f"Successfully updated entry {entry_id[:12]}", new_table)
    except Exception as e:
        logger.error(f"Failed to update entry: {e}")
        return (f"Error: {str(e)}", pd.DataFrame())

async def delete_entry(entry_id: str) -> Tuple[str, pd.DataFrame]:
    """Delete entire cache entry"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(CacheEntry).where(CacheEntry.query_hash.like(f"{entry_id.strip()}%"))
            )
            entry = result.scalars().first()
            
            if not entry:
                return (f"Entry '{entry_id}' not found", pd.DataFrame())
            
            await session.delete(entry)
            await session.commit()
            
            new_table = await load_cache_table()
            return (f"Deleted entry {entry_id[:12]}", new_table)
    except Exception as e:
        logger.error(f"Failed to delete entry: {e}")
        return (f"Error: {str(e)}", pd.DataFrame())

async def clear_all_cache() -> Tuple[str, str, pd.DataFrame]:
    """Clear entire cache"""
    try:
        count = await clear_cache()
        stats = await get_cache_stats_text()
        table = await load_cache_table()
        return (f"Cleared {count} cache entries", stats, table)
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return (f"Error: {str(e)}", "", pd.DataFrame())

# ============================================================================
# Search Operations
# ============================================================================

async def execute_search(
    query: str,
    max_results: int,
    use_cache: bool,
    scrape: bool,
    summarize: bool,
    use_llm: bool,
    progress=gr.Progress()
) -> Tuple[str, pd.DataFrame, str, str]:
    """
    Execute search with progress tracking and a progressively accumulating execution trace.
    Returns [status_md, results_df, summary_box, trace_box]
    """
    query = query.strip()
    blank_results_df = pd.DataFrame(columns=["#", "Title", "URL", "Has Content", "Has Summary"])

    execution_trace = {
        "source": "live",
        "query": query,
        "results_count": 0,
        "scraped_count": 0,
        "cached": False,
        "stages": [],  # chronological list of progress messages
    }
    
    def make_return(status_msg, df=blank_results_df, summary_msg="", trace_box=execution_trace):
        ## Utility for constructing return
        if isinstance(trace_box, dict):
            trace_box["timestamp"] = datetime.utcnow().isoformat()
            trace_out = json.dumps(execution_trace, indent=2)
        else: 
            trace_out = str(trace_box)
        return (status_msg, df, summary_msg, trace_out)
    
    if not query:
        return make_return("Enter a search query to begin", trace_box="")

    _last_search_results.update({"query": None, "results": None, "summary": None})
    results: List[Dict] = []
    scraped_count = 0
    overall_summary = None

    def log_stage(pct: float, desc: str):
        """Update Gradio progress + append trace step"""
        pct = min(max(pct, 0.0), 1.0)
        msg = f"[{pct*100:.0f}%] {desc}"
        execution_trace["stages"].append(msg)
        progress(pct, desc=desc)

    try:
        log_stage(0.0, "Initializing search")
        await asyncio.sleep(0.1)

        # Cache Lookup
        if use_cache:
            log_stage(0.1, "Checking cache...")
            cached = await get_cached_result(query, similarity_threshold=0.95)
            if cached:
                log_stage(0.3, f"Cache hit: {cached['source']}")
                execution_trace["cached"] = True
                execution_trace["source"] = cached["source"]
                execution_trace["results_count"] = len(cached.get("results", []))

                status = (
                    f"**Source:** {cached['source']} (From Cache)\n"
                    f"**Query:** {cached.get('query', query)}\n"
                    f"**Results Found:** {len(cached.get('results', []))}\n"
                    f"**Cached At:** {cached.get('cached_at', 'N/A')}\n"
                    f"**Access Count:** {cached.get('access_count', 'N/A')}"
                )

                _last_search_results.update({
                    "query": query,
                    "results": cached.get("results", []),
                    "summary": cached.get("summary"),
                })

                # Build DataFrame
                results_list = cached.get("results", [])
                df = pd.DataFrame([{
                    "#": i + 1,
                    "Title": truncate_text(r.get("title", "N/A"), 60),
                    "URL": truncate_text(r.get("href", "N/A"), 60),
                    "Has Content": "Yes" if r.get("scraped_content") else "No",
                    "Has Summary": "Yes" if r.get("summary") else "No",
                } for i, r in enumerate(results_list)])

                summary = cached.get("summary") or "No summary available"
                trace = json.dumps(execution_trace, indent=2)
                log_stage(1.0, "Complete (from cache)")
                return make_return(status, df, summary, trace)

        # Live Search
        log_stage(0.2, "Searching DuckDuckGo...")
        results = await search_duckduckgo(query, max_results)
        if not results:
            log_stage(1.0, "[EXIT] No results found")
            return make_return("No results found from DuckDuckGo", summary="No results to summarize")

        execution_trace["results_count"] = len(results)
        log_stage(0.4, f"Found {len(results)} results")

        if scrape:
            log_stage(0.5, f"Scraping {len(results)} URLs...")

            semaphore = asyncio.Semaphore(6)
            scraped_count = 0

            async def scrape_with_progress(idx: int, result: Dict) -> Dict:
                nonlocal scraped_count
                async with semaphore:
                    url = result.get("href")
                    if not url:
                        return result
                    progress(0.5 + 0.2 * (idx / len(results)), desc=f"Scraping URL {idx+1}/{len(results)}...")
                    try:
                        content = await scrape_url(url)
                        if content:
                            result["scraped_content"] = content
                            scraped_count += 1
                    except Exception as e:
                        logger.warning(f"Scrape failed: {url} ({e})")
                    return result

            results = await asyncio.gather(*[scrape_with_progress(i, r) for i, r in enumerate(results)])
            execution_trace["scraped_count"] = scraped_count
            log_stage(0.7, f"Scraped {scraped_count}/{len(results)} pages")

        # Summarize Each (batched concurrency)
        if summarize and results:
            log_stage(0.75, f"Summarizing {len(results)} results...")
            semaphore = asyncio.Semaphore(4)
            total = len(results)
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
                        if use_llm:
                            llm_sum = await summarize_with_llm(text)
                            result["summary"] = llm_sum or summarize_text(text)
                        else:
                            result["summary"] = summarize_text(text)
                    except Exception as e:
                        logger.warning(f"Summarization failed for {idx}: {e}")
                        result["summary"] = ""
                    finally:
                        completed += 1
                        if completed % 2 == 0 or completed == total:
                            log_stage(0.75 + 0.1 * (completed / total), f"Summarized {completed}/{total}")
                return result

            results = await asyncio.gather(*[summarize_single(i, r) for i, r in enumerate(results)])
            log_stage(0.85, "Summaries complete")

        # Aggregate Summary
        if summarize and results:
            log_stage(0.9, "Generating aggregate summary...")
            result_strs = [f"Title: {r.get('title', 'N/A')}\nContent: {r.get('scraped_content') or r.get('body', 'N/A')}" for r in results]
            all_text = "Original Query: " + query + "\n\n" + "\n\n".join(result_strs)
            try:
                if use_llm:
                    overall_summary = await summarize_with_llm(all_text)
                    if not overall_summary:
                        overall_summary = summarize_text(all_text, max_length=1000)
                else:
                    overall_summary = summarize_text(all_text, max_length=1000)
            except Exception as e:
                overall_summary = f"[LLM summary failed: {e}]"
            log_stage(0.95, "Aggregate summary complete")

        # Store results for manual caching
        _last_search_results.update({"query": query, "results": results, "summary": overall_summary})

        # Format results
        log_stage(0.98, "Formatting results...")
        df = pd.DataFrame([{
            "#": i + 1,
            "Title": truncate_text(r.get("title", "N/A"), 60),
            "URL": truncate_text(r.get("href", "N/A"), 60),
            "Has Content": "Yes" if r.get("scraped_content") else "No",
            "Has Summary": "Yes" if r.get("summary") else "No",
        } for i, r in enumerate(results)])

        status = (
            f"**Source:** Live Search\n"
            f"**Query:** {query}\n"
            f"**Results Found:** {len(results)}\n"
            f"**Pages Scraped:** {scraped_count}\n"
            f"**Status:** Not yet cached - use Save to Cache below"
        )

        summary_text = overall_summary or "No summary generated"
        log_stage(1.0, "Search complete")

        return make_return(status, df, summary_text)

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        log_stage(1.0, f"Search failed: {e}")
        execution_trace["error"] = str(e)
        return make_return(f"**Search Error:** {str(e)}")


async def save_search_to_cache(progress=gr.Progress()) -> str:
    """Manually save the last search results to cache"""
    try:
        if not _last_search_results["query"] or not _last_search_results["results"]:
            return "No search results to save. Perform a search first."
        
        progress(0.3, desc="Saving to cache...")
        await asyncio.sleep(0.1)
        
        success = await save_to_cache(
            _last_search_results["query"],
            _last_search_results["results"],
            _last_search_results["summary"]
        )
        
        if success:
            progress(1.0, desc="Saved")
            await asyncio.sleep(0.1)
            return f"Successfully saved '{_last_search_results['query']}' to cache with {len(_last_search_results['results'])} results"
        else:
            return "Failed to save to cache. Check logs for details."
    
    except Exception as e:
        logger.error(f"Save to cache failed: {e}", exc_info=True)
        return f"Error saving to cache: {str(e)}"

# ============================================================================
# Gradio Interface
# ============================================================================

def create_app():
    """Build professional Gradio interface"""
    
    with gr.Blocks(theme=THEME, title="DDG Cache Management") as demo:
        
        gr.Markdown("# DuckDuckGo Cache Management System")
        gr.Markdown("Intelligent search caching with semantic similarity and LLM summarization")
        
        # ====================================================================
        # Search Tab
        # ====================================================================
        
        with gr.Tab("Search"):
            with gr.Row():
                with gr.Column(scale=3):
                    query_input = gr.Textbox(
                        label="Search Query",
                        placeholder="Enter your search query...",
                        lines=2
                    )
                    
                    with gr.Row():
                        search_btn = gr.Button("Search", variant="primary", scale=2)
                        quick_btn = gr.Button("Quick Search", scale=1)
                        deep_btn = gr.Button("Deep Summary", scale=1)
                
                with gr.Column(scale=2):
                    gr.Markdown("### Search Options")
                    max_results = gr.Slider(1, 50, value=10, step=1, label="Maximum Results")
                    use_cache = gr.Checkbox(value=True, label="[QS/DS] Check Cache First")
                    scrape = gr.Checkbox(value=False, label="[DS] Scrape Full Content from URLs")
                    summarize = gr.Checkbox(value=False, label="[DS] Generate Summaries (DS)")
                    use_llm = gr.Checkbox(value=False, label="[DS] Use LLM for Summarization")
            
            status_md = gr.Markdown("Ready to search")
            
            with gr.Row():
                save_cache_btn = gr.Button("Save to Cache", variant="secondary")
                cache_save_status = gr.Markdown("")
            
            with gr.Tabs():
                with gr.Tab("Results"):
                    results_df = gr.Dataframe(
                        wrap=True,
                        interactive=False,
                        column_widths=["5%", "35%", "40%", "10%", "10%"]
                    )
                
                with gr.Tab("Summary"):
                    summary_box = gr.Textbox(
                        label="Aggregate Summary",
                        lines=20,
                        interactive=False,
                        show_copy_button=True
                    )
                
                with gr.Tab("Debug Trace"):
                    trace_box = gr.Code(language="json", label="Execution Trace")
            
            gr.Examples(
                examples=[
                    ["NVIDIA DIGITS systems", 10, True, False, True, False],
                    ["Latest GPU technology", 5, True, True, True, True],
                    ["Machine learning frameworks", 10, False, False, False, False]
                ],
                inputs=[query_input, max_results, use_cache, scrape, summarize, use_llm],
                label="Example Queries"
            )
            
            # Wire up search
            search_inputs = [query_input, max_results, use_cache, scrape, summarize, use_llm]
            search_outputs = [status_md, results_df, summary_box, trace_box]
            
            search_btn.click(execute_search, inputs=search_inputs, outputs=search_outputs)
            
            async def quick_search_wrapper(q):
                return await execute_search(q, 5, True, False, False, False)
            
            async def deep_search_wrapper(q):
                return await execute_search(q, 10, True, True, True, True)
            
            quick_btn.click(quick_search_wrapper, inputs=[query_input], outputs=search_outputs)
            deep_btn.click(deep_search_wrapper, inputs=[query_input], outputs=search_outputs)
            
            # Wire up save button
            save_cache_btn.click(save_search_to_cache, outputs=[cache_save_status])
        
        # ====================================================================
        # Aggregated Cache Tab
        # ====================================================================
        
        with gr.Tab("Aggregated Cache") as agg_tab:
            gr.Markdown("### Cached Query Entries")
            gr.Markdown("""
            **Instructions:** Click any row in the table below to automatically load it into the editor.
            You can then edit the JSON results or summary text directly. All fields support copy-paste.
            """)
            
            with gr.Row():
                refresh_agg_btn = gr.Button("Refresh", scale=1)
                clear_all_btn = gr.Button("Clear All Cache", variant="stop", scale=1)
            
            cache_stats_md = gr.Markdown()
            cache_table = gr.Dataframe(
                wrap=True,
                interactive=False,
                column_widths=["10%", "30%", "8%", "10%", "15%", "15%", "12%"]
            )
            
            gr.Markdown("---")
            gr.Markdown("### Edit Cache Entry")
            
            with gr.Row():
                agg_entry_id = gr.Textbox(
                    label="Entry ID (auto-populated when you click a row above)",
                    placeholder="Click a row or enter ID manually",
                    scale=3,
                    interactive=True
                )
                load_agg_btn = gr.Button("Load Entry", scale=1)
            
            agg_entry_info = gr.Markdown()
            
            with gr.Row():
                with gr.Column():
                    agg_results_editor = gr.Code(
                        label="All Results (JSON Array)",
                        language="json",
                        lines=15,
                        interactive=True
                    )
                
                with gr.Column():
                    agg_summary_editor = gr.Textbox(
                        label="Aggregated Summary",
                        lines=15,
                        interactive=True,
                        show_copy_button=True
                    )
            
            with gr.Row():
                save_agg_btn = gr.Button("Save Changes", variant="primary", scale=2)
                delete_agg_btn = gr.Button("Delete Entry", variant="stop", scale=1)
            
            agg_status_md = gr.Markdown()
            
            # Wire up aggregated cache
            async def refresh_agg():
                stats = await get_cache_stats_text()
                table = await load_cache_table()
                return (stats, table)
            
            refresh_agg_btn.click(refresh_agg, outputs=[cache_stats_md, cache_table])
            clear_all_btn.click(clear_all_cache, outputs=[agg_status_md, cache_stats_md, cache_table])
            
            # Auto-load on row click
            async def on_agg_row_click(evt: gr.SelectData):
                try:
                    current_df = await load_cache_table()
                    entry_id = parse_table_click(evt, current_df)
                    
                    if entry_id:
                        info, results, summary, status = await get_entry_details(entry_id)
                        return (entry_id, info, results, summary, status)
                    
                    return ("", "", "", "", "Click on a row to load")
                except Exception as e:
                    logger.error(f"Row click error: {e}")
                    return ("", "", "", "", f"Error: {str(e)}")
            
            cache_table.select(
                on_agg_row_click,
                outputs=[agg_entry_id, agg_entry_info, agg_results_editor, agg_summary_editor, agg_status_md]
            )
            
            load_agg_btn.click(
                get_entry_details,
                inputs=[agg_entry_id],
                outputs=[agg_entry_info, agg_results_editor, agg_summary_editor, agg_status_md]
            )
            
            save_agg_btn.click(
                update_entry,
                inputs=[agg_entry_id, agg_results_editor, agg_summary_editor],
                outputs=[agg_status_md, cache_table]
            )
            
            delete_agg_btn.click(
                delete_entry,
                inputs=[agg_entry_id],
                outputs=[agg_status_md, cache_table]
            )
        
        # ====================================================================
        # Chunk Cache Tab
        # ====================================================================
        
        with gr.Tab("Chunk Cache") as chunk_tab:
            gr.Markdown("### Individual Result Management")
            gr.Markdown("""
            **Instructions:** Click any row in the table to automatically load that specific result for editing.
            You can edit the title, URL, content, or summary for individual search results.
            Filter by Entry ID to see results from a specific cache entry.
            """)
            
            with gr.Row():
                chunk_filter_id = gr.Textbox(
                    label="Filter by Entry ID (optional)",
                    placeholder="Leave empty to show all results",
                    scale=3
                )
                refresh_chunk_btn = gr.Button("Refresh", scale=1)
            
            chunk_status_md = gr.Markdown()
            chunk_table = gr.Dataframe(
                wrap=True,
                interactive=False,
                column_widths=["12%", "23%", "7%", "23%", "20%", "8%", "7%"]
            )
            
            gr.Markdown("---")
            gr.Markdown("### Edit Individual Result")
            
            with gr.Row():
                chunk_entry_id = gr.Textbox(
                    label="Entry ID (auto-populated)",
                    placeholder="Click a row above",
                    scale=2,
                    interactive=True
                )
                chunk_result_idx = gr.Number(
                    label="Result Index (auto-populated)",
                    value=0,
                    precision=0,
                    scale=1,
                    interactive=True
                )
                load_chunk_btn = gr.Button("Load", scale=1)
            
            chunk_info_md = gr.Markdown()
            
            chunk_title = gr.Textbox(
                label="Title",
                lines=2,
                interactive=True,
                show_copy_button=True
            )
            chunk_url = gr.Textbox(
                label="URL",
                lines=1,
                interactive=True,
                show_copy_button=True
            )
            
            with gr.Row():
                with gr.Column():
                    chunk_content = gr.Textbox(
                        label="Scraped Content",
                        lines=12,
                        placeholder="Full content from webpage",
                        interactive=True,
                        show_copy_button=True
                    )
                
                with gr.Column():
                    chunk_summary = gr.Textbox(
                        label="Result Summary",
                        lines=12,
                        placeholder="Summary for this specific result",
                        interactive=True,
                        show_copy_button=True
                    )
            
            with gr.Row():
                save_chunk_btn = gr.Button("Save Changes", variant="primary", scale=2)
                delete_chunk_btn = gr.Button("Delete Result", variant="stop", scale=1)
            
            chunk_edit_status_md = gr.Markdown()
            
            # Wire up chunk cache
            async def refresh_chunks(filter_id=""):
                table, status = await load_chunk_cache_table(filter_id)
                return (status, table)
            
            refresh_chunk_btn.click(
                refresh_chunks,
                inputs=[chunk_filter_id],
                outputs=[chunk_status_md, chunk_table]
            )
            
            # Auto-load on row click
            async def on_chunk_row_click(evt: gr.SelectData):
                try:
                    current_df, _ = await load_chunk_cache_table(chunk_filter_id.value or "")
                    entry_id, result_idx = parse_chunk_table_click(evt, current_df)
                    
                    if entry_id:
                        info, title, url, content, summary, status = await get_chunk_details(entry_id, result_idx)
                        return (entry_id, result_idx, info, title, url, content, summary, status)
                    
                    return ("", 0, "", "", "", "", "", "Click on a row to load")
                except Exception as e:
                    logger.error(f"Chunk row click error: {e}")
                    return ("", 0, "", "", "", "", "", f"Error: {str(e)}")
            
            chunk_table.select(
                on_chunk_row_click,
                outputs=[chunk_entry_id, chunk_result_idx, chunk_info_md, chunk_title, 
                        chunk_url, chunk_content, chunk_summary, chunk_edit_status_md]
            )
            
            load_chunk_btn.click(
                get_chunk_details,
                inputs=[chunk_entry_id, chunk_result_idx],
                outputs=[chunk_info_md, chunk_title, chunk_url, chunk_content, chunk_summary, chunk_edit_status_md]
            )
            
            save_chunk_btn.click(
                update_chunk,
                inputs=[chunk_entry_id, chunk_result_idx, chunk_title, chunk_url, chunk_content, chunk_summary],
                outputs=[chunk_edit_status_md, chunk_table]
            )
            
            delete_chunk_btn.click(
                delete_chunk,
                inputs=[chunk_entry_id, chunk_result_idx],
                outputs=[chunk_edit_status_md, chunk_table]
            )

            agg_tab.select(refresh_agg, outputs=[cache_stats_md, cache_table])
            chunk_tab.select(refresh_chunks, inputs=[chunk_filter_id], outputs=[chunk_status_md, chunk_table])
        
        # ====================================================================
        # API Documentation Tab
        # ====================================================================
        
        with gr.Tab("API Documentation"):
            gr.Markdown("""
            ## REST API Endpoints
            
            **Base URL:** `http://localhost:7861`
            
            ### Search Endpoints
            
            **POST /search** - Full search with all options
            ```bash
            curl -X POST http://localhost:7861/search \\
              -H "Content-Type: application/json" \\
              -d '{
                "query": "NVIDIA GPUs",
                "max_results": 10,
                "use_cache": true,
                "scrape_content": true,
                "summarize_all": true,
                "use_llm_summary": true
              }'
            ```
            
            **POST /search/quick** - Fast search without extras
            ```bash
            curl -X POST http://localhost:7861/search/quick \\
              -H "Content-Type: application/json" \\
              -d '{"query": "machine learning", "max_results": 5}'
            ```
            
            **POST /search/deep** - Comprehensive search with scraping and LLM
            ```bash
            curl -X POST http://localhost:7861/search/deep \\
              -H "Content-Type: application/json" \\
              -d '{"query": "AI trends", "max_results": 10}'
            ```
            
            **POST /search/batch** - Search multiple queries
            ```bash
            curl -X POST http://localhost:7861/search/batch \\
              -H "Content-Type: application/json" \\
              -d '{
                "queries": ["query1", "query2", "query3"],
                "max_results_per_query": 5,
                "use_cache": true
              }'
            ```
            
            ### Cache Endpoints
            
            **GET /cache/lookup?query=your+query&similarity_threshold=0.95** - Check cache
            
            **DELETE /cache/clear** - Clear entire cache
            
            **GET /stats** - Get cache statistics
            
            **GET /health** - Health check
            
            ### Interactive Documentation
            
            - **Swagger UI:** [http://localhost:7861/docs](http://localhost:7861/docs)
            - **ReDoc:** [http://localhost:7861/redoc](http://localhost:7861/redoc)
            
            ### Python SDK Usage
            
            ```python
            from ddg_cache import cached_ddg_search, quick_search, search_and_summarize
            
            # Basic search
            result = await cached_ddg_search("your query", max_results=10)
            
            # Quick search (no extras)
            results = await quick_search("fast query", max_results=5)
            
            # Deep search (scraping + LLM summaries)
            result = await search_and_summarize("comprehensive query", max_results=10)
            
            # Custom configuration
            result = await cached_ddg_search(
                query="your query",
                max_results=10,
                use_cache=True,
                scrape_content=True,
                summarize_all=True,
                use_llm_summary=True
            )
            
            # Access results
            for r in result['results']:
                print(f"Title: {r['title']}")
                print(f"URL: {r['href']}")
                if r.get('scraped_content'):
                    print(f"Content: {r['scraped_content'][:200]}...")
            
            # Access aggregated summary
            if result.get('summary'):
                print(f"Overall: {result['summary']}")
            ```
            
            ### Cache Strategy
            
            - **Exact Match:** Returns cached results with original summary
            - **Semantic Match:** Returns cached results, regenerates summary
            - **Mixed:** Combines cached and live results when insufficient
            - **Fallback:** Uses cache if live search fails
            
            ### Technology Stack
            
            - **Search:** DuckDuckGo API
            - **Database:** PostgreSQL (async SQLAlchemy)
            - **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
            - **LLM:** NVIDIA NIMs (Llama 3.1 8B)
            - **Scraping:** Trafilatura + HTTPX (async)
            - **Observability:** OpenTelemetry + Jaeger
            
            ### Performance Metrics
            
            - **Cache Hit (Exact):** < 50ms
            - **Cache Hit (Semantic):** < 200ms
            - **Live Search:** 1-3 seconds
            - **Scraping:** 100-500ms per URL (parallel)
            - **LLM Summary:** 2-5 seconds
            """)
        
        # Load initial data on startup
        async def load_initial_data():
            stats = await get_cache_stats_text()
            agg_table = await load_cache_table()
            chunk_table, chunk_msg = await load_chunk_cache_table()
            return (stats, agg_table, chunk_msg, chunk_table)
        
        demo.load(
            load_initial_data,
            outputs=[cache_stats_md, cache_table, chunk_status_md, chunk_table]
        )
    
    return demo

# ============================================================================
# Startup
# ============================================================================

async def startup():
    """Initialize system on startup"""
    logger.info("Initializing DDG Cache Gradio UI...")
    try:
        await init_database()
        stats = await get_cache_stats()
        logger.info(f"Database ready: {stats['total_queries']} cached queries")
        return True
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Initialize database
    asyncio.run(startup())
    
    # Create and launch app
    app = create_app()
    app.queue(status_update_rate="auto").launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_api=False
    )