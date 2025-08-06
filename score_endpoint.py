# API: Update Supplier Score
@app.post("/api/update-supplier-score")
async def api_update_supplier_score(request: Request):
    """
    Update supplier score (0-100 in jumps of 10)
    """
    from fastapi.responses import JSONResponse
    
    body = await request.json()
    supplier_id = body.get('supplier_id')
    score = body.get('score')
    
    if supplier_id is None:
        return JSONResponse(
            content={"error": "Supplier ID is required"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    if score is None or score < 0 or score > 100 or score % 10 != 0:
        return JSONResponse(
            content={"error": "Score must be 0-100 in jumps of 10"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update supplier score
        cursor.execute(
            "UPDATE suppliers SET score = %s WHERE id = %s",
            (score, supplier_id)
        )
        
        if cursor.rowcount == 0:
            return JSONResponse(
                content={"error": "Supplier not found"},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse(
            content={"success": True, "message": "Score updated successfully"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
