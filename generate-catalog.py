import os
import json

USER = "onduboy"
REPO = "nuvio-collection-assets"
BRANCH = "main"
BASE_URL = f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@{BRANCH}"

COLLECTIONS_DIR = "collections"
OUTPUT_FILE = "catalog.json"
VALID_EXTENSIONS = ('.webp', '.png', '.jpg', '.jpeg', '.svg')

catalog = {}

if os.path.exists(COLLECTIONS_DIR):
    # 1. Recorre categorías (genres, streaming, discover, etc.)
    for category_name in sorted(os.listdir(COLLECTIONS_DIR)):
        category_path = os.path.join(COLLECTIONS_DIR, category_name)

        if os.path.isdir(category_path):
            category_items = []

            # 2. Recorre ítems dentro de cada categoría (horror, netflix, etc.)
            for item_name in sorted(os.listdir(category_path)):
                item_path = os.path.join(category_path, item_name)

                if os.path.isdir(item_path):
                    display_name = item_name.replace("-", " ").title()
                    assets = {}

                    # 3. Escanea imágenes dentro del ítem
                    for file_name in os.listdir(item_path):
                        if file_name.lower().endswith(VALID_EXTENSIONS):
                            asset_key = os.path.splitext(file_name)[0]
                            # Slashes '/' explícitos para evitar problemas si ejecutas el script en Windows
                            asset_rel_path = f"collections/{category_name}/{item_name}/{file_name}"
                            assets[asset_key] = f"{BASE_URL}/{asset_rel_path}"

                    # Solo agregamos el ítem si contiene al menos una imagen
                    if assets:
                        category_items.append({
                            "id": item_name,
                            "name": display_name,
                            "assets": assets
                        })

            # Solo agregamos la categoría al catálogo si tiene ítems con imágenes
            if category_items:
                catalog[category_name] = category_items

# Guardar catálogo
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"✅ ¡{OUTPUT_FILE} generado exitosamente!")