document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Sidebar dots navigation
const dots = document.querySelectorAll('.dot');
const sections = document.querySelectorAll('.hero-section, .photo-section, .legacy-section, .moments-section');

dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        dots.forEach(d => d.classList.remove('active'));
        dot.classList.add('active');
        if (sections[index]) {
            sections[index].scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Update active dot on scroll
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach((section, index) => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = index;
        }
    });

    dots.forEach((dot, index) => {
        dot.classList.remove('active');
        if (index === current) {
            dot.classList.add('active');
        }
    });
});

// Image hover effects
document.querySelectorAll('.category-card, .gallery-card').forEach(card => {
    card.addEventListener('mouseenter', function () {
        const img = this.querySelector('img');
        if (img) {
            img.style.transform = 'scale(1.1)';
            img.style.transition = 'transform 0.5s ease';
        }
    });

    card.addEventListener('mouseleave', function () {
        const img = this.querySelector('img');
        if (img) {
            img.style.transform = 'scale(1)';
        }
    });
});

// Button hover effects
document.querySelectorAll('button, .get-touch-btn, .explore-link, .book-link, .footer-book-btn').forEach(btn => {
    btn.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-2px)';
        this.style.transition = 'transform 0.3s ease';
    });

    btn.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0)';
    });
});

// Fade in elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.gallery-card, .category-card, .sidebar-card, .moment-card, .contact-section').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// Counter animation for stats
const statsElement = document.querySelector('.stats-badge');
let hasAnimated = false;

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !hasAnimated) {
            hasAnimated = true;
            let count = 0;
            const target = 2.6;
            const increment = target / 60;

            const counter = setInterval(() => {
                count += increment;
                if (count >= target) {
                    statsElement.innerHTML = '2.6K<br><small>Events Managed</small>';
                    clearInterval(counter);
                } else {
                    statsElement.innerHTML = count.toFixed(1) + 'K<br><small>Events Managed</small>';
                }
            }, 25);
        }
    });
});

if (statsElement) {
    statsObserver.observe(statsElement);
}

// Parallax effect for hero image
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroImage = document.querySelector('.hero-image img');
    if (heroImage && scrolled < 800) {
        heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Contact form submission
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const btn = this.querySelector('.submit-btn');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = 'SENDING... <i class="fas fa-spinner fa-spin"></i>';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = 'MESSAGE SENT! <i class="fas fa-check"></i>';
            btn.style.background = '#28a745';
            this.reset();

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '#ff6347';
                btn.disabled = false;
            }, 3000);
        }, 1500);
    });
}

// Mobile menu toggle
if (window.innerWidth <= 1200) {
    const nav = document.querySelector('nav');
    const navLinks = document.querySelector('.nav-links');

    const menuBtn = document.createElement('button');
    menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    menuBtn.style.cssText = 'background: none; border: none; font-size: 24px; cursor: pointer; color: #333;';

    nav.appendChild(menuBtn);
    navLinks.style.display = 'none';

    menuBtn.addEventListener('click', () => {
        if (navLinks.style.display === 'none' || navLinks.style.display === '') {
            navLinks.style.display = 'flex';
            navLinks.style.flexDirection = 'column';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '70px';
            navLinks.style.right = '20px';
            navLinks.style.background = 'white';
            navLinks.style.padding = '20px';
            navLinks.style.borderRadius = '8px';
            navLinks.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
            navLinks.style.zIndex = '1000';
        } else {
            navLinks.style.display = 'none';
        }
    });
}