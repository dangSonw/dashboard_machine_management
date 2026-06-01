/* Blog Page JavaScript */

// Smooth transitions for hover effects
document.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('mouseenter', () => {
        el.style.transition = "all 0.2s ease-in-out";
    });
});

// Simple observer for scroll animations
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('opacity-100');
            entry.target.classList.remove('translate-y-10');
            entry.target.classList.remove('opacity-0');
        }
    });
}, observerOptions);

document.querySelectorAll('section > div').forEach(el => {
    el.classList.add('transition-all', 'duration-700', 'opacity-0', 'translate-y-10');
    observer.observe(el);
});