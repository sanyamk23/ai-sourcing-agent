/**
 * MOTION UTILITIES
 * JavaScript helpers for advanced animations
 * Includes scroll observers, intersection observers, and dynamic animations
 */

class MotionSystem {
    constructor() {
        this.observers = new Map();
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupParallax();
    }

    /**
     * SCROLL-TRIGGERED ANIMATIONS
     */
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Optional: unobserve after animation
                    // observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all scroll-animated elements
        const scrollElements = document.querySelectorAll(
            '.scroll-fade-in, .scroll-slide-left, .scroll-slide-right, ' +
            '.scroll-scale-in, .scroll-reveal-blur, .scroll-stagger-cascade'
        );

        scrollElements.forEach(el => observer.observe(el));
        this.observers.set('scroll', observer);
    }

    /**
     * MAGNETIC HOVER EFFECT
     * Elements follow cursor on hover
     */
    setupHoverEffects() {
        const magneticElements = document.querySelectorAll('.btn-magnetic, .hover-magnetic');

        magneticElements.forEach(el => {
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;

                const moveX = x * 0.15;
                const moveY = y * 0.15;

                el.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.05)`;
            });

            el.addEventListener('mouseleave', () => {
                el.style.transform = 'translate(0, 0) scale(1)';
            });
        });
    }

    /**
     * PARALLAX SCROLLING
     */
    setupParallax() {
        const parallaxElements = document.querySelectorAll(
            '.parallax-layer-1, .parallax-layer-2, .parallax-layer-3'
        );

        if (parallaxElements.length === 0) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;

            parallaxElements.forEach(el => {
                const speed = el.classList.contains('parallax-layer-1') ? 0.5 :
                             el.classList.contains('parallax-layer-2') ? 0.3 :
                             0.1;

                const yPos = -(scrolled * speed);
                el.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    /**
     * RIPPLE EFFECT
     * Creates ripple on click
     */
    static createRipple(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        ripple.classList.add('ripple-effect');

        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    /**
     * STAGGER ANIMATION
     * Animates children with delay
     */
    static staggerChildren(parent, delay = 100) {
        const children = parent.children;
        Array.from(children).forEach((child, index) => {
            child.style.animationDelay = `${index * delay}ms`;
            child.classList.add('slide-fade-in');
        });
    }

    /**
     * CONFETTI BURST
     * Creates confetti explosion
     */
    static confettiBurst(x, y, count = 20) {
        const colors = ['#10B981', '#0555C8', '#00D9FF', '#F59E0B', '#EF4444'];
        
        for (let i = 0; i < count; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.left = `${x}px`;
            confetti.style.top = `${y}px`;
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
            
            const angle = (Math.PI * 2 * i) / count;
            const velocity = 100 + Math.random() * 100;
            const vx = Math.cos(angle) * velocity;
            const vy = Math.sin(angle) * velocity;
            
            confetti.style.setProperty('--vx', `${vx}px`);
            confetti.style.setProperty('--vy', `${vy}px`);
            
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 1500);
        }
    }

    /**
     * SMOOTH SCROLL TO ELEMENT
     */
    static smoothScrollTo(element, offset = 0) {
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }

    /**
     * ANIMATE NUMBER COUNTER
     */
    static animateCounter(element, start, end, duration = 2000) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = Math.round(end);
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, 16);
    }

    /**
     * MORPH ELEMENT
     * Smoothly morphs one element into another
     */
    static morphElement(fromEl, toEl, duration = 600) {
        const fromRect = fromEl.getBoundingClientRect();
        const toRect = toEl.getBoundingClientRect();

        const clone = fromEl.cloneNode(true);
        clone.style.position = 'fixed';
        clone.style.top = `${fromRect.top}px`;
        clone.style.left = `${fromRect.left}px`;
        clone.style.width = `${fromRect.width}px`;
        clone.style.height = `${fromRect.height}px`;
        clone.style.margin = '0';
        clone.style.transition = `all ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
        clone.style.zIndex = '9999';

        document.body.appendChild(clone);

        fromEl.style.opacity = '0';
        toEl.style.opacity = '0';

        requestAnimationFrame(() => {
            clone.style.top = `${toRect.top}px`;
            clone.style.left = `${toRect.left}px`;
            clone.style.width = `${toRect.width}px`;
            clone.style.height = `${toRect.height}px`;
        });

        setTimeout(() => {
            clone.remove();
            fromEl.style.opacity = '';
            toEl.style.opacity = '1';
        }, duration);
    }

    /**
     * SHAKE ELEMENT
     */
    static shake(element) {
        element.classList.add('error-shake');
        setTimeout(() => element.classList.remove('error-shake'), 500);
    }

    /**
     * PULSE ELEMENT
     */
    static pulse(element, duration = 2000) {
        element.classList.add('pulse');
        setTimeout(() => element.classList.remove('pulse'), duration);
    }

    /**
     * BOUNCE ELEMENT
     */
    static bounce(element) {
        element.classList.add('bounce');
        setTimeout(() => element.classList.remove('bounce'), 600);
    }

    /**
     * LOADING STATE MANAGER
     */
    static showLoading(element, type = 'spinner') {
        const loaders = {
            spinner: '<div class="spinner"></div>',
            dots: '<div class="loading-dots"><span></span><span></span><span></span></div>',
            orbital: '<div class="loader-orbital"></div>',
            quantum: '<div class="loader-quantum"><span></span><span></span><span></span></div>',
            morph: '<div class="loader-morph"></div>'
        };

        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = loaders[type] || loaders.spinner;
        element.disabled = true;
        element.style.pointerEvents = 'none';
    }

    static hideLoading(element) {
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
        element.style.pointerEvents = '';
    }

    /**
     * TOAST NOTIFICATION
     */
    static showToast(message, type = 'success', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `notification-toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * MODAL MANAGER
     */
    static openModal(modalId, animationType = 'cinematic') {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('active');
        const content = modal.querySelector('.modal-content, .workflow-modal, .matching-modal');
        
        if (content) {
            content.classList.add(`modal-${animationType}`);
        }

        document.body.style.overflow = 'hidden';
    }

    static closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * CARD FLIP
     */
    static flipCard(card) {
        card.style.transform = card.style.transform === 'rotateY(180deg)' 
            ? 'rotateY(0deg)' 
            : 'rotateY(180deg)';
    }

    /**
     * PROGRESS BAR ANIMATION
     */
    static animateProgress(progressBar, targetPercent, duration = 1000) {
        const fill = progressBar.querySelector('.progress-fill, .progress-fill-new');
        if (!fill) return;

        let currentPercent = 0;
        const increment = targetPercent / (duration / 16);

        const timer = setInterval(() => {
            currentPercent += increment;
            if (currentPercent >= targetPercent) {
                fill.style.width = `${targetPercent}%`;
                clearInterval(timer);
            } else {
                fill.style.width = `${currentPercent}%`;
            }
        }, 16);
    }

    /**
     * TYPEWRITER EFFECT
     */
    static typeWriter(element, text, speed = 50) {
        element.textContent = '';
        let i = 0;

        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    }

    /**
     * CLEANUP
     */
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

// Initialize motion system when DOM is ready
let motionSystem;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        motionSystem = new MotionSystem();
    });
} else {
    motionSystem = new MotionSystem();
}

// Export for use in other scripts
window.MotionSystem = MotionSystem;
window.motionSystem = motionSystem;
