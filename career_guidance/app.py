import os
import sys
from flask import Flask, render_template, request, jsonify
from utils.recommend import RecommendationEngine, format_recommendations_for_display

# Initialize Flask app
app = Flask(__name__)

# Get the absolute path to the career_guidance directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'career_data.csv')

# Initialize recommendation engine
try:
    recommendation_engine = RecommendationEngine(DATASET_PATH)
except Exception as e:
    print(f"Error initializing recommendation engine: {e}")
    recommendation_engine = None


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/assessment')
def assessment():
    """Career assessment form page"""
    return render_template('form.html')


@app.route('/get_results', methods=['POST'])
def get_results():
    """
    Process assessment form and return career recommendations
    """
    try:
        # Get form data
        data = request.json
        
        education_level = data.get('education_level', '')
        skills = data.get('skills', '')
        interests = data.get('interests', '')
        domain = data.get('domain', '')
        strengths = data.get('strengths', '')
        
        # Validate input
        if not skills or not interests:
            return jsonify({
                'success': False,
                'message': 'Please fill in skills and interests'
            }), 400
        
        # Get recommendations from engine
        recommendations = recommendation_engine.get_recommendations(
            education_level=education_level,
            skills_text=skills,
            interests_text=interests,
            domain_preference=domain,
            strengths_text=strengths
        )
        
        # Format data for display
        formatted_data = format_recommendations_for_display(recommendations)
        
        return jsonify({
            'success': True,
            'data': formatted_data
        }), 200
    
    except Exception as e:
        print(f"Error in get_results: {e}")
        return jsonify({
            'success': False,
            'message': f'Error processing assessment: {str(e)}'
        }), 500


@app.route('/results')
def results():
    """Results dashboard page"""
    return render_template('result.html')


@app.route('/api/career_details/<career_name>')
def get_career_details(career_name):
    """
    Get detailed information about a specific career
    """
    try:
        career_details = recommendation_engine.get_career_details(career_name)
        
        if not career_details:
            return jsonify({
                'success': False,
                'message': 'Career not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': career_details
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
