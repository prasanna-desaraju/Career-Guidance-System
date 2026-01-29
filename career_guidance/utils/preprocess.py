import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextPreprocessor:
    """
    Handles text preprocessing for career guidance system.
    Includes: lowercasing, stopword removal, tokenization
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text):
        """
        Clean and preprocess text input
        Args:
            text (str): Raw text input
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [word for word in tokens if word not in self.stop_words]
        
        # Join back to string
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text

    def extract_skills(self, skills_text):
        """
        Extract individual skills from input text
        Args:
            skills_text (str): Text containing skills (comma or semicolon separated)
        Returns:
            list: List of skills
        """
        # Split by common delimiters
        skills = re.split(r'[,;]', skills_text)
        skills = [skill.strip().lower() for skill in skills if skill.strip()]
        return skills

    def vectorize_text(self, texts, max_features=100):
        """
        Convert text to TF-IDF vectors
        Args:
            texts (list): List of text documents
            max_features (int): Maximum number of features
        Returns:
            vectorizer: Fitted TF-IDF vectorizer
            vectors: TF-IDF matrix
        """
        vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
        vectors = vectorizer.fit_transform(texts)
        return vectorizer, vectors

    def calculate_similarity(self, user_profile, career_profiles):
        """
        Calculate cosine similarity between user profile and career profiles
        Args:
            user_profile: User's vectorized profile
            career_profiles: Vectorized career profiles
        Returns:
            array: Similarity scores
        """
        similarities = cosine_similarity(user_profile, career_profiles)
        return similarities[0]


class CareerMatcher:
    """
    Matches user profile with careers using similarity metrics
    """

    def __init__(self, career_data_path):
        self.df = pd.read_csv(career_data_path)
        self.preprocessor = TextPreprocessor()

    def prepare_career_data(self):
        """
        Prepare career data for matching
        Returns:
            dict: Career information with processed skills
        """
        careers = {}
        for idx, row in self.df.iterrows():
            career_name = row['Career']
            skills = [s.strip() for s in row['Required_Skills'].split(';')]
            careers[career_name] = {
                'skills': skills,
                'domain': row['Domain'],
                'description': row['Description']
            }
        return careers

    def match_user_to_careers(self, user_skills, user_interests):
        """
        Match user profile to careers
        Args:
            user_skills (list): User's skills
            user_interests (list): User's interests
        Returns:
            list: Ranked career matches with scores
        """
        careers = self.prepare_career_data()
        matches = []

        for career_name, career_info in careers.items():
            # Calculate skill overlap
            career_skills_set = set(career_info['skills'])
            user_skills_set = set(user_skills)
            
            # Find matched skills
            matched_skills = user_skills_set.intersection(career_skills_set)
            
            # Calculate match percentage
            if len(career_skills_set) > 0:
                match_score = (len(matched_skills) / len(career_skills_set)) * 100
            else:
                match_score = 0
            
            # Calculate skill gap
            missing_skills = list(career_skills_set - user_skills_set)
            
            matches.append({
                'career': career_name,
                'match_score': round(match_score, 2),
                'matched_skills': list(matched_skills),
                'missing_skills': missing_skills,
                'domain': career_info['domain'],
                'description': career_info['description']
            })

        # Sort by match score (descending)
        matches = sorted(matches, key=lambda x: x['match_score'], reverse=True)
        
        return matches

    def get_skill_gap_analysis(self, user_skills, top_careers=3):
        """
        Analyze skill gaps for top recommended careers
        Args:
            user_skills (list): User's current skills
            top_careers (int): Number of top careers to analyze
        Returns:
            list: Skill gap analysis for top careers
        """
        careers = self.prepare_career_data()
        gap_analysis = []

        for i, career_name in enumerate(list(careers.keys())[:top_careers]):
            career_skills = set(careers[career_name]['skills'])
            user_skills_set = set(user_skills)
            missing_skills = list(career_skills - user_skills_set)
            
            gap_analysis.append({
                'career': career_name,
                'missing_skills': missing_skills,
                'domain': careers[career_name]['domain']
            })

        return gap_analysis

    def get_learning_roadmap(self, career_name):
        """
        Generate learning roadmap for a career
        Args:
            career_name (str): Target career
        Returns:
            dict: Learning roadmap with skills and resources
        """
        careers = self.prepare_career_data()
        
        if career_name not in careers:
            return None

        skills = careers[career_name]['skills']
        
        # Categorize skills by learning progression
        fundamental_skills = []
        advanced_skills = []
        specialized_skills = []
        
        # Simple categorization based on skill keywords
        for skill in skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in ['html', 'css', 'javascript', 'python', 'sql']):
                fundamental_skills.append(skill)
            elif any(keyword in skill_lower for keyword in ['tensorflow', 'pytorch', 'deep learning', 'neural']):
                advanced_skills.append(skill)
            else:
                specialized_skills.append(skill)

        roadmap = {
            'career': career_name,
            'domain': careers[career_name]['domain'],
            'roadmap': {
                'Fundamentals': fundamental_skills or skills[:len(skills)//3] or skills[:1],
                'Intermediate': advanced_skills or skills[len(skills)//3:2*len(skills)//3] or skills[1:2],
                'Advanced': specialized_skills or skills[2*len(skills)//3:] or skills[2:]
            },
            'resources': {
                'Fundamentals': ['Codecademy', 'Coursera Basics', 'YouTube Tutorials'],
                'Intermediate': ['Udacity', 'DataCamp', 'Pluralsight'],
                'Advanced': ['Specialized Courses', 'Real-world Projects', 'Kaggle Competitions']
            }
        }

        return roadmap
