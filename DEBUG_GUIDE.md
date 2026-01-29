# 🔧 Debugging & Advanced Tips

## Common Issues & Solutions

### 1. **Python Not Found**
```powershell
# Error: 'python' is not recognized

# Solution:
python --version  # or python3 --version

# If not found, install Python from python.org
# Make sure to check "Add Python to PATH" during installation
```

### 2. **Virtual Environment Not Activating**
```powershell
# Error: cannot be loaded because running scripts is disabled

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Y  # Type Y and press Enter

# Then try again:
.\venv\Scripts\Activate.ps1
```

### 3. **Dependencies Won't Install**
```powershell
# Error: Could not find a version that satisfies the requirement

# Solution: Update pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### 4. **Port 5000 Already in Use**
```powershell
# Error: Address already in use

# Option 1: Change port in app.py
# Find line: app.run(debug=True, host='0.0.0.0', port=5000)
# Change to: app.run(debug=True, host='0.0.0.0', port=5001)

# Option 2: Kill process using port 5000
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 5. **NLTK Data Not Found**
```powershell
# Error: LookupError: Resource punkt not found

# Solution: Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Or in Python interpreter:
# python
# >>> import nltk
# >>> nltk.download('punkt')
# >>> nltk.download('stopwords')
# >>> exit()
```

### 6. **CSV File Not Found**
```powershell
# Error: FileNotFoundError: dataset/career_data.csv

# Solution: Make sure you're in the correct directory
pwd  # Check current location
cd c:\CareerGuidanceSystem\career_guidance

# Verify file exists:
Test-Path -Path "dataset/career_data.csv"
```

### 7. **Form Submission Not Working**
```javascript
// Check browser console (F12 → Console tab)
// Look for errors like:

// "Failed to fetch" = backend not running
// Check: Is Flask server running? 

// "CORS error" = only if deployed
// Solution: Not an issue locally

// "JSON parse error" = frontend/backend mismatch
// Solution: Check network tab (F12 → Network) to see response
```

### 8. **CSS Not Loading (Styling Broken)**
```html
<!-- Make sure Flask is serving static files correctly -->
<!-- In templates, use: -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

<!-- NOT: -->
<!-- <link rel="stylesheet" href="/static/style.css"> -->
```

---

## 🔍 How to Debug Issues

### **Method 1: Check Flask Logs**
```powershell
# When running: python app.py

# You'll see:
# [2024-01-17 10:00:00,123] DEBUG in app: Loading assessment form
# [2024-01-17 10:00:05,456] INFO: 127.0.0.1 POST /get_results 200

# Look for ERROR or WARNING messages
```

### **Method 2: Browser Developer Tools**
```javascript
// Press F12 to open DevTools

// Console Tab:
// Check for JavaScript errors
// Test fetch: fetch('/api/career_details/Data%20Scientist')

// Network Tab:
// Click form submit, watch for /get_results request
// Check Response for data or errors

// Sources Tab:
// Debug JavaScript step-by-step
```

### **Method 3: Add Debug Prints**
```python
# In app.py, add prints to see what's happening:

@app.route('/get_results', methods=['POST'])
def get_results():
    data = request.json
    print(f"Received form data: {data}")  # ← Add this
    
    recommendations = recommendation_engine.get_recommendations(
        education_level=data.get('education_level', ''),
        skills_text=data.get('skills', '')
    )
    
    print(f"Generated recommendations: {recommendations}")  # ← Add this
    
    return jsonify({'success': True, 'data': recommendations})
```

### **Method 4: Test Individual Components**
```python
# Test preprocess.py separately:

from utils.preprocess import TextPreprocessor, CareerMatcher

# Test text preprocessing
preprocessor = TextPreprocessor()
result = preprocessor.clean_text("Python, Machine Learning, Data Analysis")
print(result)

# Test career matching
matcher = CareerMatcher('dataset/career_data.csv')
matches = matcher.match_user_to_careers(
    user_skills=['Python', 'SQL', 'Machine Learning'],
    user_interests=['Data Science', 'Analytics']
)
print(matches[0])  # First recommendation
```

---

## 📈 Performance Optimization

### **1. Cache Career Data**
```python
# In app.py, cache the career data instead of reloading:

@app.before_first_request
def load_career_data():
    global recommendation_engine
    recommendation_engine = RecommendationEngine(DATASET_PATH)

# Now recommendation_engine loads only once, not per request
```

### **2. Async Processing**
```python
# For slow operations, use async:

from flask import jsonify
from celery import Celery

celery = Celery(app.name)

@celery.task
def process_recommendations(form_data):
    # Long-running task
    return recommendation_engine.get_recommendations(**form_data)
```

### **3. Database Instead of CSV**
```python
# Replace CSV with SQLite:

import sqlite3

conn = sqlite3.connect('careers.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM careers WHERE domain = ?', (domain,))
careers = cursor.fetchall()
```

---

## 🧪 Testing the System

### **Manual Testing Checklist**

- [ ] Landing page loads without errors
- [ ] Assessment form validates inputs (required fields)
- [ ] Form submission shows loading spinner
- [ ] Results page displays after ~1 second
- [ ] Top 3 recommendations show with match scores
- [ ] Skill tags display correctly (color-coded)
- [ ] Learning roadmap shows 3 levels
- [ ] Responsive design works on mobile (F12 → Toggle device toolbar)
- [ ] Retake assessment button works
- [ ] Back to home button works
- [ ] All links work (no 404 errors)

### **Sample Test Cases**

**Test Case 1: High Match**
- Skills: Python, SQL, Machine Learning, Statistics, Pandas
- Interests: Data science, analytics, insights
- Expected: Data Scientist should be top match (90%+)

**Test Case 2: No Match**
- Skills: Cooking, Gardening, Arts
- Interests: Music, painting
- Expected: Low scores for all tech careers

**Test Case 3: Domain Filter**
- Domain: Web Development
- Skills: Python, JavaScript, React
- Expected: Web Developer, Full Stack Developer in top results

---

## 🐛 Common Bugs & Fixes

### **Bug #1: Same career appearing multiple times**
```python
# In preprocess.py CareerMatcher.match_user_to_careers()
# Add: matches = list(dict.fromkeys(matches))
# To remove duplicates while preserving order
```

### **Bug #2: Empty skill recommendations**
```python
# In recommend.py, check:
if not recommendation_result['recommendations']:
    return {'success': False, 'message': 'No matching careers found'}
```

### **Bug #3: NaN values in results**
```python
# In preprocess.py, ensure:
match_score = round(match_score, 2) if match_score else 0
# Add None checks before calculations
```

### **Bug #4: Encoding issues with special characters**
```python
# In app.py, ensure UTF-8:
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# Add correct headers in render_template
```

---

## 📊 Monitoring & Analytics

### **Track Usage**
```python
# Add request logging:

import logging
from datetime import datetime

logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/assessment')
def assessment():
    logger.info(f"{datetime.now()} - User accessed assessment")
    return render_template('form.html')

@app.route('/get_results', methods=['POST'])
def get_results():
    logger.info(f"{datetime.now()} - Form submitted")
    # ... rest of code
```

### **Track Recommendations**
```python
# Store recommendations data:

def save_recommendation(education_level, skills, recommendations):
    with open('recommendations_log.csv', 'a') as f:
        f.write(f"{datetime.now()}, {education_level}, {len(skills)}, {recommendations[0]['career']}\n")
```

---

## 🔐 Security Considerations

### **1. Input Validation**
```python
# Always validate user input:

def get_results():
    skills = request.json.get('skills', '').strip()
    if not skills or len(skills) > 1000:
        return jsonify({'success': False, 'message': 'Invalid input'}), 400
```

### **2. Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/get_results', methods=['POST'])
@limiter.limit("5 per minute")
def get_results():
    # Only 5 requests per minute per IP
```

### **3. Sanitize Output**
```python
# Prevent XSS attacks:
from markupsafe import escape

recommendation_result['career'] = escape(recommendation_result['career'])
```

---

## 📚 Advanced Topics

### **1. Machine Learning Improvements**
- Replace TF-IDF with Word Embeddings (Word2Vec)
- Train ML model on historical recommendation data
- Use clustering to find similar careers
- Implement ranking algorithm (LambdaMART)

### **2. NLP Enhancements**
- Implement synonym detection (career = job, role)
- Add spell checking
- Use BERT for better semantic understanding
- Add multi-language support

### **3. Scalability**
- Deploy on cloud (Heroku, AWS, Google Cloud)
- Use Docker for containerization
- Implement caching (Redis)
- Use CDN for static files
- Load balance requests

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Remove `debug=True` from app.py
- [ ] Use environment variables for config
- [ ] Enable HTTPS
- [ ] Implement logging
- [ ] Add error tracking (Sentry)
- [ ] Set up monitoring (New Relic)
- [ ] Configure backup system
- [ ] Test performance under load
- [ ] Implement rate limiting
- [ ] Add CORS headers if needed
- [ ] Minify CSS and JS
- [ ] Compress images
- [ ] Set up CI/CD pipeline

---

## 💡 Pro Tips

1. **Use Flask Shell for debugging:**
   ```powershell
   flask shell
   >>> from utils.preprocess import TextPreprocessor
   >>> p = TextPreprocessor()
   >>> p.clean_text("Python, ML, Data")
   ```

2. **Test API with Postman:**
   - Create new POST request to `http://localhost:5000/get_results`
   - Set Body (JSON):
     ```json
     {
       "education_level": "Bachelor",
       "skills": "Python, SQL",
       "interests": "Data Science",
       "domain": "AI"
     }
     ```

3. **Use VS Code extensions:**
   - Better Comments
   - Python Docstring Generator
   - Thunder Client (API testing)

4. **Monitor with `top` command:**
   ```powershell
   # Check CPU/Memory usage (Linux-like):
   # Use Windows Task Manager instead
   ```

---

**Happy debugging! 🎯**
