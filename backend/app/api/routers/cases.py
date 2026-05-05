from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Optional, Any
from app.core.supabase_client import supabase
from app.api.dependencies import get_current_user

router = APIRouter()

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

SUMMARY_FIELDS = "id, query, domain, created_at"
FULL_FIELDS    = "id, query, domain, created_at, answer"
QUERY_TRUNCATE = 150


def _shape_record(record: dict, expand: bool) -> dict:
    """
    Return a consistently-shaped record.
    - query is always truncated to QUERY_TRUNCATE chars in listing mode.
    - answer (full jsonb) is only included when expand=True.
    """
    out: dict[str, Any] = {
        "id":         record["id"],
        "query":      (record.get("query") or "")[:QUERY_TRUNCATE],
        "domain":     record.get("domain"),
        "created_at": record.get("created_at"),
    }
    if expand:
        out["answer"] = record.get("answer")
    return out


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@router.get("/", summary="List query history for the current user")
def get_cases(
    q:      Optional[str] = Query(None,  description="Keyword search on the query text field"),
    expand: bool          = Query(False, description="Include full answer+citations in each record"),
    page:   int           = Query(1,     ge=1,         description="Page number (1-indexed)"),
    limit:  int           = Query(20,    ge=1, le=100, description="Records per page"),
    user    = Depends(get_current_user),
):
    """
    Returns the authenticated user's RAG query history, sorted newest-first.

    - **q**: optional substring search on the `query` column (case-insensitive).
    - **expand**: when `true`, the full `answer` JSONB (including citations) is
      returned for every record. When omitted / `false`, `answer` is excluded.
    - Paginated via **page** / **limit**.
    """
    client = supabase.get_client()

    # Choose the select fields based on whether we need the answer blob
    select_fields = FULL_FIELDS if expand else SUMMARY_FIELDS

    db_query = (
        client.table("query_history")
        .select(select_fields, count="exact")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
    )

    # Optional full-text / substring search on the `query` column
    if q and q.strip():
        db_query = db_query.ilike("query", f"%{q.strip()}%")

    # Pagination
    offset = (page - 1) * limit
    db_query = db_query.range(offset, offset + limit - 1)

    try:
        response = db_query.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    records = [_shape_record(r, expand) for r in (response.data or [])]
    total   = response.count if hasattr(response, "count") and response.count is not None else len(records)

    return {
        "data":        records,
        "total_count": total,
        "page":        page,
        "limit":       limit,
        "has_more":    (offset + limit) < total,
    }


@router.get("/{case_id}", summary="Get a single query history record with full answer")
def get_case(
    case_id: str = Path(..., description="UUID of the query_history record"),
    user     = Depends(get_current_user),
):
    """
    Fetches a single record from `query_history` by its UUID.
    Always returns the full `answer` JSONB (including citations).
    Enforces ownership — a user can only read their own records.
    """
    client = supabase.get_client()

    try:
        response = (
            client.table("query_history")
            .select(FULL_FIELDS)
            .eq("id", case_id)
            .eq("user_id", user.id)   # ownership guard
            .single()
            .execute()
        )
    except Exception as e:
        # PostgREST raises an error (PGRST116) when .single() finds 0 rows
        raise HTTPException(status_code=404, detail="Case not found or access denied")

    if not response.data:
        raise HTTPException(status_code=404, detail="Case not found or access denied")

    return _shape_record(response.data, expand=True)
