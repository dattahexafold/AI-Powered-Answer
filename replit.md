# Overview

This is a Marathi language Question-Answer web application built with Flask that provides intelligent answers based on web search results. The system searches the web using DuckDuckGo, extracts relevant content from webpages, and presents summarized answers to user questions in Marathi.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap CSS framework
- **Design Pattern**: Single Page Application (SPA) with AJAX-based interactions
- **UI Framework**: Bootstrap with dark theme and Replit agent styling
- **Language Support**: Marathi language interface with bilingual error messages
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system

## Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Simple MVC structure with separation of concerns
- **Main Components**:
  - `app.py`: Main Flask application with route handlers
  - `qa_engine.py`: Core question-answering logic and web scraping
  - `main.py`: Application entry point
- **API Design**: RESTful endpoints with JSON responses for AJAX communication
- **Error Handling**: Comprehensive exception handling with user-friendly Marathi error messages

## Enhanced Question-Answer Engine
- **Intelligent Question Detection**: Automatically detects question types (math, complex, simple, general)
- **Adaptive Search Strategy**: 
  - Math questions: 8 sources with enhanced mathematical search terms
  - Complex questions: 10 sources for comprehensive coverage  
  - Simple questions: 4 sources for quick facts
  - General questions: 6 sources for balanced information
- **Enhanced Search Queries**: Query enhancement based on question type for better results
- **Content Extraction**: 
  - Uses `readability-lxml` library for main content extraction
  - BeautifulSoup for HTML parsing
  - NLTK for text tokenization and processing
- **Smart Summarization**: 
  - Math questions: Prioritizes numerical data, formulas, and solution steps
  - Other questions: Frequency-based extractive summarization
  - Adaptive sentence count (4-12 sentences based on question complexity)
- **Human-like Responses**: Natural, conversational formatting with varied introductions and conclusions
- **Language Processing**: Language-agnostic approach with NLTK punkt tokenizer

## Enhanced Data Processing Pipeline
1. **Question Analysis Phase**: Detect question type and complexity using pattern matching
2. **Query Enhancement Phase**: Enhance search terms based on question type
3. **Adaptive Search Phase**: Search 2-10 sources based on question requirements
4. **Smart Extraction Phase**: Extract content with adaptive quality thresholds
5. **Intelligent Summarization Phase**: Type-aware summarization with priority scoring
6. **Human-like Response Phase**: Format responses with natural language patterns

# External Dependencies

## Python Libraries
- **Flask**: Web framework for application server
- **requests**: HTTP client for web scraping and search
- **BeautifulSoup (bs4)**: HTML/XML parsing for content extraction
- **readability**: Main content extraction from web pages
- **nltk**: Natural language processing and tokenization
- **lxml**: XML/HTML parser (BeautifulSoup backend)

## Frontend Libraries
- **Bootstrap**: CSS framework with dark theme support
- **Bootstrap Icons**: Icon library for UI elements
- **Replit Bootstrap Theme**: Custom dark theme styling

## External Services
- **DuckDuckGo HTML Search**: Web search engine (no API key required)
- **Web Content Sources**: Various websites for answer generation
- **NLTK Data**: Punkt tokenizer models for sentence segmentation

## Browser APIs
- **Fetch API**: For AJAX requests to backend
- **DOM API**: For dynamic content manipulation
- **Clipboard API**: For copy-to-clipboard functionality (implied by copy button)