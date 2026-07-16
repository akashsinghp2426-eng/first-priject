"""Hugging Face-based email summarizer using lightweight models."""

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Optional
import torch


class HuggingFaceSummarizer:
    """Email summarizer using Hugging Face transformers with lightweight models."""
    
    def __init__(self, model_name: str = 'google/flan-t5-base', max_length: int = 512):
        """Initialize summarizer with Hugging Face model.
        
        Args:
            model_name: Hugging Face model name (default: google/flan-t5-base - lightweight)
            max_length: Maximum input length
        """
        self.model_name = model_name
        self.max_length = max_length
        self.summarizer = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def load_model(self):
        """Load the summarization model."""
        if self.summarizer is None:
            print(f"Loading model: {self.model_name} on {self.device}...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # Create summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model=model,
                tokenizer=self.tokenizer,
                device=0 if self.device == 'cuda' else -1,
                max_length=150,
                min_length=30,
                do_sample=True,
                temperature=0.7
            )
            print("Model loaded successfully!")
    
    def summarize(self, text: str, max_summary_length: int = 150, min_summary_length: int = 30) -> str:
        """Summarize email text.
        
        Args:
            text: Email text to summarize
            max_summary_length: Maximum summary length
            min_summary_length: Minimum summary length
            
        Returns:
            Summary string
        """
        if not text or len(text.strip()) < 50:
            return text
        
        # Load model if not already loaded
        if self.summarizer is None:
            self.load_model()
        
        try:
            # Truncate if too long
            if len(text) > self.max_length:
                text = text[:self.max_length]
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_summary_length,
                min_length=min_summary_length,
                do_sample=True,
                temperature=0.7
            )
            
            if summary and len(summary) > 0:
                return summary[0]['summary_text']
            else:
                return text[:200] + "..." if len(text) > 200 else text
                
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: return first 200 chars
            return text[:200] + "..." if len(text) > 200 else text
    
    def summarize_batch(self, texts: List[str], max_summary_length: int = 150) -> List[str]:
        """Summarize multiple texts.
        
        Args:
            texts: List of texts to summarize
            max_summary_length: Maximum summary length
            
        Returns:
            List of summaries
        """
        return [self.summarize(text, max_summary_length) for text in texts]
