// Main JavaScript for RAG-Powered Agent

// This file contains additional JavaScript functionality beyond the
// Alpine.js functionality defined in the HTML templates

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling for results container
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        resultsContainer.style.scrollBehavior = 'smooth';
    }
    
    // Add keyboard shortcut (Ctrl+Enter) to submit query
    document.addEventListener('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const submitButton = document.querySelector('form button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
            }
        }
    });
    
    // Add scroll-to-top functionality
    window.addEventListener('scroll', function() {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollTopButton = document.getElementById('scroll-top-button');
        
        if (scrollTopButton) {
            if (scrollTop > 300) {
                scrollTopButton.classList.remove('hidden');
            } else {
                scrollTopButton.classList.add('hidden');
            }
        }
    });
    
    // Helper function to scroll to top
    window.scrollToTop = function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };
    
    // Initialize tooltips if any are present
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltipElement = document.createElement('div');
            tooltipElement.classList.add('tooltip');
            tooltipElement.textContent = tooltipText;
            
            document.body.appendChild(tooltipElement);
            
            const rect = this.getBoundingClientRect();
            tooltipElement.style.left = rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2) + 'px';
            tooltipElement.style.top = rect.top - tooltipElement.offsetHeight - 10 + 'px';
            
            this.addEventListener('mouseleave', function() {
                document.body.removeChild(tooltipElement);
            }, { once: true });
        });
    });
    
    // Markdown rendering helper (if needed)
    window.renderMarkdown = function(text) {
        if (!text) return '';
        
        // Simple Markdown parsing for common elements
        let html = text;
        
        // Convert headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        
        // Convert bold and italic
        html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
        
        // Convert lists
        html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/<\/li>\n<li>/gim, '</li><li>');
        html = html.replace(/(<li>.*?<\/li>)/gim, '<ul>$1</ul>');
        
        // Convert line breaks
        html = html.replace(/\n/gim, '<br>');
        
        return html;
    };
});