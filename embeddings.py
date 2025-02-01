from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

class EmbeddingGenerator:
    _instance = None
    _model = None
    _cross_encoder = None

    @classmethod
    def initialize(cls):
        """Initialize the SBERT model and cross-encoder at server start"""
        if cls._model is None:
            print("Loading SBERT model...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("SBERT model loaded successfully!")
            
            print("Loading cross-encoder model...")
            cls._cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            print("Cross-encoder model loaded successfully!")
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

    def generate_combined_embedding(self, interests, skills, bio=None):
        """Generate a combined embedding from interests, skills, and bio"""
        # Combine interests, skills, and bio into a single descriptive text
        combined_text = ""
        
        if interests:
            combined_text += "Interests: " + ", ".join(interests) + ". "
        
        if skills:
            combined_text += "Skills: " + ", ".join(skills) + ". "
            
        if bio:
            combined_text += "Bio: " + bio
            
        if not combined_text:
            return []
            
        return self.generate_embedding(combined_text)
        
    def rerank_results(self, query_text, candidates):
        """Rerank candidates using cross-encoder"""
        if not candidates:
            return []
            
        # Prepare pairs for cross-encoder
        pairs = []
        for candidate in candidates:
            # Create descriptive text for candidate
            candidate_text = ""
            if candidate.get('interests'):
                candidate_text += "Interests: " + ", ".join(candidate['interests']) + ". "
            if candidate.get('skills'):
                candidate_text += "Skills: " + ", ".join(candidate['skills']) + ". "
            if candidate.get('bio'):
                candidate_text += "Bio: " + candidate['bio']
            
            pairs.append([query_text, candidate_text])
            
        # Get cross-encoder scores
        scores = self._cross_encoder.predict(pairs)
        
        # Add scores to candidates
        scored_candidates = []
        for candidate, score in zip(candidates, scores):
            if score > 0:  # Only include positive scores
                candidate['similarity'] = float(score)
                scored_candidates.append(candidate)
                
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['similarity'], reverse=True)
        return scored_candidates 