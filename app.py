import os
import logging
from flask import Flask, render_template, request, jsonify
from qa_engine import answer_question

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    """Main page with question input form"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process question and return answer via AJAX"""
    try:
        question = request.form.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False, 
                'error': 'कृपया प्रश्न लिहा.'
            })
        
        if len(question) < 5:
            return jsonify({
                'success': False, 
                'error': 'प्रश्न खूप लहान आहे. कृपया अधिक तपशील द्या.'
            })
        
        # Get answer using the QA engine
        answer = answer_question(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
        
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'तांत्रिक त्रुटी झाली. कृपया पुन्हा प्रयत्न करा.'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
