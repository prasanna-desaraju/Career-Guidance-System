from .preprocess import CareerMatcher, TextPreprocessor
class RecommendationEngine:
    """
    Main recommendation engine that orchestrates career matching and analysis
    """

    def __init__(self, career_data_path):
        self.matcher = CareerMatcher(career_data_path)
        self.preprocessor = TextPreprocessor()

    def get_recommendations(self, education_level, skills_text, interests_text, domain_preference=None, strengths_text=None):
        """
        Get career recommendations based on user profile
        
        Args:
            education_level (str): User's education level
            skills_text (str): User's skills (comma/semicolon separated)
            interests_text (str): User's interests
            domain_preference (str): Preferred domain (optional)
            strengths_text (str): User's strengths (optional)
        
        Returns:
            dict: Complete recommendation result with matches, gaps, and roadmaps
        """
        
        # Extract skills from text
        user_skills = self.preprocessor.extract_skills(skills_text)
        user_interests = self.preprocessor.extract_skills(interests_text)
        user_strengths = self.preprocessor.extract_skills(strengths_text) if strengths_text else []
        
        # Get career matches
        matches = self.matcher.match_user_to_careers(user_skills, user_interests)
        
        # Filter by domain if specified
        if domain_preference:
            filtered_matches = [m for m in matches if m['domain'].lower() == domain_preference.lower()]
            if filtered_matches:
                matches = filtered_matches
        
        # Get top 3 recommendations
        top_matches = matches[:3]
        
        # Get skill gap analysis
        gap_analysis = self.matcher.get_skill_gap_analysis(user_skills, top_careers=3)
        
        # Get learning roadmaps for top 3 careers
        roadmaps = []
        for match in top_matches:
            roadmap = self.matcher.get_learning_roadmap(match['career'])
            if roadmap:
                roadmaps.append(roadmap)
        
        result = {
            'education_level': education_level,
            'user_profile': {
                'skills': user_skills,
                'interests': user_interests,
                'strengths': user_strengths,
                'domain_preference': domain_preference
            },
            'recommendations': top_matches,
            'skill_gaps': gap_analysis,
            'roadmaps': roadmaps,
            'all_matches': matches  # For reference
        }
        
        return result

    def get_career_details(self, career_name):
        """
        Get detailed information about a specific career
        
        Args:
            career_name (str): Name of the career
        
        Returns:
            dict: Detailed career information
        """
        careers = self.matcher.prepare_career_data()
        
        if career_name not in careers:
            return None
        
        roadmap = self.matcher.get_learning_roadmap(career_name)
        
        return {
            'career': career_name,
            'skills': careers[career_name]['skills'],
            'domain': careers[career_name]['domain'],
            'description': careers[career_name]['description'],
            'roadmap': roadmap['roadmap'] if roadmap else None,
            'resources': roadmap['resources'] if roadmap else None
        }


def format_recommendations_for_display(recommendation_result):
    """
    Format recommendation result for display in UI
    
    Args:
        recommendation_result (dict): Raw recommendation result
    
    Returns:
        dict: Formatted data for template rendering
    """
    
    formatted = {
        'education_level': recommendation_result['education_level'],
        'user_skills': recommendation_result['user_profile']['skills'],
        'user_interests': recommendation_result['user_profile']['interests'],
        'top_recommendation': recommendation_result['recommendations'][0] if recommendation_result['recommendations'] else None,
        'all_recommendations': recommendation_result['recommendations'],
        'skill_gaps': recommendation_result['skill_gaps'],
        'roadmaps': recommendation_result['roadmaps']
    }
    
    return formatted
