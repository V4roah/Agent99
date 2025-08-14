from typing import List, Dict, Any, Optional
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from models.vector import VectorItem
import json


class VectorStore:
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2", index_path: str = "models/vector_index.faiss"):
        self.model_name = model_name
        self.index_path = index_path
        try:
            self.encoder = SentenceTransformer(model_name)
            self.dimension = self.encoder.get_sentence_embedding_dimension()
        except Exception as e:
            print(f"⚠️ Error cargando modelo {model_name}: {e}")
            print("🔄 Usando modelo alternativo más pequeño...")
            try:
                self.encoder = SentenceTransformer("paraphrase-MiniLM-L3-v2")
                self.dimension = self.encoder.get_sentence_embedding_dimension()
            except Exception as e2:
                print(f"❌ Error con modelo alternativo: {e2}")
                print("🔄 Deshabilitando embeddings temporalmente...")
                self.encoder = None
                self.dimension = 384  # Dimensión por defecto

        # Inicializar FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.items: List[VectorItem] = []
        self.load_index()

    def add_item(self, item: VectorItem) -> str:
        """Añade un item al vector store"""
        if not self.encoder:
            print("⚠️ Embeddings deshabilitados - guardando solo texto")
            self.items.append(item)
            return item.id

        if not item.embedding:
            try:
                item.embedding = self.encoder.encode([item.text])[0]
            except Exception as e:
                print(f"⚠️ Error generando embedding: {e}")
                self.items.append(item)
                return item.id

        # Añadir al index
        self.index.add(item.embedding.reshape(1, -1))
        self.items.append(item)

        return item.id

    def add_batch(self, items: List[VectorItem]) -> List[str]:
        """Añade múltiples items en batch"""
        if not self.encoder:
            print("⚠️ Embeddings deshabilitados - guardando solo texto")
            for item in items:
                self.items.append(item)
            return [item.id for item in items]

        texts = [item.text for item in items]
        try:
            embeddings = self.encoder.encode(texts)

            # Añadir embeddings al index
            self.index.add(embeddings)

            # Actualizar items con sus embeddings
            for item, embedding in zip(items, embeddings):
                item.embedding = embedding
                self.items.append(item)
        except Exception as e:
            print(f"⚠️ Error en batch: {e}")
            for item in items:
                self.items.append(item)

        return [item.id for item in items]

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca items similares al query"""
        if not self.encoder:
            print("⚠️ Embeddings deshabilitados - búsqueda por texto simple")
            # Búsqueda simple por texto
            results = []
            query_lower = query.lower()
            for item in self.items:
                if query_lower in item.text.lower():
                    results.append({
                        "id": item.id,
                        "text": item.text,
                        "metadata": item.metadata,
                        "similarity_score": 0.8  # Score falso
                    })
            return results[:k]

        try:
            query_embedding = self.encoder.encode([query])

            # Buscar en el index
            scores, indices = self.index.search(query_embedding, k)

            # Verificar que hay resultados
            if len(scores) == 0 or len(indices) == 0:
                return []

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.items):
                    item = self.items[idx]
                    results.append({
                        "id": item.id,
                        "text": item.text,
                        "metadata": item.metadata,
                        "similarity_score": float(score)
                    })

            return results
        except Exception as e:
            print(f"⚠️ Error en búsqueda: {e}")
            return []

    def save_index(self):
        """Guarda el index y los items"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        if self.encoder:
            # Guardar FAISS index
            faiss.write_index(self.index, self.index_path)

        # Guardar items (sin embeddings para ahorrar espacio)
        items_data = []
        for item in self.items:
            items_data.append({
                "id": item.id,
                "text": item.text,
                "metadata": item.metadata
            })

        items_path = self.index_path.replace(".faiss", "_items.json")
        with open(items_path, 'w', encoding='utf-8') as f:
            json.dump(items_data, f, ensure_ascii=False, indent=2)

    def load_index(self):
        """Carga el index guardado"""
        if os.path.exists(self.index_path) and self.encoder:
            try:
                self.index = faiss.read_index(self.index_path)

                # Cargar items
                items_path = self.index_path.replace(".faiss", "_items.json")
                if os.path.exists(items_path):
                    with open(items_path, 'r', encoding='utf-8') as f:
                        items_data = json.load(f)

                    self.items = []
                    for item_data in items_data:
                        item = VectorItem(
                            id=item_data["id"],
                            text=item_data["text"],
                            metadata=item_data["metadata"]
                        )
                        self.items.append(item)

            except Exception as e:
                print(f"⚠️ Error loading index: {e}")
                # Si hay error, crear index vacío
                self.index = faiss.IndexFlatIP(self.dimension)
                self.items = []
        else:
            # Cargar solo items si no hay embeddings
            items_path = self.index_path.replace(".faiss", "_items.json")
            if os.path.exists(items_path):
                try:
                    with open(items_path, 'r', encoding='utf-8') as f:
                        items_data = json.load(f)

                    self.items = []
                    for item_data in items_data:
                        item = VectorItem(
                            id=item_data["id"],
                            text=item_data["text"],
                            metadata=item_data["metadata"]
                        )
                        self.items.append(item)
                except Exception as e:
                    print(f"⚠️ Error loading items: {e}")
                    self.items = []


# Instancia global del vector store
vector_store = VectorStore()
