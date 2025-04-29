def filtrar_por_description(products, description_part):
    return [p for p in products if description_part.lower() in p["product_description"].lower()]

def ordenar_por_preco(products, asc=True):
    return sorted(products, key=lambda p: p["product_price"], reverse=not asc)

def filtrar_por_id(products, id):
    return next((p for p in products if p["id"] == id), None)
