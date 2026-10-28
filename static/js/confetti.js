/**
 * AURA FARMERS ANONYMOUS — confetti.js
 * Confetti Canvas Engine & High-Chaos Visual FX
 * "Log in. Lose your dignity."
 */

(function () {
    'use strict';

    const NEON_PALETTE = ['#ff2e9a', '#00f0ff', '#fff200', '#7b2cff', '#7dff00'];

    let canvas = null;
    let ctx = null;
    let particles = [];
    let animationFrameId = null;
    let burstEndTime = 0;

    /**
     * Get chaos level (1 to 5).
     */
    function getChaosLevel() {
        try {
            return parseInt(document.body.dataset.chaos || localStorage.getItem('chaos-level') || '3', 10);
        } catch (e) {
            return 3;
        }
    }

    /**
     * Prepare canvas element and resize to full viewport.
     */
    function getCanvas() {
        if (!canvas) {
            canvas = document.getElementById('confetti-canvas');
            if (!canvas) {
                canvas = document.createElement('canvas');
                canvas.id = 'confetti-canvas';
                document.body.appendChild(canvas);
            }
            ctx = canvas.getContext('2d');
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);
        }
        return canvas;
    }

    function resizeCanvas() {
        if (canvas) {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
    }

    /**
     * Spawn 100+ confetti particles at the center-top of screen.
     */
    function confettiBurst() {
        if (getChaosLevel() < 2) return;

        getCanvas();
        if (!ctx) return;

        const count = 120;
        const originX = window.innerWidth / 2;
        const originY = 20;

        for (let i = 0; i < count; i++) {
            const isCircle = Math.random() < 0.35;
            const color = NEON_PALETTE[Math.floor(Math.random() * NEON_PALETTE.length)];
            const angle = (Math.random() * Math.PI) - (Math.PI / 2); // Spread outward
            const speed = 4 + Math.random() * 12;

            particles.push({
                x: originX + (Math.random() * 160 - 80),
                y: originY + (Math.random() * 40),
                vx: Math.cos(angle) * speed + (Math.random() * 4 - 2),
                vy: Math.sin(angle) * speed + (Math.random() * 2),
                gravity: 0.18 + Math.random() * 0.14,
                drag: 0.985,
                color: color,
                isCircle: isCircle,
                width: 7 + Math.random() * 6,
                height: 10 + Math.random() * 8,
                radius: 4 + Math.random() * 4,
                rotation: Math.random() * Math.PI * 2,
                rotationSpeed: (Math.random() - 0.5) * 0.2,
                alpha: 1.0,
                decay: 0.003 + Math.random() * 0.005
            });
        }

        burstEndTime = Date.now() + 3000;

        if (!animationFrameId) {
            animateConfetti();
        }
    }

    function animateConfetti() {
        if (!ctx || !canvas) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const now = Date.now();
        const isTimeUp = now >= burstEndTime;

        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];

            p.vx *= p.drag;
            p.vy += p.gravity;
            p.x += p.vx;
            p.y += p.vy;
            p.rotation += p.rotationSpeed;
            p.alpha -= p.decay;

            if (p.alpha <= 0 || p.y > canvas.height + 20) {
                particles.splice(i, 1);
                continue;
            }

            ctx.save();
            ctx.globalAlpha = Math.max(0, p.alpha);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;

            if (p.isCircle) {
                ctx.beginPath();
                ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
                ctx.fill();
            } else {
                ctx.fillRect(-p.width / 2, -p.height / 2, p.width, p.height);
            }

            ctx.restore();
        }

        if (particles.length > 0 && !isTimeUp) {
            animationFrameId = requestAnimationFrame(animateConfetti);
        } else if (particles.length > 0 && isTimeUp) {
            // Fade out rest quickly
            for (let i = 0; i < particles.length; i++) {
                particles[i].alpha -= 0.05;
            }
            animationFrameId = requestAnimationFrame(animateConfetti);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles = [];
            animationFrameId = null;
        }
    }

    /**
     * Screen shake:
     * Add 'screen-shake' class to document.body for 500ms and play fail sound.
     */
    function screenShake() {
        if (getChaosLevel() < 2) return;

        document.body.classList.remove('screen-shake');
        void document.body.offsetHeight; // force reflow
        document.body.classList.add('screen-shake');

        if (window.AuraSound && typeof window.AuraSound.playFail === 'function') {
            window.AuraSound.playFail();
        }

        setTimeout(() => {
            document.body.classList.remove('screen-shake');
        }, 500);
    }

    /**
     * Rainbow flash:
     * Add 'rainbow-flash' class to document.body for 1s, play success sound + confetti.
     */
    function rainbowFlash() {
        if (getChaosLevel() < 2) return;

        document.body.classList.remove('rainbow-flash');
        void document.body.offsetHeight;
        document.body.classList.add('rainbow-flash');

        if (window.AuraSound && typeof window.AuraSound.playSuccess === 'function') {
            window.AuraSound.playSuccess();
        }

        confettiBurst();

        setTimeout(() => {
            document.body.classList.remove('rainbow-flash');
        }, 1000);
    }

    /**
     * Red flash:
     * Create a full-screen red overlay div, fade in/out over 500ms, then remove.
     */
    function redFlash() {
        if (getChaosLevel() < 2) return;

        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.45)';
        overlay.style.pointerEvents = 'none';
        overlay.style.zIndex = '99998';
        overlay.style.transition = 'opacity 0.5s ease-out';
        overlay.style.opacity = '1';

        document.body.appendChild(overlay);

        requestAnimationFrame(() => {
            overlay.style.opacity = '0';
        });

        setTimeout(() => {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        }, 520);
    }

    /**
     * Auto-trigger effects based on flash messages or URL params on page load.
     */
    function checkPageTriggers() {
        // 1. Check flash messages in the DOM
        const hasSuccessFlash = Boolean(
            document.querySelector('.flash-success, .alert-success, [data-category="success"]')
        );
        const hasErrorFlash = Boolean(
            document.querySelector('.flash-error, .flash-danger, .alert-danger, [data-category="error"]')
        );

        // 2. Check URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const urlStatus = urlParams.get('status') || urlParams.get('result');

        if (hasSuccessFlash || urlStatus === 'success' || urlStatus === 'pass') {
            setTimeout(() => {
                rainbowFlash();
                if (window.mascotReact) window.mascotReact('pass');
            }, 300);
        } else if (hasErrorFlash || urlStatus === 'error' || urlStatus === 'fail') {
            setTimeout(() => {
                screenShake();
                redFlash();
                if (window.mascotReact) window.mascotReact('fail');
            }, 300);
        }
    }

    document.addEventListener('DOMContentLoaded', checkPageTriggers);

    // Global exposure
    window.confettiBurst = confettiBurst;
    window.screenShake = screenShake;
    window.rainbowFlash = rainbowFlash;
    window.redFlash = redFlash;
})();
