"""Text transformation tools for the document editing agent."""

import re
from typing import Dict, Any


class DocumentTools:
    """Collection of text manipulation tools."""
    
    @staticmethod
    def fix_grammar(text: str) -> Dict[str, Any]:
        """
        Fix grammar and typos in text.
        
        Args:
            text: Input text to fix
            
        Returns:
            Dictionary with fixed text and changes made
        """
        # Basic grammar fixes
        fixed_text = text
        changes = []
        
        # Common grammar corrections
        corrections = {
            r'\bi\b': 'I',  # Capitalize 'i'
            r'\s+': ' ',  # Multiple spaces to single space
            r'([.!?])\s*([a-z])': lambda m: f"{m.group(1)} {m.group(2).upper()}",  # Capitalize after punctuation
        }
        
        for pattern, replacement in corrections.items():
            if callable(replacement):
                new_text = re.sub(pattern, replacement, fixed_text)
            else:
                new_text = re.sub(pattern, replacement, fixed_text)
            if new_text != fixed_text:
                changes.append(f"Applied {pattern}")
                fixed_text = new_text
        
        return {
            "original": text,
            "fixed": fixed_text.strip(),
            "changes": changes,
            "tool": "fix_grammar"
        }
    
    @staticmethod
    def make_professional(text: str) -> Dict[str, Any]:
        """
        Transform text to a more professional tone.
        
        Args:
            text: Input text to transform
            
        Returns:
            Dictionary with professional version and changes
        """
        professional_text = text
        changes = []
        
        # Replace casual phrases with professional alternatives
        replacements = {
            r'\bkinda\b': 'somewhat',
            r'\bgonna\b': 'going to',
            r'\bwanna\b': 'want to',
            r'\byeah\b': 'yes',
            r'\bnope\b': 'no',
            r'\bguys\b': 'everyone',
            r'\bstuff\b': 'items',
            r'\bthing\b': 'item',
        }
        
        for pattern, replacement in replacements.items():
            new_text = re.sub(pattern, replacement, professional_text, flags=re.IGNORECASE)
            if new_text != professional_text:
                changes.append(f"Replaced casual term with '{replacement}'")
                professional_text = new_text
        
        return {
            "original": text,
            "professional": professional_text,
            "changes": changes,
            "tool": "make_professional"
        }
    
    @staticmethod
    def summarize_text(text: str, bullet_points: int = 5) -> Dict[str, Any]:
        """
        Create a bullet-point summary of the text.
        
        Args:
            text: Input text to summarize
            bullet_points: Number of bullet points to generate
            
        Returns:
            Dictionary with summary and metadata
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take key sentences (simplified approach)
        num_bullets = min(bullet_points, len(sentences))
        summary_sentences = sentences[:num_bullets]
        
        summary = "\n".join([f"• {sentence}" for sentence in summary_sentences])
        
        return {
            "original": text,
            "summary": summary,
            "bullet_points": num_bullets,
            "word_count_original": len(text.split()),
            "word_count_summary": len(summary.split()),
            "tool": "summarize_text"
        }
    
    @staticmethod
    def add_section(text: str, topic: str, position: str = "end") -> Dict[str, Any]:
        """
        Add a new section about a specific topic.
        
        Args:
            text: Original document text
            topic: Topic for the new section
            position: Where to add ('start', 'end', or 'middle')
            
        Returns:
            Dictionary with updated text and metadata
        """
        section_title = f"\n\n## {topic.title()}\n\n"
        section_content = f"[Content about {topic} to be added here]\n\n"
        new_section = section_title + section_content
        
        if position == "start":
            updated_text = new_section + text
        elif position == "middle":
            # Insert in the middle
            mid_point = len(text) // 2
            updated_text = text[:mid_point] + new_section + text[mid_point:]
        else:  # end
            updated_text = text + new_section
        
        return {
            "original": text,
            "updated": updated_text,
            "section_added": topic,
            "position": position,
            "tool": "add_section"
        }
    
    @staticmethod
    def change_tone(text: str, target_tone: str = "formal") -> Dict[str, Any]:
        """
        Change the tone of the text.
        
        Args:
            text: Input text
            target_tone: Desired tone ('formal', 'casual', 'friendly', 'technical')
            
        Returns:
            Dictionary with transformed text and metadata
        """
        changes = []
        transformed = text
        
        if target_tone == "formal":
            # Make more formal
            replacements = {
                r'\bhi\b': 'Hello',
                r'\bthanks\b': 'Thank you',
                r'\bbye\b': 'Goodbye',
                r'\bcan\'t\b': 'cannot',
                r'\bwon\'t\b': 'will not',
                r'\bdon\'t\b': 'do not',
            }
            for pattern, replacement in replacements.items():
                new_text = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
                if new_text != transformed:
                    changes.append(f"Formalized: {pattern} -> {replacement}")
                    transformed = new_text
                    
        elif target_tone == "casual":
            # Make more casual
            replacements = {
                r'\bHello\b': 'Hi',
                r'\bThank you\b': 'Thanks',
                r'\bGoodbye\b': 'Bye',
            }
            for pattern, replacement in replacements.items():
                new_text = re.sub(pattern, replacement, transformed)
                if new_text != transformed:
                    changes.append(f"Casualized: {pattern} -> {replacement}")
                    transformed = new_text
        
        return {
            "original": text,
            "transformed": transformed,
            "target_tone": target_tone,
            "changes": changes,
            "tool": "change_tone"
        }
