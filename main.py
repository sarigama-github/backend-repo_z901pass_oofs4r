import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Vic Signature API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_str_id(doc: dict):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])  # add string id
        del doc["_id"]
    return doc

# Schemas
from schemas import Product, Category, Order


@app.get("/")
def read_root():
    return {"brand": "Vic Signature", "message": "Welcome to the Vic Signature backend"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Categories
@app.get("/api/categories")
def list_categories():
    cats = get_documents("category")
    return [to_str_id(c) for c in cats]

@app.post("/api/categories")
def create_category(cat: Category):
    cat_id = create_document("category", cat)
    return {"id": cat_id}

# Products
@app.get("/api/products")
def list_products(category: Optional[str] = None, q: Optional[str] = None):
    filters = {}
    if category:
        filters["category"] = category
    if q:
        filters["title"] = {"$regex": q, "$options": "i"}
    items = get_documents("product", filters)
    return [to_str_id(i) for i in items]

@app.post("/api/products")
def create_product(prod: Product):
    pid = create_document("product", prod)
    return {"id": pid}

# Orders
class OrderResponse(BaseModel):
    id: str

@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: Order):
    # naive total validation (trusting client subtotals here)
    if abs(order.subtotal + order.shipping - order.total) > 0.01:
        raise HTTPException(status_code=400, detail="Totals don't add up")
    oid = create_document("order", order)
    return {"id": oid}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
