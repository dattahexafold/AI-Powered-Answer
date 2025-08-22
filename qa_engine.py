import requests, re, time, random
from bs4 import BeautifulSoup
from readability.readability import Document
import nltk
from nltk.tokenize import sent_tokenize
from collections import Counter
import logging
import ast
import operator
import sympy as sp
from sympy import sympify, simplify
from sympy.parsing.sympy_parser import parse_expr

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception as e:
    logging.warning(f"NLTK download failed: {e}")

# --- Utility: साधं clean ---
def clean_text(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# --- Advanced Math Expression Extraction and Conversion ---
def extract_and_convert_math_expression(query):
    """Extract and convert natural language math to symbolic expression"""
    query_lower = query.lower().strip()
    
    # First, remove common question words
    query_lower = re.sub(r'^(what\s+is\s+|answer\s+of\s+|calculate\s+|solve\s+|find\s+)', '', query_lower)
    query_lower = re.sub(r'(\s*=\s*\?|\?|का\s*उत्तर|चे\s*उत्तर)$', '', query_lower)
    
    # Convert natural language math words to symbols
    conversions = {
        r'\bplus\b': '+',
        r'\badd\b': '+', 
        r'\badded\s+to\b': '+',
        r'\bminus\b': '-',
        r'\bsubtract\b': '-',
        r'\bsubtracted\s+from\b': '-',
        r'\btimes\b': '*',
        r'\bmultiply\b': '*',
        r'\bmultiplied\s+by\b': '*',
        r'\bdivide\b': '/',
        r'\bdivided\s+by\b': '/',
        r'\bx\b': '*',  # "2 x 3" means "2 * 3"
        r'\bby\b': '*',  # "2 by 3" could mean "2 * 3"
        r'\bof\b': '*',  # "half of 10" means "0.5 * 10"
        r'\band\b': '+',  # "8 plus 8 and 5 minus 1" = "8+8+5-1"
        r'\bthen\b': '+',
        r'\bpower\s+of\b': '**',
        r'\bsquare\s+of\b': '**2',
        r'\bcube\s+of\b': '**3',
        r'\bsquare\s+root\s+of\b': 'sqrt(',
        r'\broot\s+of\b': 'sqrt('
    }
    
    # Apply conversions
    for pattern, replacement in conversions.items():
        query_lower = re.sub(pattern, replacement, query_lower)
    
    # Handle special cases like "8 plus 8 and 5-1"
    # This should become "8+8+5-1" not just "8+8+5"
    
    # Clean up extra spaces and normalize
    query_lower = re.sub(r'\s+', ' ', query_lower).strip()
    
    # Replace word numbers with digits (basic ones)
    word_numbers = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    for word, digit in word_numbers.items():
        query_lower = re.sub(r'\b' + word + r'\b', digit, query_lower)
    
    # Remove remaining non-mathematical words and clean
    # Keep numbers, operators, parentheses, and spaces
    clean_expr = re.sub(r'[^0-9+\-*/()×÷\s.]', '', query_lower)
    clean_expr = clean_expr.replace('×', '*').replace('÷', '/')
    clean_expr = re.sub(r'\s+', '', clean_expr)  # Remove all spaces for sympy
    
    return clean_expr if clean_expr else query_lower

# --- Advanced Math Calculator with SymPy ---
def calculate_advanced_math(expression):
    """Calculate mathematical expressions using SymPy for accuracy and advanced functions"""
    try:
        # Extract and convert natural language to math expression
        expr = extract_and_convert_math_expression(expression)
        
        if not expr or not re.search(r'\d', expr):
            return None
            
        # Try to parse and evaluate with SymPy
        try:
            # Handle special functions
            expr = expr.replace('sqrt(', 'sqrt(').replace('log(', 'log(')
            
            # Parse and evaluate with SymPy
            sympy_expr = sympify(expr)
            result = float(sympy_expr.evalf() if hasattr(sympy_expr, 'evalf') else sympy_expr)
            
            # Format result nicely
            if isinstance(result, float):
                if result.is_integer():
                    return int(result)
                else:
                    # Round to reasonable precision
                    return round(result, 6)
            
            return result
            
        except Exception as sympy_error:
            # Fallback to basic AST evaluation if SymPy fails
            logging.warning(f"SymPy failed: {sympy_error}, trying basic calculation")
            return calculate_basic_fallback(expr)
            
    except Exception as e:
        logging.error(f"Math calculation failed: {e}")
        return None

# --- Basic Fallback Calculator ---
def calculate_basic_fallback(expr):
    """Fallback calculator using basic AST evaluation"""
    try:
        # Clean and validate expression
        expr = re.sub(r'[^\d+\-*/().\s]', '', expr)
        expr = expr.strip()
        
        if not expr:
            return None
            
        # Safety check
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expr):
            return None
        
        # Use AST for safe evaluation
        def safe_eval(node):
            if isinstance(node, ast.Expression):
                return safe_eval(node.body)
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                elif isinstance(node.op, ast.Sub):
                    return left - right
                elif isinstance(node.op, ast.Mult):
                    return left * right
                elif isinstance(node.op, ast.Div):
                    return left / right if right != 0 else None
            elif isinstance(node, ast.UnaryOp):
                operand = safe_eval(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +operand
                elif isinstance(node.op, ast.USub):
                    return -operand
            return None
        
        tree = ast.parse(expr, mode='eval')
        result = safe_eval(tree)
        
        if result is not None:
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return round(result, 6) if isinstance(result, float) else result
        
        return None
        
    except:
        return None

# --- Direct Code Generator ---
def generate_code_response(query):
    """Generate direct code examples based on coding questions"""
    query_lower = query.lower()
    
    # JavaScript programs
    if 'javascript' in query_lower and 'addition' in query_lower:
        code = """```javascript
// JavaScript Addition Program
function addNumbers(a, b) {
    return a + b;
}

// Example usage:
let num1 = 10;
let num2 = 20;
let result = addNumbers(num1, num2);

console.log(`${num1} + ${num2} = ${result}`);

// Interactive version with user input:
let userNum1 = prompt("Enter first number:");
let userNum2 = prompt("Enter second number:");
let sum = addNumbers(parseInt(userNum1), parseInt(userNum2));
console.log("Sum is: " + sum);
```"""
        return code
    
    elif 'javascript' in query_lower and any(word in query_lower for word in ['program', 'code', 'function', 'script']):
        if 'subtraction' in query_lower or 'subtract' in query_lower:
            code = """```javascript
// JavaScript Subtraction Program
function subtractNumbers(a, b) {
    return a - b;
}

// Example usage:
let num1 = 50;
let num2 = 30;
let result = subtractNumbers(num1, num2);
console.log(`${num1} - ${num2} = ${result}`);
```"""
            return code
        elif 'multiplication' in query_lower or 'multiply' in query_lower:
            code = """```javascript
// JavaScript Multiplication Program
function multiplyNumbers(a, b) {
    return a * b;
}

// Example usage:
let num1 = 5;
let num2 = 8;
let result = multiplyNumbers(num1, num2);
console.log(`${num1} × ${num2} = ${result}`);
```"""
            return code
        elif 'division' in query_lower or 'divide' in query_lower:
            code = """```javascript
// JavaScript Division Program
function divideNumbers(a, b) {
    if (b === 0) {
        return "Error: Cannot divide by zero";
    }
    return a / b;
}

// Example usage:
let num1 = 100;
let num2 = 5;
let result = divideNumbers(num1, num2);
console.log(`${num1} ÷ ${num2} = ${result}`);
```"""
            return code
        else:
            # Default basic JavaScript program
            code = """```javascript
// Basic JavaScript Program
function calculate(a, b, operation) {
    switch(operation) {
        case '+':
            return a + b;
        case '-':
            return a - b;
        case '*':
            return a * b;
        case '/':
            return b !== 0 ? a / b : "Error: Division by zero";
        default:
            return "Error: Invalid operation";
    }
}

// Example usage:
console.log("Addition: " + calculate(10, 5, '+'));
console.log("Subtraction: " + calculate(10, 5, '-'));
console.log("Multiplication: " + calculate(10, 5, '*'));
console.log("Division: " + calculate(10, 5, '/'));
```"""
            return code
    
    # Python programs
    elif 'python' in query_lower:
        if 'addition' in query_lower:
            code = """```python
# Python Addition Program
def add_numbers(a, b):
    return a + b

# Example usage:
num1 = 10
num2 = 20
result = add_numbers(num1, num2)

print(f"{num1} + {num2} = {result}")

# Interactive version:
num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))
sum_result = add_numbers(num1, num2)
print(f"Sum is: {sum_result}")
```"""
            return code
        else:
            code = """```python
# Basic Python Calculator Program
def calculator(a, b, operation):
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        return a / b if b != 0 else "Error: Division by zero"
    else:
        return "Error: Invalid operation"

# Example usage:
print("Addition:", calculator(10, 5, '+'))
print("Subtraction:", calculator(10, 5, '-'))
print("Multiplication:", calculator(10, 5, '*'))
print("Division:", calculator(10, 5, '/'))
```"""
            return code
    
    # HTML programs
    elif 'html' in query_lower:
        code = """```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Calculator</title>
</head>
<body>
    <h1>Simple Addition Calculator</h1>
    
    <div>
        <input type="number" id="num1" placeholder="Enter first number">
        <span>+</span>
        <input type="number" id="num2" placeholder="Enter second number">
        <button onclick="calculate()">Calculate</button>
    </div>
    
    <div id="result"></div>
    
    <script>
        function calculate() {
            let a = parseInt(document.getElementById('num1').value);
            let b = parseInt(document.getElementById('num2').value);
            let sum = a + b;
            document.getElementById('result').innerHTML = `Result: ${a} + ${b} = ${sum}`;
        }
    </script>
</body>
</html>
```"""
        return code
    
    # Generic coding response
    else:
        # Detect language if mentioned
        if any(lang in query_lower for lang in ['java', 'c++', 'php']):
            if 'java' in query_lower:
                code = """```java
// Java Addition Program
public class Calculator {
    public static int addNumbers(int a, int b) {
        return a + b;
    }
    
    public static void main(String[] args) {
        int num1 = 10;
        int num2 = 20;
        int result = addNumbers(num1, num2);
        
        System.out.println(num1 + " + " + num2 + " = " + result);
    }
}
```"""
                return code
        
        # Default to JavaScript if no specific language mentioned
        code = """```javascript
// General Programming Example
function processData(input) {
    // Your code logic here
    return input * 2; // Example operation
}

// Usage:
let data = 42;
let result = processData(data);
console.log("Result:", result);
```"""
        return code

# --- Question Type Detection ---
def detect_question_type(query):
    """Detect the type and complexity of question to determine search strategy"""
    query_lower = query.lower()
    
    # Simple arithmetic pattern (like 2+2+8=?, 5*3=?, etc.)
    simple_math_pattern = r'^[0-9+\-*/()×÷\s=?]+$'
    if re.match(simple_math_pattern, query.strip()):
        return 'simple_arithmetic'
    
    # Enhanced natural language arithmetic detection (including word numbers and operations)
    natural_math_patterns = [
        r'what\s+is\s+.*?\d+.*?[\+\-\*\/×÷].*?\d+',  # "what is 8 plus 8"
        r'answer\s+of\s+.*?\d+.*?[\+\-\*\/×÷].*?\d+',  # "answer of 8 plus 8"
        r'calculate\s+.*?\d+.*?[\+\-\*\/×÷].*?\d+',   # "calculate 8 plus 8"
        r'solve\s+.*?\d+.*?[\+\-\*\/×÷].*?\d+',      # "solve 8 plus 8"
        r'\d+.*?(plus|minus|times|multiply|divide|add|subtract).*?\d+',  # "8 plus 8"
        r'\d+[\+\-\*\/×÷]\d+',  # Direct "8+8"
        r'(\d+.*?)+.*?=.*?\?',  # "8+8 = ?"
        r'(\d+.*?)+.*?का\s*उत्तर',  # Marathi patterns
        r'(\d+.*?)+.*?चे\s*उत्तर'
    ]
    
    for pattern in natural_math_patterns:
        if re.search(pattern, query_lower):
            # Additional check: make sure it contains numbers and math operations
            if re.search(r'\d+', query_lower) and re.search(r'(plus|minus|times|multiply|divide|add|subtract|\+|\-|\*|\/|×|÷|and)', query_lower):
                return 'simple_arithmetic'
    
    # Coding question patterns - detect programming/code related questions
    coding_patterns = [
        r'(give\s+me|write|create|make)\s+.*?(program|code|script|function)',
        r'(javascript|python|java|html|css|php|c\+\+|programming)\s+.*?(program|code|example)',
        r'how\s+to\s+(code|program|write)\s+.*?(in|using)\s+(javascript|python|java|html|css)',
        r'(show|give)\s+.*?(code|example|program)\s+(for|to|of)',
        r'.*?(addition|subtraction|multiplication|division)\s+(program|code|script)',
        r'(write|create)\s+.*?(function|method|class)\s+(in|using|for)',
        r'.*?(algorithm|sorting|loop|array|function)\s+(code|example|program)',
        r'(प्रोग्राम|कोड)\s+.*?(javascript|python|java|html)',
        r'.*?(प्रोग्राम|कोड)\s+(लिहा|बनवा|दाखवा)'
    ]
    
    for pattern in coding_patterns:
        if re.search(pattern, query_lower):
            return 'coding'
    
    # Math question patterns
    math_patterns = [
        r'\d+[\+\-\*\/×÷]\d+', r'solve|calculate|compute|math|mathematics|equation',
        r'square root|sqrt|logarithm|trigonometry|algebra|geometry|calculus',
        r'formula|theorem|proof|derivative|integral', r'sin|cos|tan|log|exp'
    ]
    
    # Complex question patterns
    complex_patterns = [
        r'explain|describe|analyze|compare|contrast|difference between',
        r'how does|why does|what happens when|step by step|detailed',
        r'process|procedure|method|technique|approach'
    ]
    
    # Simple fact patterns
    simple_patterns = [
        r'^(what|when|where|who|which)\s', r'definition|meaning|is\s\w+',
        r'capital|population|currency|date|time'
    ]
    
    # Check math first
    for pattern in math_patterns:
        if re.search(pattern, query_lower):
            return 'math'
    
    # Check complex questions
    for pattern in complex_patterns:
        if re.search(pattern, query_lower):
            return 'complex'
    
    # Check simple facts
    for pattern in simple_patterns:
        if re.search(pattern, query_lower):
            return 'simple'
    
    # Default to general
    return 'general'

# --- Enhanced Search Query for Different Question Types ---
def enhance_search_query(query, question_type):
    """Enhance search query based on question type"""
    if question_type == 'math':
        # Add math-specific terms for better results
        enhanced = f"{query} mathematics solution steps explanation"
        if re.search(r'\d+', query):
            enhanced += " calculator math problem solve"
        return enhanced
    elif question_type == 'complex':
        return f"{query} detailed explanation comprehensive guide"
    elif question_type == 'simple':
        return f"{query} definition simple explanation"
    else:
        return f"{query} detailed information"

# --- Step 1: DuckDuckGo (lite) वर सर्च (API key नको) ---
def search_duckduckgo(query, n=3):
    """Search DuckDuckGo and return top n links"""
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.post(url, data={"q": query}, timeout=20, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        links = []
        for a in soup.select("a.result__a")[:n]:
            href = a.get("href")
            if href and str(href).startswith("http"):
                links.append(href)
        return links
    except Exception as e:
        logging.error(f"DuckDuckGo search failed: {e}")
        return []

# --- Step 2: पेजमधून मुख्य मजकूर काढणे ---
def extract_main_text(url):
    """Extract main text content from a webpage"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, timeout=25, headers=headers)
        r.raise_for_status()
        doc = Document(r.text)
        html = doc.summary(html_partial=True)
        soup = BeautifulSoup(html, "lxml")
        # Extract paragraph and list text
        text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all(["p","li"]))
        return clean_text(text)
    except Exception as e:
        logging.error(f"Text extraction failed for {url}: {e}")
        return ""

# --- Determine Search Parameters Based on Question Type ---
def get_search_params(question_type):
    """Get search count and answer length based on question type"""
    params = {
        'simple_arithmetic': {'search_count': 0, 'max_sentences': 1}, # No search needed for simple math
        'coding': {'search_count': 0, 'max_sentences': 1},            # Direct code generation, no search
        'math': {'search_count': 8, 'max_sentences': 8},      # Math needs more sources
        'complex': {'search_count': 10, 'max_sentences': 12}, # Complex questions need detailed answers
        'simple': {'search_count': 4, 'max_sentences': 4},    # Simple questions need fewer sources
        'general': {'search_count': 6, 'max_sentences': 7}    # General questions moderate
    }
    return params.get(question_type, params['general'])

# --- Enhanced Adaptive Summary with Daily Life Context ---
def summarize(text, max_sentences=5, question_type='general'):
    """Create adaptive extractive summary with natural, meaningful responses"""
    try:
        sents = [s.strip() for s in sent_tokenize(text) if len(s.strip()) > 20]
        if not sents:
            return text[:500] if text else "सारांश तयार करता आला नाही."

        # Math questions get special treatment
        if question_type == 'math':
            # Prioritize sentences with numbers, equations, steps
            math_keywords = ['step', 'solution', 'answer', 'calculate', 'formula', 'result', '=', '+', '-', '*', '/', 'method']
            math_sents = []
            other_sents = []
            
            for s in sents:
                if any(keyword in s.lower() for keyword in math_keywords) or re.search(r'\d+', s):
                    math_sents.append(s)
                else:
                    other_sents.append(s)
            
            # Prioritize math-related sentences
            prioritized_sents = math_sents + other_sents
            final_sents = prioritized_sents[:max_sentences]
            return " ".join(final_sents)

        # Enhanced summarization for daily life questions
        words = re.findall(r'\w+', text.lower())
        cnt = Counter(w for w in words if len(w) > 3)
        
        # Boost important daily life keywords
        daily_life_keywords = {
            'important', 'essential', 'main', 'primary', 'key', 'best', 'good', 'effective',
            'useful', 'helpful', 'recommended', 'should', 'need', 'must', 'can', 'will',
            'first', 'second', 'third', 'step', 'way', 'method', 'tip', 'advice',
            'benefit', 'advantage', 'reason', 'cause', 'effect', 'result'
        }
        
        # Score sentences with daily life relevance
        scores = []
        for s in sents:
            w = re.findall(r'\w+', s.lower())
            base_score = sum(cnt.get(x, 0) for x in w) / (len(w) + 1)
            
            # Boost sentences with practical keywords
            daily_boost = sum(2 for word in w if word in daily_life_keywords)
            
            # Prefer sentences that are more informative (not too short, not too long)
            length_score = 1.0
            if 50 <= len(s) <= 200:  # Ideal length
                length_score = 1.5
            elif len(s) < 30:  # Too short
                length_score = 0.5
            elif len(s) > 300:  # Too long
                length_score = 0.7
            
            final_score = (base_score + daily_boost) * length_score
            scores.append((final_score, s))
        
        # Get top sentences
        top = [s for _, s in sorted(scores, key=lambda x: x[0], reverse=True)[:max_sentences]]
        
        # Maintain original order for better flow
        top_in_order = [s for s in sents if s in top][:max_sentences]
        
        # Add connecting words for better flow
        result = " ".join(top_in_order)
        
        # Make it more conversational for daily life topics
        if question_type in ['simple', 'general']:
            # Add some natural transitions
            result = result.replace('. ', '. तसेच, ').replace('. तसेच, तसेच, ', '. ')
            result = re.sub(r'\. तसेच, ([A-Z])', r'. \1', result)  # Remove unnecessary transitions
        
        return result
        
    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return text[:500] if text else "सारांश तयार करता आला नाही."

# --- Enhanced Human-like Response Formatter ---
def format_human_response(answer, question_type, question, source_count, language='marathi'):
    """Format response in a more human-like manner with daily life context in multiple languages"""
    
    # Special handling for simple arithmetic - Multi-language
    if question_type == 'simple_arithmetic':
        simple_responses = {
            'marathi': [
                f"हे आहे उत्तर: **{answer}** 🔢",
                f"**{answer}** हे उत्तर आहे! 😊",
                f"गणित केले, उत्तर: **{answer}**",
                f"सोपे! उत्तर **{answer}** आहे.",
                f"**{answer}** - हे आहे तुमचे उत्तर!"
            ],
            'hindi': [
                f"यह है उत्तर: **{answer}** 🔢",
                f"**{answer}** यह उत्तर है! 😊",
                f"गणित किया, उत्तर: **{answer}**",
                f"आसान! उत्तर **{answer}** है।",
                f"**{answer}** - यह है आपका उत्तर!"
            ],
            'english': [
                f"Here's the answer: **{answer}** 🔢",
                f"**{answer}** is the answer! 😊",
                f"Calculated, answer: **{answer}**",
                f"Simple! The answer is **{answer}**.",
                f"**{answer}** - that's your answer!"
            ],
            'gujarati': [
                f"આ છે જવાબ: **{answer}** 🔢",
                f"**{answer}** આ જવાબ છે! 😊",
                f"ગણિત કર્યું, જવાબ: **{answer}**",
                f"સરળ! જવાબ **{answer}** છે।",
                f"**{answer}** - આ છે તમારો જવાબ!"
            ],
            'bengali': [
                f"এই হল উত্তর: **{answer}** 🔢",
                f"**{answer}** এই উত্তর! 😊",
                f"গণিত করলাম, উত্তর: **{answer}**",
                f"সহজ! উত্তর **{answer}**।",
                f"**{answer}** - এই হল আপনার উত্তর!"
            ],
            'tamil': [
                f"இது தான் பதில்: **{answer}** 🔢",
                f"**{answer}** இது பதில்! 😊",
                f"கணிதம் செய்தேன், பதில்: **{answer}**",
                f"எளிது! பதில் **{answer}**.",
                f"**{answer}** - இது உங்கள் பதில்!"
            ],
            'telugu': [
                f"ఇదే సమాధానం: **{answer}** 🔢",
                f"**{answer}** ఇదే సమాధానం! 😊",
                f"గణితం చేశాను, సమాధానం: **{answer}**",
                f"సులభం! సమాధానం **{answer}**.",
                f"**{answer}** - ఇదే మీ సమాధానం!"
            ]
        }
        responses = simple_responses.get(language, simple_responses['marathi'])
        return random.choice(responses)
    
    # Enhanced introductions with more personality and context - Multi-language
    intros = {
        'marathi': {
            'math': [
                "मी तुमच्या गणित प्रश्नाचे उत्तर शोधले आहे:",
                "तुमच्या गणित समस्येचे समाधान मिळाले:",
                "गणिताचा हा प्रश्न सोडवला गेला:",
                "तुमच्या गणिताच्या प्रश्नाची उत्तरे येथे आहेत:"
            ],
            'complex': [
                "तुमच्या प्रश्नावर विस्तृत संशोधन केले आहे:",
                "या विषयावर सखोल माहिती गोळा केली आहे:",
                "तुमच्या जटिल प्रश्नाचे तपशीलवार उत्तर:",
                "या महत्त्वाच्या विषयावर संपूर्ण माहिती:"
            ],
            'simple': [
                "तुमच्या प्रश्नाचे थोडक्यात उत्तर:",
                "या विषयी मुख्य गोष्टी असे आहेत:",
                "सरळ सोप्या भाषेत सांगायचे तर:",
                "तुमच्या प्रश्नाचे उत्तर लवकर मिळवले:"
            ],
            'general': [
                "तुमच्या प्रश्नावर संशोधन केले आणि हे मिळाले:",
                "तुम्ही विचारलेल्या गोष्टीबद्दल माहिती:",
                "या विषयी जे काही महत्त्वाचे आहे:",
                "तुमच्या जिज्ञासेचे उत्तर येथे आहे:"
            ]
        },
        'hindi': {
            'math': [
                "मैंने आपके गणित के प्रश्न का उत्तर खोजा है:",
                "आपकी गणित समस्या का समाधान मिल गया:",
                "गणित का यह प्रश्न हल हो गया:",
                "आपके गणित के प्रश्न के उत्तर यहाँ हैं:"
            ],
            'complex': [
                "आपके प्रश्न पर विस्तृत शोध किया गया है:",
                "इस विषय पर गहरी जानकारी एकत्र की गई है:",
                "आपके जटिल प्रश्न का विस्तृत उत्तर:",
                "इस महत्वपूर्ण विषय पर संपूर्ण जानकारी:"
            ],
            'simple': [
                "आपके प्रश्न का संक्षिप्त उत्तर:",
                "इस विषय की मुख्य बातें ये हैं:",
                "सीधी सरल भाषा में कहें तो:",
                "आपके प्रश्न का उत्तर जल्दी मिल गया:"
            ],
            'general': [
                "आपके प्रश्न पर शोध किया और यह मिला:",
                "आपने जो पूछा था उसके बारे में जानकारी:",
                "इस विषय में जो कुछ महत्वपूर्ण है:",
                "आपकी जिज्ञासा का उत्तर यहाँ है:"
            ]
        },
        'english': {
            'math': [
                "I found the answer to your math question:",
                "Your math problem has been solved:",
                "This math question has been resolved:",
                "Here are the answers to your math question:"
            ],
            'complex': [
                "Extensive research has been done on your question:",
                "In-depth information has been gathered on this topic:",
                "Detailed answer to your complex question:",
                "Complete information on this important topic:"
            ],
            'simple': [
                "Brief answer to your question:",
                "The main points about this topic are:",
                "In simple terms:",
                "Quickly found the answer to your question:"
            ],
            'general': [
                "Research was done on your question and here's what was found:",
                "Information about what you asked:",
                "What's important about this topic:",
                "Here's the answer to your curiosity:"
            ]
        }
    }
    
    # More conversational and helpful conclusions - Multi-language
    conclusions = {
        'marathi': [
            "आशा करतो हे तुमच्या कामी येईल! काही आणखी प्रश्न असतील तर नक्की विचारा.",
            "हे माहिती उपयुक्त वाटली का? आणखी काही जाणून घ्यायचे असेल तर सांगा.",
            "तुमच्या प्रश्नाचे उत्तर मिळाले आशा करतो. आणखी काही मदत हवी असेल तर विचारा.",
            "या माहितीने तुमची मदत झाली असेल अशी आशा! पुढे काही प्रश्न असतील तर नक्की सांगा.",
            "हे उत्तर कसे वाटले? आणखी काही स्पष्टीकरण हवे असेल तर विचारा.",
            "आशा आहे तुमची शंका दूर झाली असेल. आणखी काही प्रश्न असतील तर मोकळ्या मनाने विचारा!"
        ],
        'hindi': [
            "उम्मीद है यह आपके काम आएगा! कोई और प्रश्न हों तो जरूर पूछें।",
            "यह जानकारी उपयोगी लगी? और कुछ जानना हो तो बताएं।",
            "आपके प्रश्न का उत्तर मिल गया उम्मीद है। और कोई मदद चाहिए तो पूछें।",
            "इस जानकारी से आपकी मदद हुई होगी! आगे कोई प्रश्न हों तो जरूर बताएं।",
            "यह उत्तर कैसा लगा? कोई और स्पष्टीकरण चाहिए तो पूछें।",
            "उम्मीद है आपका संदेह दूर हुआ होगा। कोई और प्रश्न हों तो बेझिझक पूछें!"
        ],
        'english': [
            "Hope this helps you! If you have any more questions, feel free to ask.",
            "Did you find this information useful? Let me know if you want to know more.",
            "Hope you got the answer to your question. Ask if you need any more help.",
            "Hope this information helped you! Feel free to ask if you have more questions.",
            "How did you like this answer? Ask if you need any more explanation.",
            "Hope your doubt has been cleared. Feel free to ask any more questions!"
        ]
    }
    
    # Add contextual touch based on question content
    question_lower = question.lower()
    
    # Detect daily life topics and add relevant context
    if any(word in question_lower for word in ['खाणे', 'food', 'recipe', 'cook', 'खाना']):
        intro_context = "खाण्याच्या गोष्टींबद्दल तुम्ही विचारले आहे, "
    elif any(word in question_lower for word in ['health', 'आरोग्य', 'medicine', 'doctor']):
        intro_context = "आरोग्याच्या विषयावर तुमचा प्रश्न आहे, "
    elif any(word in question_lower for word in ['weather', 'हवामान', 'rain', 'temperature']):
        intro_context = "हवामानाबद्दल तुम्ही विचारले आहे, "
    elif any(word in question_lower for word in ['travel', 'प्रवास', 'transport', 'train', 'bus']):
        intro_context = "प्रवासाच्या गोष्टींबद्दल तुमचा प्रश्न आहे, "
    else:
        intro_context = ""
    
    # Get language-specific content
    lang_intros = intros.get(language, intros['marathi'])
    intro = random.choice(lang_intros.get(question_type, lang_intros['general']))
    
    lang_conclusions = conclusions.get(language, conclusions['marathi'])
    conclusion = random.choice(lang_conclusions)
    
    # Make the response more conversational
    if intro_context:
        response = f"{intro_context}{intro.lower()}\n\n{answer}\n\n---\n"
    else:
        response = f"{intro}\n\n{answer}\n\n---\n"
    
    # Add source information in a friendlier way
    if question_type == 'math':
        response += f"**माहितीचे स्रोत:** {source_count} विश्वसनीय गणित वेबसाइटवरून तपासले\n\n"
    else:
        if source_count > 5:
            response += f"**विस्तृत संशोधन:** {source_count} वेगवेगळ्या वेबसाइटवरून माहिती एकत्र केली\n\n"
        elif source_count > 2:
            response += f"**तपासलेले स्रोत:** {source_count} भरवसेमंद वेबसाइटवरून माहिती\n\n"
        else:
            response += f"**स्रोत:** {source_count} वेब पृष्ठांवरून माहिती\n\n"
    
    response += f"*{conclusion}*"
    
    return response

# --- Coding Response Formatter ---
def format_coding_response(code, question, language='marathi'):
    """Format coding responses with appropriate context in multiple languages"""
    
    # Detect programming language from question or code
    question_lower = question.lower()
    
    if 'javascript' in question_lower:
        language = "JavaScript"
        emoji = "🟨"
    elif 'python' in question_lower:
        language = "Python"
        emoji = "🐍"
    elif 'java' in question_lower:
        language = "Java"
        emoji = "☕"
    elif 'html' in question_lower:
        language = "HTML"
        emoji = "🌐"
    elif 'css' in question_lower:
        language = "CSS"
        emoji = "🎨"
    else:
        language = "Programming"
        emoji = "💻"
    
    # Contextual introductions - Multi-language
    intros = {
        'marathi': [
            f"तुम्ही {language} कोड मागितला आहे, येथे आहे:",
            f"{language} प्रोग्राम तुमच्यासाठी तयार केला:",
            f"तुमच्या प्रश्नासाठी {language} कोड येथे आहे:",
            f"{language} मध्ये तुमचे प्रोग्राम:",
            f"तुमच्या मागणीनुसार {language} कोड:"
        ],
        'hindi': [
            f"आपने {language} कोड माँगा था, यहाँ है:",
            f"{language} प्रोग्राम आपके लिए तैयार किया:",
            f"आपके प्रश्न के लिए {language} कोड यहाँ है:",
            f"{language} में आपका प्रोग्राम:",
            f"आपकी माँग के अनुसार {language} कोड:"
        ],
        'english': [
            f"You asked for {language} code, here it is:",
            f"{language} program created for you:",
            f"Here's the {language} code for your question:",
            f"Your program in {language}:",
            f"{language} code as per your request:"
        ]
    }
    
    # Helpful conclusions for coding - Multi-language
    conclusions = {
        'marathi': [
            "हा कोड तुम्ही copy-paste करून वापरू शकता. काही प्रश्न असल्यास विचारा!",
            "कोड कसा वापरायचा समजला का? अधिक मदत हवी असेल तर सांगा.",
            "हे प्रोग्राम तुमच्या कामी येईल. आणखी काही कोड हवा असेल तर विचारा!",
            "या कोडमध्ये काही बदल हवे असतील तर नक्की सांगा.",
            "आशा आहे हा कोड उपयुक्त ठरेल! आणखी प्रोग्रामिंग प्रश्न असतील तर विचारा."
        ],
        'hindi': [
            "यह कोड आप copy-paste करके इस्तेमाल कर सकते हैं। कोई प्रश्न हो तो पूछें!",
            "कोड कैसे उपयोग करना है समझ गया? और मदद चाहिए तो बताएं।",
            "यह प्रोग्राम आपके काम आएगा। और कोई कोड चाहिए तो पूछें!",
            "इस कोड में कोई बदलाव चाहिए हो तो जरूर बताएं।",
            "उम्मीद है यह कोड उपयोगी होगा! और प्रोग्रामिंग प्रश्न हों तो पूछें।"
        ],
        'english': [
            "You can copy-paste this code and use it. Ask if you have any questions!",
            "Did you understand how to use the code? Let me know if you need more help.",
            "This program will be useful for you. Ask if you need any more code!",
            "Let me know if you need any changes in this code.",
            "Hope this code will be useful! Ask if you have more programming questions."
        ]
    }
    
    # Get language-specific content for coding
    lang_intros = intros.get(language, intros['marathi'])
    intro = random.choice(lang_intros)
    
    lang_conclusions = conclusions.get(language, conclusions['marathi'])
    conclusion = random.choice(lang_conclusions)
    
    # Language-specific metadata text
    metadata_text = {
        'marathi': {
            'code_type': 'कोड प्रकार:',
            'feature': 'वैशिष्ट्य: तत्काळ कोड निर्मिती (वेब सर्च नको)'
        },
        'hindi': {
            'code_type': 'कोड प्रकार:',
            'feature': 'विशेषता: तत्काल कोड निर्माण (वेब सर्च नहीं)'
        },
        'english': {
            'code_type': 'Code Type:',
            'feature': 'Feature: Instant code generation (no web search needed)'
        }
    }
    
    lang_metadata = metadata_text.get(language, metadata_text['marathi'])
    
    response = f"{intro} {emoji}\n\n{code}\n\n---\n"
    response += f"**{lang_metadata['code_type']}** {language} प्रोग्राम\n"
    response += f"**{lang_metadata['feature']}**\n\n"
    response += f"*{conclusion}*"
    
    return response

# --- Enhanced Main Function: Smart Question Answering ---
def answer_question(query, language='marathi'):
    """Enhanced function with adaptive search and human-like responses in multiple languages"""
    logging.info(f"Processing question: {query}")
    
    try:
        # Step 1: Detect question type for smart handling
        question_type = detect_question_type(query)
        logging.info(f"Question type detected: {question_type}")
        
        # Step 2: Handle simple arithmetic directly with advanced calculator
        if question_type == 'simple_arithmetic':
            result = calculate_advanced_math(query)
            if result is not None:
                logging.info(f"Calculated advanced arithmetic: {query} = {result}")
                return format_human_response(
                    answer=result,
                    question_type=question_type,
                    question=query,
                    source_count=0,
                    language=language
                )
            else:
                # Fallback to web search if calculation fails
                question_type = 'math'
                logging.info("Advanced calculation failed, falling back to web search")
        
        # Step 2.5: Handle coding questions directly with code generation
        if question_type == 'coding':
            code_response = generate_code_response(query)
            if code_response:
                logging.info(f"Generated code for: {query}")
                return format_coding_response(code_response, query, language)
            else:
                # Fallback to web search if code generation fails
                question_type = 'general'
                logging.info("Code generation failed, falling back to web search")
        
        # Step 3: Get adaptive search parameters
        params = get_search_params(question_type)
        search_count = params['search_count']
        max_sentences = params['max_sentences']
        
        # Step 4: Enhance search query for better results
        enhanced_query = enhance_search_query(query, question_type)
        logging.info(f"Enhanced query: {enhanced_query}")
        
        # Step 5: Search with adaptive count (2-10 sites)
        links = search_duckduckgo(enhanced_query, n=search_count)
        if not links:
            # Language-specific "no results" messages
            no_results_msg = {
                'marathi': "क्षमस्व, काही परिणाम सापडले नाहीत. कृपया वेगळे शब्द वापरून पुन्हा प्रयत्न करा.",
                'hindi': "क्षमा करें, कोई परिणाम नहीं मिले। कृपया अलग शब्दों का उपयोग करके पुनः प्रयास करें।",
                'english': "Sorry, no results found. Please try again with different words.",
                'gujarati': "માફ કરશો, કોઈ પરિણામ મળ્યા નથી. કૃપા કરીને અલગ શબ્દો વાપરીને ફરી પ્રયાસ કરો.",
                'bengali': "দুঃখিত, কোনো ফলাফল পাওয়া যায়নি। অনুগ্রহ করে ভিন্ন শব্দ ব্যবহার করে আবার চেষ্টা করুন।",
                'tamil': "மன்னிக்கவும், எந்த முடிவும் கிடைக்கவில்லை. தயவுசெய்து வேறு வார்த்தைகளைப் பயன்படுத்தி மீண்டும் முயற்சி செய்யுங்கள்।",
                'telugu': "క్షమించండి, ఎలాంటి ఫలితాలు కనుగొనబడలేదు. దయచేసి వేరే పదాలను ఉపయోగించి మళ్లీ ప్రయత్నించండి।"
            }
            return no_results_msg.get(language, no_results_msg['marathi'])

        # Step 6: Extract content from multiple sources
        gathered = []
        processed_sources = []
        
        for i, url in enumerate(links, 1):
            try:
                logging.info(f"Processing source {i}/{search_count}: {url}")
                txt = extract_main_text(url)
                
                # Adaptive content length threshold
                min_length = 300 if question_type == 'simple' else 600
                if len(txt) > min_length:
                    gathered.append(txt)
                    processed_sources.append(url)
                
                # Respectful delay between requests
                time.sleep(1)
                
            except Exception as e:
                logging.warning(f"Skipping source {i}: {e}")

        if not gathered:
            # Language-specific "insufficient content" messages
            insufficient_content_msg = {
                'marathi': "परिणाम मिळाले, पण सारांशासाठी पुरेसा मजकूर मिळाला नाही. कृपया अधिक स्पष्ट प्रश्न विचारा.",
                'hindi': "परिणाम मिले, लेकिन सारांश के लिए पर्याप्त सामग्री नहीं मिली। कृपया अधिक स्पष्ट प्रश्न पूछें।",
                'english': "Results found, but not enough content for summary. Please ask a more specific question.",
                'gujarati': "પરિણામ મળ્યા, પરંતુ સારાંશ માટે પૂરતી સામગ્રી મળી નથી. કૃપા કરીને વધુ સ્પષ્ટ પ્રશ્ન પૂછો.",
                'bengali': "ফলাফল পাওয়া গেছে, কিন্তু সারসংক্ষেপের জন্য পর্যাপ্ত বিষয়বস্তু পাওয়া যায়নি। অনুগ্রহ করে আরো স্পষ্ট প্রশ্ন জিজ্ঞাসা করুন।",
                'tamil': "முடிவுகள் கிடைத்தன, ஆனால் சுருக்கத்திற்கு போதுமான உள்ளடக்கம் கிடைக்கவில்லை। தயவுசெய்து மிகவும் குறிப்பிட்ட கேள்வி கேளுங்கள்।",
                'telugu': "ఫలితాలు వచ్చాయి, కానీ సారాంశం కోసం తగినంత కంటెంట్ రాలేదు. దయచేసి మరింత స్పష్టమైన ప్రశ్న అడుగండి।"
            }
            return insufficient_content_msg.get(language, insufficient_content_msg['marathi'])

        # Step 7: Create intelligent summary based on question type
        big_text = " ".join(gathered)
        summary = summarize(big_text, max_sentences=max_sentences, question_type=question_type)

        # Step 8: Format human-like response
        final_response = format_human_response(
            answer=summary, 
            question_type=question_type, 
            question=query, 
            source_count=len(processed_sources),
            language=language
        )
        
        logging.info(f"Successfully processed {question_type} question with {len(processed_sources)} sources")
        return final_response
        
    except Exception as e:
        logging.error(f"Question processing failed: {e}")
        # Language-specific error messages
        error_msg = {
            'marathi': "तांत्रिक त्रुटी झाली. कृपया काही वेळानंतर पुन्हा प्रयत्न करा.",
            'hindi': "तकनीकी त्रुटि हुई। कृपया कुछ समय बाद पुनः प्रयास करें।",
            'english': "Technical error occurred. Please try again after some time.",
            'gujarati': "તકનીકી ભૂલ થઈ. કૃપા કરીને થોડી વાર પછી ફરી પ્રયાસ કરો.",
            'bengali': "প্রযুক্তিগত ত্রুটি হয়েছে। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।",
            'tamil': "தொழில்நுட்ப பிழை ஏற்பட்டது. தயவுசெய்து சிறிது நேரம் கழித்து மீண்டும் முயற்சி செய்யுங்கள்।",
            'telugu': "సాంకేతిక లోపం జరిగింది. దయచేసి కొంత సమయం తర్వాత మళ్లీ ప్రయత్నించండి।"
        }
        return error_msg.get(language, error_msg['marathi'])
