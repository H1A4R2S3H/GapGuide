import spacy
import json
from spacy.matcher import PhraseMatcher

class SkillExtractor:
    def __init__(self, skills_file_path):
        """
        Loads the master skill dictionary and sets up the spaCy PhraseMatcher.
        """
        print("Initializing SkillExtractor with PhraseMatcher...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
            with open(skills_file_path, 'r', encoding='utf-8') as f:
                skill_data = json.load(f)
                skill_list = skill_data['skills']

            self.matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
            # Create spaCy doc objects for each skill for efficient matching
            patterns = [self.nlp.make_doc(skill) for skill in skill_list]
            self.matcher.add("SKILL_MATCHER", patterns)
            print("✅ SkillExtractor initialized successfully.")
        except Exception as e:
            print(f"❌ Error initializing SkillExtractor: {e}")
            self.nlp = None
            self.matcher = None

    def extract_skills(self, text: str) -> list:
        """
        Processes text (e.g., a resume) and extracts skills using the PhraseMatcher.
        """
        if not self.nlp or not self.matcher:
            return []
        
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        # Use a set to get unique matched skill text
        found_skills = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            found_skills.add(span.text)
            
        return sorted(list(found_skills))