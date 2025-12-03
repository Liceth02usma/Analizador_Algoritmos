import chromadb
from app.data.seed_algorithms import KNOWN_ALGORITHMS

class AlgorithmKnowledgeBase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlgorithmKnowledgeBase, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("📚 [KnowledgeBase] Inicializando ChromaDB...")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="algorithms_library")
        
        if self.collection.count() == 0:
            self._seed_database()

    def _seed_database(self):
        print("🌱 [KnowledgeBase] Base vacía. Cargando algoritmos semilla...")
        ids = []
        documents = [] 
        metadatas = [] 

        for algo in KNOWN_ALGORITHMS:
            ids.append(algo["id"])
            # Embeddings semánticos
            documents.append(f"{algo['name']}. {algo['keywords']}")
            metadatas.append({
                "pseudocode": algo["pseudocode"],
                "official_name": algo["name"],
                "keywords": algo["keywords"] # Guardamos keywords para búsqueda exacta
            })

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ [KnowledgeBase] {len(ids)} algoritmos cargados.")

    def search_algorithm(self, query: str, threshold: float = 0.65): # <--- SUBIMOS EL UMBRAL DEFAULT
        """
        Estrategia Híbrida:
        1. Búsqueda exacta (rápida y precisa para nombres cortos).
        2. Búsqueda vectorial (inteligente para descripciones largas).
        """
        query_lower = query.lower().strip()

        # --- 1. FILTRO DE PALABRAS CLAVE (EXACT MATCH) ---
        # Buscamos manualmente en la memoria RAM antes de ir a los vectores
        # Esto soluciona tu problema con "factorial"
        for algo in KNOWN_ALGORITHMS:
            name_match = query_lower in algo["name"].lower()
            keyword_match = any(k.strip() in query_lower for k in algo["keywords"].split(","))
            
            # Si el usuario escribió exactamente el nombre o una keyword clave
            if name_match or (keyword_match and len(query_lower.split()) < 3):
                print(f"🎯 [KnowledgeBase] Match exacto por texto: {algo['name']}")
                return algo["pseudocode"]

        # --- 2. BÚSQUEDA VECTORIAL (SEMÁNTICA) ---
        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )

        if not results["distances"] or not results["distances"][0]:
            return None

        distance = results["distances"][0][0]
        
        # Ajustamos el umbral a algo más permisivo (0.6 - 0.7 suele ser bueno para MiniLM)
        if distance < threshold:
            metadata = results["metadatas"][0][0]
            print(f"🎯 [KnowledgeBase] Match semántico encontrado: {metadata['official_name']} (Dist: {distance:.3f})")
            return metadata["pseudocode"]
        
        print(f"⚠️ [KnowledgeBase] Sin coincidencias suficientes (Mejor: {distance:.3f} > {threshold})")
        return None