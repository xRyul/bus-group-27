// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initNavbarScroll();
});

/*
 * Initialize navbar scroll effect
 * Changes navbar background color and shadow when scrolling
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar-modern');
    function handleScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    }
    window.addEventListener('scroll', handleScroll);
    
    // Call once on page load to set initial state
    handleScroll();
}
