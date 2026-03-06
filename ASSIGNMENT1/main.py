from fastapi import FastAPI, Query
app = FastAPI()
@app.get("/")
def home():
    return {"message": "My First FastApi program!"}

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook','price':  99,  'category': 'Stationery',  'in_stock': False },
    {'id': 3, 'name': 'USB Hub','price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set','price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop stand','price': 1299,'category': 'Electronics', 'in_stock': False},
    {'id': 6, 'name': 'Mechanical Keyboard','price': 1600, 'category': 'Electronics',  'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 2000,'category': 'Electronics', 'in_stock': True }
]
 
# ── Endpoint 1  Return all products ─

@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/filter')
def filter_products(

    category:  str  = Query(None, description='Electronics or Stationery'),

    max_price: int  = Query(None, description='Maximum price'),

    in_stock:  bool = Query(None, description='True = in stock only')

):

    result = products          # start with all products

 

    if category:

        result = [p for p in result if p['category'] == category]

 

    if max_price:

        result = [p for p in result if p['price'] <= max_price]

 

    if in_stock is not None:

        result = [p for p in result if p['in_stock'] == in_stock]

 

    return {'filtered_products': result, 'count': len(result)}

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered = [
        product for product in products
        if product["category"].lower() == category_name.lower()
    ]

    if not filtered:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered,
        "count": len(filtered)
    }

@app.get("/products/instock")
def get_instock_products():

    instock = [
        product for product in products
        if product["in_stock"] is True
    ]

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }

@app.get('/store/summary')
def store_summary():
    total_products = len(products)
    avg_price = sum(p['price'] for p in products) / total_products
    category_counts = {}
    for p in products:
        category_counts[p['category']] = category_counts.get(p['category'], 0) + 1
    return {
        'total_products': total_products,
        'average_price': round(avg_price, 2),
        'products_by_category': category_counts
    }

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matches = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not matches:
        return {"message": "No products matched your search"}

    return {
        "results": matches,
        "count": len(matches)
    }

@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}