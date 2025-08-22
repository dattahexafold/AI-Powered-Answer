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
        language = request.form.get('language', 'marathi').strip()
        
        # Language-specific error messages
        error_messages = {
            'marathi': {
                'empty': 'कृपया प्रश्न लिहा.',
                'short': 'प्रश्न खूप लहान आहे. कृपया अधिक तपशील द्या.',
                'technical': 'तांत्रिक त्रुटी झाली. कृपया पुन्हा प्रयत्न करा.'
            },
            'hindi': {
                'empty': 'कृपया प्रश्न लिखें।',
                'short': 'प्रश्न बहुत छोटा है। कृपया अधिक विवरण दें।',
                'technical': 'तकनीकी त्रुटि हुई। कृपया पुनः प्रयास करें।'
            },
            'english': {
                'empty': 'Please enter a question.',
                'short': 'Question is too short. Please provide more details.',
                'technical': 'Technical error occurred. Please try again.'
            },
            'gujarati': {
                'empty': 'કૃપા કરીને પ્રશ્ન લખો.',
                'short': 'પ્રશ્ન ખૂબ નાનો છે. કૃપા કરીને વધુ વિગતો આપો.',
                'technical': 'તકનીકી ભૂલ થઈ. કૃપા કરીને ફરી પ્રયાસ કરો.'
            },
            'bengali': {
                'empty': 'অনুগ্রহ করে একটি প্রশ্ন লিখুন।',
                'short': 'প্রশ্নটি খুব ছোট। অনুগ্রহ করে আরো বিস্তারিত দিন।',
                'technical': 'প্রযুক্তিগত ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।'
            },
            'tamil': {
                'empty': 'தயவுசெய்து ஒரு கேள்வியை எழுதுங்கள்.',
                'short': 'கேள்வி மிகவும் சிறியது. தயவுசெய்து அதிக விவரங்களை கொடுங்கள்.',
                'technical': 'தொழில்நுட்ப பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சி செய்யுங்கள்.'
            },
            'telugu': {
                'empty': 'దయచేసి ఒక ప్రశ్న రాయండి.',
                'short': 'ప్రశ్న చాలా చిన్నది. దయచేసి మరింత వివరాలు ఇవ్వండి.',
                'technical': 'సాంకేతిక లోపం జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.'
            }
        }
        
        msgs = error_messages.get(language, error_messages['marathi'])
        
        if not question:
            return jsonify({
                'success': False, 
                'error': msgs['empty']
            })
        
        if len(question) < 5:
            return jsonify({
                'success': False, 
                'error': msgs['short']
            })
        
        # Get answer using the QA engine with language parameter
        answer = answer_question(question, language)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'language': language
        })
        
    except Exception as e:
        app.logger.error(f"Error processing question: {str(e)}")
        language = request.form.get('language', 'marathi')
        error_messages = {
            'marathi': 'तांत्रिक त्रुटी झाली. कृपया पुन्हा प्रयत्न करा.',
            'hindi': 'तकनीकी त्रुटि हुई। कृपया पुनः प्रयास करें।',
            'english': 'Technical error occurred. Please try again.',
            'gujarati': 'તકનીકી ભૂલ થઈ. કૃપા કરીને ફરી પ્રયાસ કરો.',
            'bengali': 'প্রযুক্তিগত ত্রুটি হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।',
            'tamil': 'தொழில்நுட்ப பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சி செய்யுங்கள்.',
            'telugu': 'సాంకేతిక లోపం జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.'
        }
        return jsonify({
            'success': False,
            'error': error_messages.get(language, error_messages['marathi'])
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
