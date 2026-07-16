"""Hugging Face-based email reply generator."""

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional
import torch


class HuggingFaceReplier:
    """Email reply generator using Hugging Face transformers."""
    
    def __init__(self, model_name: str = 'google/flan-t5-base'):
        """Initialize replier with Hugging Face model.
        
        Args:
            model_name: Hugging Face model name
        """
        self.model_name = model_name
        self.generator = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def load_model(self):
        """Load the model for text generation."""
        if self.generator is None:
            print(f"Loading model for reply generation: {self.model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            self.generator = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=self.tokenizer,
                device=0 if self.device == 'cuda' else -1,
                max_length=200,
                do_sample=True,
                temperature=0.7
            )
            print("Reply generator loaded!")
    
    def generate_reply(self, email_subject: str, email_body: str, 
                      style: str = 'professional', custom_instruction: str = None) -> str:
        """Generate a reply to an email.
        
        Args:
            email_subject: Subject of the original email
            email_body: Body of the original email
            style: Reply style (professional, casual, concise)
            custom_instruction: Custom instruction for reply
            
        Returns:
            Generated reply text
        """
        if self.generator is None:
            self.load_model()
        
        # Create prompt based on style
        style_prompts = {
            'professional': "Write a professional email reply:",
            'casual': "Write a friendly casual email reply:",
            'concise': "Write a brief concise email reply:"
        }
        
        base_prompt = style_prompts.get(style, style_prompts['professional'])
        
        # Build full prompt
        if custom_instruction:
            prompt = f"{base_prompt} {custom_instruction}\n\nOriginal email subject: {email_subject}\nOriginal email: {email_body[:500]}"
        else:
            prompt = f"{base_prompt}\n\nOriginal email subject: {email_subject}\nOriginal email: {email_body[:500]}"
        
        try:
            # Generate reply
            result = self.generator(prompt, max_length=150, do_sample=True, temperature=0.7)
            
            if result and len(result) > 0:
                reply = result[0]['generated_text']
                return reply.strip()
            else:
                return self._get_fallback_reply(style)
                
        except Exception as e:
            print(f"Reply generation error: {e}")
            return self._get_fallback_reply(style)
    
    def _get_fallback_reply(self, style: str = 'professional') -> str:
        """Get a fallback reply template."""
        fallbacks = {
            'professional': "Thank you for your email. I have received your message and will review it shortly. I will get back to you soon with a detailed response.",
            'casual': "Thanks for your email! Got your message and will check it out. Will get back to you soon!",
            'concise': "Thank you for your email. I'll review and respond soon."
        }
        return fallbacks.get(style, fallbacks['professional'])
