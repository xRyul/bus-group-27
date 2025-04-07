// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initAnimations();
    initInteractiveElements();
});

/*
 * Initialize animations for page elements
 */
function initAnimations() {
    // Add fade-in class to elements that should animate in
    const fadeElements = document.querySelectorAll('.modern-card, .greenscore-section');
    fadeElements.forEach(element => {
        element.classList.add('fade-in');
    });
    
    // Activate elements on page load with a slight delay
    setTimeout(function() {
        fadeElements.forEach(element => {
            element.classList.add('active');
        });
    }, 100);
    
    // Add scroll-based animations
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY + window.innerHeight * 0.8;
        
        // Find all elements with fade-in class
        document.querySelectorAll('.fade-in:not(.active)').forEach(element => {
            // If the element is in view, add the active class
            if (element.offsetTop < scrollPosition) {
                element.classList.add('active');
            }
        });
    });
}

/*
 * Initialize interactive elements on the page/ add hover effects for feature cards
 */
function initInteractiveElements() {

    const featureCards = document.querySelectorAll('.modern-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}
