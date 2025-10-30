import os
import gc
import threading
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

class MemoryService:
    """
    Memory service with lazy-loading to minimize RAM usage.
    SentenceTransformer is only loaded when needed and can be unloaded.
    """
    
    def __init__(self):
        # Use local file storage for Qdrant if no URL provided
        self.qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_storage_v2")
        os.makedirs(self.qdrant_path, exist_ok=True)
        
        self.client = QdrantClient(path=self.qdrant_path)
        print(f"[MEMORY] Initialized Qdrant at path: {self.qdrant_path}")
        
        self.collection_name = "personal_memory"
        
        # LAZY LOADING: Don't load encoder at startup - saves ~2GB RAM
        self._encoder = None
        self._encoder_lock = threading.RLock()  # RLock allows nested acquisition
        self._last_encoder_use = 0
        
        # Auto-unload encoder after 5 minutes of inactivity
        self._unload_timeout = 300  # 5 minutes
        self._unload_timer = None
        
        self._ensure_collection()
        print("[MEMORY] Memory service initialized (encoder will load on first use)")

    @property
    def encoder(self):
        """Lazy-load the SentenceTransformer encoder on first use."""
        import time
        
        with self._encoder_lock:
            if self._encoder is None:
                print("[MEMORY] Loading embedding model (lazy load)...")
                # Import here to delay PyTorch loading
                from sentence_transformers import SentenceTransformer
                self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
                print("[MEMORY] Embedding model loaded.")
            
            # Reset unload timer
            self._last_encoder_use = time.time()
            self._schedule_unload()
            
            return self._encoder
    
    def _schedule_unload(self):
        """Schedule encoder unload after timeout."""
        if self._unload_timer:
            self._unload_timer.cancel()
        
        self._unload_timer = threading.Timer(self._unload_timeout, self._auto_unload_encoder)
        self._unload_timer.daemon = True
        self._unload_timer.start()
    
    def _auto_unload_encoder(self):
        """Automatically unload encoder after inactivity to free RAM."""
        import time
        
        with self._encoder_lock:
            if self._encoder is not None:
                elapsed = time.time() - self._last_encoder_use
                if elapsed >= self._unload_timeout:
                    print(f"[MEMORY] Auto-unloading encoder after {elapsed:.0f}s of inactivity...")
                    self._unload_encoder_internal()

    def _unload_encoder_internal(self):
        """Internal method to unload encoder (must hold lock)."""
        if self._encoder is not None:
            try:
                # Clear GPU cache if using CUDA
                try:
                    import torch
                    if torch.cuda.is_available():
                        self._encoder.to('cpu')
                        torch.cuda.empty_cache()
                except:
                    pass
                
                del self._encoder
                self._encoder = None
                gc.collect()
                print("[MEMORY] Encoder unloaded - RAM freed.")
            except Exception as e:
                print(f"[MEMORY] Error unloading encoder: {e}")

    def unload_encoder(self):
        """Manually unload the encoder to free RAM."""
        with self._encoder_lock:
            self._unload_encoder_internal()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            print(f"[MEMORY] Creating collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension for all-MiniLM-L6-v2
                    distance=models.Distance.COSINE
                )
            )

    def add_memory(self, text: str, metadata: dict = None) -> bool:
        """Add a text chunk to long-term memory (thread-safe). Returns False if duplicate found."""
        with self._encoder_lock:  # Reuse encoder lock to serialize all memory operations
            embedding = self.encoder.encode(text).tolist()
            
            # Duplicate Detection: Check if similar content already exists
            try:
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=embedding,
                    limit=1
                )
                
                if hits and len(hits) > 0:
                    # Qdrant returns cosine similarity as score (1.0 = identical)
                    similarity = hits[0].score if hasattr(hits[0], 'score') else 0
                    existing_content = hits[0].payload.get("content", "")
                    
                    # If very similar (>0.92) and content overlaps, skip insertion
                    if similarity > 0.92:
                        print(f"[MEMORY] DUPLICATE DETECTED (similarity: {similarity:.2f}): {text[:40]}...")
                        return False
            except Exception as e:
                print(f"[MEMORY] Duplicate check failed (proceeding anyway): {e}")
            
            # No duplicate found, proceed with insertion
            payload = {"content": text, **(metadata or {})}
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            print(f"[MEMORY] Memory added: {text[:50]}...")
            return True

    def search_memory(self, query: str, limit: int = 5, filter_type: str = None) -> List[dict]:
        """Retrieve relevant context for a query. Optional filter by 'type'."""
        query_vector = self.encoder.encode(query).tolist()
        
        try:
            query_filter = None
            if filter_type:
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value=filter_type)
                        )
                    ]
                )

            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit
            )
        except Exception as e:
            print(f"[MEMORY] Search failed: {e}")
            return []
            
        return [h.payload for h in hits]
        
    def search_code(self, query: str, limit: int = 3) -> List[dict]:
        """Specialized search for code snippets and patterns."""
        return self.search_memory(query, limit=limit, filter_type="code")

    def get_all_memories(self, limit: int = 1000) -> List[dict]:
        """Retrieve all memories (up to limit) ordered by insertion."""
        try:
            result, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            return [
                {"id": str(point.id), "content": point.payload.get("content", ""), "metadata": point.payload} 
                for point in result
            ]
        except Exception as e:
            print(f"[MEMORY] Scroll failed: {e}")
            return []

    def get_memory_stats(self) -> dict:
        """Get memory usage statistics safe."""
        stats = {
            "encoder_loaded": self._encoder is not None,
            "ram_usage_mb": 0,
            "qdrant_path": self.qdrant_path,
            "collection": self.collection_name,
            "total_memories": 0
        }
        
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            stats["ram_usage_mb"] = round(mem_info.rss / 1024 / 1024, 2)
        except Exception as e:
            print(f"[MEMORY WARN] Could not get RAM usage: {e}")

        try:
            if self.client:
                count_result = self.client.count(collection_name=self.collection_name)
                stats["total_memories"] = count_result.count
        except Exception as e:
            # Qdrant might fail if locked or not init
            pass
        
        return stats

    def cleanup(self):
        """Clean up resources - close Qdrant client and clear encoder from memory."""
        print("[MEMORY] Cleaning up memory service...")
        
        # Cancel unload timer
        if self._unload_timer:
            self._unload_timer.cancel()
        
        # Unload encoder
        with self._encoder_lock:
            self._unload_encoder_internal()
        
        # Close Qdrant client
        try:
            if self.client and hasattr(self.client, 'close'):
                self.client.close()
            self.client = None
            print("[MEMORY] Qdrant client closed.")
        except Exception as e:
            print(f"[MEMORY] Error closing Qdrant client: {e}")
        
        gc.collect()
        print("[MEMORY] Memory service cleanup complete.")

memory_service = MemoryService()
