from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    _instance = None
    _model = None

    @classmethod
    def initialize(cls):
        """Initialize the SBERT model at server start"""
        if cls._model is None:
            print("Loading SBERT model...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("SBERT model loaded successfully!")
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
            if cls._model is None:
                cls.initialize()
        return cls._instance

    def generate_embedding(self, text):
        """Generate embedding for a single text"""
        if not text:
            return []
        if self._model is None:
            raise RuntimeError("SBERT model not initialized")
        embedding = self._model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def generate_combined_embedding(self, interests, skills):
        """Generate a combined embedding from interests and skills"""
        # Combine interests and skills into a single descriptive text
        combined_text = ""
        
        if interests:
            combined_text += "Interests: " + ", ".join(interests) + ". "
        
        if skills:
            combined_text += "Skills: " + ", ".join(skills)
            
        if not combined_text:
            return []
            
        return self.generate_embedding(combined_text) 