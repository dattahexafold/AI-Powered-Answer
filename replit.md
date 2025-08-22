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

## Question-Answer Engine
- **Search Strategy**: DuckDuckGo HTML search (no API key required)
- **Content Extraction**: 
  - Uses `readability` library for main content extraction
  - BeautifulSoup for HTML parsing
  - NLTK for text tokenization and processing
- **Summarization**: Custom extractive summarization algorithm based on word frequency
- **Language Processing**: Language-agnostic approach with NLTK punkt tokenizer

## Data Processing Pipeline
1. **Search Phase**: Query DuckDuckGo for relevant web pages
2. **Extraction Phase**: Extract main content using readability algorithms
3. **Summarization Phase**: Generate concise summaries using sentence scoring
4. **Response Phase**: Return structured JSON responses to frontend

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