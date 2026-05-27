"""
Product Database — Vector search over a clothing product catalog.
Uses ChromaDB for lightweight, file-based vector similarity search.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class Product:
    """Represents a single clothing product."""

    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.brand = data.get("brand", "")
        self.category = data.get("category", "")
        self.subcategory = data.get("subcategory", "")
        self.colors = data.get("colors", [])
        self.fit = data.get("fit", "")
        self.material = data.get("material", "")
        self.price_range = data.get("price_range", "")
        self.occasions = data.get("occasions", [])
        self.seasons = data.get("seasons", [])
        self.body_type_match = data.get("body_type_match", [])
        self.description = data.get("description", "")
        self.style_tags = data.get("style_tags", [])
        self.gender = data.get("gender", "unisex")
        self._raw = data

    def to_search_text(self) -> str:
        """Generate a searchable text representation."""
        parts = [
            self.name,
            self.brand,
            self.category,
            self.subcategory,
            " ".join(self.colors),
            self.fit,
            self.material,
            " ".join(self.occasions),
            " ".join(self.seasons),
            " ".join(self.body_type_match),
            self.description,
            " ".join(self.style_tags),
        ]
        return " | ".join(filter(None, parts))

    def to_display_text(self) -> str:
        """Format for display in recommendations."""
        colors = "/".join(self.colors) if self.colors else "N/A"
        return (
            f"[{self.brand}] {self.name} "
            f"(顏色: {colors}, 版型: {self.fit}, "
            f"材質: {self.material}, 價位: {self.price_range})"
        )

    def to_dict(self) -> dict:
        return self._raw


class ProductDB:
    """Manages the product catalog with vector search capabilities."""

    def __init__(self):
        self.products: List[Product] = []
        self._collection = None
        self._client = None

    def load(self, path: str):
        """Load product catalog from a JSON file."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        products_data = data if isinstance(data, list) else data.get("products", [])
        self.products = [Product(p) for p in products_data]
        logger.info(f"Loaded {len(self.products)} products from {path}")
        self._build_index()

    def _build_index(self):
        """Build ChromaDB vector index from products."""
        try:
            import chromadb
            self._client = chromadb.Client()  # In-memory, ephemeral

            # Delete existing collection if it exists
            try:
                self._client.delete_collection("products")
            except Exception:
                pass

            self._collection = self._client.create_collection(
                name="products",
                metadata={"hnsw:space": "cosine"},
            )

            if not self.products:
                return

            documents = [p.to_search_text() for p in self.products]
            ids = [p.id for p in self.products]
            metadatas = [
                {
                    "category": p.category,
                    "brand": p.brand,
                    "fit": p.fit,
                    "gender": p.gender,
                    "price_range": p.price_range,
                }
                for p in self.products
            ]
            self._collection.add(
                documents=documents, ids=ids, metadatas=metadatas
            )
            logger.info(f"Built vector index with {len(self.products)} products")
        except ImportError:
            logger.warning(
                "chromadb not installed. Falling back to keyword search. "
                "Install with: pip install chromadb"
            )
            self._collection = None

    def search(
        self,
        query: str,
        top_k: int = 15,
        category_filter: str = None,
        gender_filter: str = None,
    ) -> List[Product]:
        """
        Search for products matching the query.
        
        Args:
            query: natural language search query (e.g., VLM features + scene)
            top_k: number of results to return
            category_filter: optional filter by category
            gender_filter: optional filter by gender
        """
        if self._collection is not None:
            return self._vector_search(query, top_k, category_filter, gender_filter)
        else:
            return self._keyword_search(query, top_k)

    def _vector_search(
        self, query: str, top_k: int, category_filter: str, gender_filter: str
    ) -> List[Product]:
        """ChromaDB vector similarity search."""
        where_filters = {}
        if category_filter:
            where_filters["category"] = category_filter
        if gender_filter:
            where_filters["gender"] = {"$in": [gender_filter, "unisex"]}

        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, len(self.products)),
            where=where_filters if where_filters else None,
        )

        matched_ids = results["ids"][0] if results["ids"] else []
        id_to_product = {p.id: p for p in self.products}
        return [id_to_product[pid] for pid in matched_ids if pid in id_to_product]

    def _keyword_search(self, query: str, top_k: int) -> List[Product]:
        """Simple keyword-based fallback search."""
        query_lower = query.lower()
        scored = []
        for p in self.products:
            text = p.to_search_text().lower()
            score = sum(1 for word in query_lower.split() if word in text)
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]

    def get_by_category(self, category: str) -> List[Product]:
        """Get all products in a category."""
        return [p for p in self.products if p.category == category]

    def add_products(self, products_data: List[dict]):
        """Add new products to the catalog."""
        new_products = [Product(p) for p in products_data]
        self.products.extend(new_products)
        self._build_index()  # Rebuild index
