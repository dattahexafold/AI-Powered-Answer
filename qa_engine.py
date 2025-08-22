import requests, re, time
from bs4 import BeautifulSoup
from readability.readability import Document
import nltk
from nltk.tokenize import sent_tokenize
from collections import Counter
import logging

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logging.warning(f"NLTK download failed: {e}")

# --- Utility: साधं clean ---
def clean_text(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return t

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

# --- Step 3: सोपी extractive summary (language-agnostic) ---
def summarize(text, max_sentences=5):
    """Create extractive summary of text"""
    try:
        sents = [s.strip() for s in sent_tokenize(text) if len(s.strip()) > 40]
        if not sents:
            return text[:400] if text else "सारांश तयार करता आला नाही."

        # शब्द-frequency (stopwords शिवाय खूप बेसिक)
        words = re.findall(r'\w+', text.lower())
        cnt = Counter(w for w in words if len(w) > 3)
        
        # प्रत्येक वाक्याला स्कोर
        scores = []
        for s in sents:
            w = re.findall(r'\w+', s.lower())
            score = sum(cnt.get(x, 0) for x in w) / (len(w) + 1)
            scores.append((score, s))
        
        # टॉप वाक्ये क्रमाने
        top = [s for _, s in sorted(scores, key=lambda x: x[0], reverse=True)[:max_sentences]]
        
        # मूळ क्रम राखण्यासाठी:
        top_in_order = [s for s in sents if s in top][:max_sentences]
        return " ".join(top_in_order)
    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        return text[:400] if text else "सारांश तयार करता आला नाही."

# --- Step 4: मुख्य फंक्शन: इंटरनेटवरून उत्तर शोधून मराठीत साधं सांगणे ---
def answer_question(query):
    """Main function to search internet and provide summarized answer"""
    logging.info(f"Processing question: {query}")
    
    try:
        links = search_duckduckgo(query, n=3)
        if not links:
            return "क्षमस्व, काही परिणाम सापडले नाहीत. कृपया वेगळे शब्द वापरून पुन्हा प्रयत्न करा."

        gathered = []
        processed_sources = []
        
        for i, url in enumerate(links, 1):
            try:
                logging.info(f"Processing source {i}: {url}")
                txt = extract_main_text(url)
                if len(txt) > 500:
                    gathered.append(txt)
                    processed_sources.append(url)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logging.warning(f"Skipping source {i}: {e}")

        if not gathered:
            return "परिणाम मिळाले, पण सारांशासाठी पुरेसा मजकूर मिळाला नाही. कृपया अधिक स्पष्ट प्रश्न विचारा."

        # Combine all gathered text
        big = " ".join(gathered)
        sumy = summarize(big, max_sentences=5)

        # Format the response
        reply = f"""## साधं उत्तर (वेब सारांश)

{sumy}

---
**स्रोत:** {len(processed_sources)} वेब पृष्ठांवरून संकलित माहिती

*हा सारांश टॉप वेब स्रोतांवरून घेतलेल्या माहितीस आधारलेला आहे.*"""
        
        return reply
        
    except Exception as e:
        logging.error(f"Question processing failed: {e}")
        return "तांत्रिक त्रुटी झाली. कृपया काही वेळानंतर पुन्हा प्रयत्न करा."
