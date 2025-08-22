// Question-Answer System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const questionForm = document.getElementById('questionForm');
    const questionInput = document.getElementById('questionInput');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSection = document.getElementById('loadingSection');
    const answerSection = document.getElementById('answerSection');
    const errorSection = document.getElementById('errorSection');
    const questionDisplay = document.getElementById('questionDisplay');
    const answerContent = document.getElementById('answerContent');
    const errorMessage = document.getElementById('errorMessage');
    const copyBtn = document.getElementById('copyBtn');
    const newQuestionBtn = document.getElementById('newQuestionBtn');

    // Form submission handler
    questionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) {
            showError('कृपया प्रश्न लिहा.');
            return;
        }

        if (question.length < 5) {
            showError('प्रश्न खूप लहान आहे. कृपया अधिक तपशील द्या.');
            return;
        }

        // Show loading state
        showLoading();
        
        // Prepare form data
        const formData = new FormData();
        formData.append('question', question);

        // Submit question
        fetch('/ask', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                showAnswer(data.question, data.answer);
            } else {
                showError(data.error || 'तांत्रिक त्रुटी झाली.');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showError('नेटवर्क त्रुटी झाली. कृपया पुन्हा प्रयत्न करा.');
        });
    });

    // Copy answer functionality
    copyBtn.addEventListener('click', function() {
        const answerText = answerContent.textContent || answerContent.innerText;
        
        navigator.clipboard.writeText(answerText).then(function() {
            // Show success feedback
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check"></i>';
            copyBtn.classList.add('btn-success-temp');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                copyBtn.classList.remove('btn-success-temp');
            }, 2000);
        }).catch(function(err) {
            console.error('Copy failed:', err);
            showError('कॉपी करता आली नाही.');
        });
    });

    // New question button
    newQuestionBtn.addEventListener('click', function() {
        resetForm();
        questionInput.focus();
    });

    // Auto-resize textarea
    questionInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Helper functions
    function showLoading() {
        hideAllSections();
        loadingSection.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>शोधत आहे...';
    }

    function hideLoading() {
        loadingSection.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-search me-2"></i>उत्तर शोधा';
    }

    function showAnswer(question, answer) {
        hideAllSections();
        
        // Display question
        questionDisplay.innerHTML = `<strong>प्रश्न:</strong> ${escapeHtml(question)}`;
        
        // Display answer (convert markdown-like formatting to HTML)
        answerContent.innerHTML = formatAnswer(answer);
        
        answerSection.style.display = 'block';
        answerSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showError(message) {
        hideAllSections();
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function hideAllSections() {
        loadingSection.style.display = 'none';
        answerSection.style.display = 'none';
        errorSection.style.display = 'none';
    }

    function resetForm() {
        questionInput.value = '';
        questionInput.style.height = 'auto';
        hideAllSections();
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatAnswer(answer) {
        // Simple markdown-like formatting
        let formatted = escapeHtml(answer);
        
        // Headers
        formatted = formatted.replace(/^## (.+)$/gm, '<h4 class="text-primary mt-3 mb-2">$1</h4>');
        formatted = formatted.replace(/^# (.+)$/gm, '<h3 class="text-primary mt-3 mb-2">$1</h3>');
        
        // Bold text
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Horizontal rules
        formatted = formatted.replace(/^---$/gm, '<hr class="my-3">');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Multiple line breaks to paragraphs
        formatted = formatted.replace(/(<br>\s*){2,}/g, '</p><p class="mb-3">');
        
        // Wrap in paragraphs
        if (!formatted.startsWith('<h')) {
            formatted = '<p class="mb-3">' + formatted + '</p>';
        } else {
            formatted = formatted + '<p class="mb-3"></p>';
        }
        
        return formatted;
    }

    // Focus on question input when page loads
    questionInput.focus();
});
