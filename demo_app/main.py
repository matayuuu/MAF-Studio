import csv
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse

app = FastAPI(title="Insurance CRM Demo")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Data loading helpers ──────────────────────────────────────────────────────

def load_csv(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _customers():
    return load_csv("customers.csv")

def _products():
    return load_csv("products.csv")

def _contracts():
    return load_csv("contracts.csv")

def _activities():
    return load_csv("activities.csv")


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def index(request: Request):
    html_path = TEMPLATES_DIR / "index.html"
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


# ── API: Dashboard stats ───────────────────────────────────────────────────────

@app.get("/api/dashboard")
async def dashboard():
    customers = _customers()
    contracts = _contracts()
    activities = _activities()

    total_customers = len(customers)
    active_contracts = sum(1 for c in contracts if c["contract_status"] == "有効")
    inactive_contracts = sum(1 for c in contracts if c["contract_status"] != "有効")
    total_premium = sum(int(c["monthly_premium"]) for c in contracts if c["contract_status"] == "有効")

    # Contracts by product
    products = _products()
    product_map = {p["product_id"]: p["product_name"] for p in products}
    product_counts: dict[str, int] = {}
    for ct in contracts:
        pname = product_map.get(ct["product_id"], ct["product_id"])
        product_counts[pname] = product_counts.get(pname, 0) + 1

    # Recent activities (last 5)
    sorted_acts = sorted(activities, key=lambda a: a["activity_date"], reverse=True)[:5]

    return {
        "total_customers": total_customers,
        "active_contracts": active_contracts,
        "inactive_contracts": inactive_contracts,
        "total_monthly_premium": total_premium,
        "product_distribution": product_counts,
        "recent_activities": sorted_acts,
    }


# ── API: Customers ─────────────────────────────────────────────────────────────

@app.get("/api/customers")
async def get_customers(
    search: str = Query(None),
):
    customers = _customers()
    if search:
        q = search.lower()
        customers = [
            c for c in customers
            if q in c["last_name"] + c["first_name"]
            or q in c["last_name_kana"] + c["first_name_kana"]
            or q in c.get("email", "")
            or q in c.get("phone", "")
        ]
    return customers


@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str):
    customers = _customers()
    customer = next((c for c in customers if c["customer_id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Attach contracts
    contracts = _contracts()
    products = _products()
    product_map = {p["product_id"]: p for p in products}
    customer_contracts = []
    for ct in contracts:
        if ct["customer_id"] == customer_id:
            ct_copy = dict(ct)
            ct_copy["product"] = product_map.get(ct["product_id"], {})
            customer_contracts.append(ct_copy)

    # Attach activities
    activities = _activities()
    customer_activities = sorted(
        [a for a in activities if a["customer_id"] == customer_id],
        key=lambda a: a["activity_date"],
        reverse=True,
    )

    return {
        "customer": customer,
        "contracts": customer_contracts,
        "activities": customer_activities,
    }


# ── API: Products ──────────────────────────────────────────────────────────────

@app.get("/api/products")
async def get_products():
    return _products()


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    products = _products()
    product = next((p for p in products if p["product_id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    contracts = [c for c in _contracts() if c["product_id"] == product_id]
    return {"product": product, "contracts": contracts}


# ── API: Activities ────────────────────────────────────────────────────────────

@app.get("/api/activities")
async def get_activities(customer_id: str = Query(None)):
    activities = _activities()
    if customer_id:
        activities = [a for a in activities if a["customer_id"] == customer_id]
    return sorted(activities, key=lambda a: a["activity_date"], reverse=True)
