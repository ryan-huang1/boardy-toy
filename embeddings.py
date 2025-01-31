from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """Initialize the SBERT model"""
        print("Loading SBERT model...")
        # Using all-MiniLM-L6-v2 as it's a good balance of speed and performance
        self._model = SentenceTransformer('all-MiniLM-L6-v2')
        print("SBERT model loaded successfully!")

    def generate_embedding(self, text):
        """Generate embedding for a single text"""
        if not text:
            return []
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