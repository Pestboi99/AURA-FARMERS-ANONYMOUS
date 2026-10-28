/**
 * AURA FARMERS ANONYMOUS — mascot.js
 * Tung Tung Mascot Character, Cursor Following, & Dynamic Reactions
 * "Log in. Lose your dignity."
 */

(function () {
    'use strict';

    let mascotContainer = null;
    let speechBubble = null;
    let eyesGroup = null;
    let mouthPath = null;
    let speechTimeout = null;
    let faceResetTimeout = null;

    let posX = 30;
    let posY = 300;
    let targetX = 30;
    let targetY = 300;
    let isTracking = false;
    let isMobile = false;

    const PASS_PHRASES = [
        'The vibes are immaculate',
        'Sigma detected?',
        'W rizz fr fr',
        'Aura stonks 📈',
        'Bro actually cooked!',
        'Immaculate jawline geometry',
        'Certified sigma entry!'
    ];

    const FAIL_PHRASES = [
        'No cap, that was sus',
        'Your aura is mid',
        'Cooked in Ohio 💀',
        'Major L bestie',
        'Sentenced to 100 years of mewing',
        'Bro got mogged by a wooden log',
        'Down bad in Ohio fr'
    ];

    const IDLE_PHRASES = [
        'Tung tung tung!',
        'Still mewing? 🗿',
        'Did you pay Fanum tax?',
        'Aura audit in progress...',
        'Don\'t drop your aura!',
        'Tung tung tung sahur!',
        'The Bouncer is watching 👀'
    ];

    /**
     * Build inline SVG for the cartoon wooden log character with a bat.
     */
    function createMascotSVG() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 80 100');
        svg.setAttribute('width', '80');
        svg.setAttribute('height', '100');
        svg.style.overflow = 'visible';

        svg.innerHTML = `
            <!-- Stick Legs & Feet -->
            <line x1="32" y1="72" x2="30" y2="88" stroke="#3D2314" stroke-width="3.5" stroke-linecap="round"/>
            <line x1="48" y1="72" x2="50" y2="88" stroke="#3D2314" stroke-width="3.5" stroke-linecap="round"/>
            <ellipse cx="28" cy="88" rx="4.5" ry="2.5" fill="#3D2314"/>
            <ellipse cx="52" cy="88" rx="4.5" ry="2.5" fill="#3D2314"/>

            <!-- Wooden Log Body -->
            <rect x="22" y="20" width="36" height="52" rx="10" ry="10" fill="#8B5A2B" stroke="#3D2314" stroke-width="3"/>

            <!-- Wood Grain Texture -->
            <path d="M 28 32 Q 38 35 34 50 Q 30 60 38 65" fill="none" stroke="#6F421B" stroke-width="2" stroke-linecap="round"/>
            <path d="M 48 26 Q 52 40 46 54 Q 44 64 50 68" fill="none" stroke="#6F421B" stroke-width="2" stroke-linecap="round"/>

            <!-- Top Tree Rings Cap -->
            <ellipse cx="40" cy="22" rx="17" ry="5.5" fill="#CD853F" stroke="#3D2314" stroke-width="2.5"/>
            <ellipse cx="40" cy="22" rx="9" ry="2.8" fill="none" stroke="#8B5A2B" stroke-width="1.8"/>

            <!-- Face Group -->
            <g id="mascot-face">
                <g id="mascot-eyes">
                    <circle cx="33" cy="38" r="2.5" fill="#000"/>
                    <circle cx="47" cy="38" r="2.5" fill="#000"/>
                </g>
                <path id="mascot-mouth" d="M 32 46 Q 40 52 48 46" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round"/>
            </g>

            <!-- Stick Arms & Bat -->
            <!-- Left Arm -->
            <path d="M 22 45 Q 12 50 15 58" fill="none" stroke="#3D2314" stroke-width="3.2" stroke-linecap="round"/>

            <!-- Right Arm Holding Bat -->
            <path d="M 58 45 Q 68 46 64 36" fill="none" stroke="#3D2314" stroke-width="3.2" stroke-linecap="round"/>

            <!-- Wooden Bat / Club -->
            <path d="M 62 38 L 74 14 Q 78 11 77 16 L 66 40 Z" fill="#D2B48C" stroke="#5C3317" stroke-width="2"/>
            <line x1="62" y1="36" x2="65" y2="40" stroke="#8B0000" stroke-width="2"/>
        `;

        return svg;
    }

    /**
     * Show speech bubble with specified text for 3 seconds.
     */
    function showSpeech(text) {
        if (!speechBubble) return;

        if (speechTimeout) clearTimeout(speechTimeout);

        speechBubble.textContent = text;
        speechBubble.classList.add('visible');

        speechTimeout = setTimeout(() => {
            speechBubble.classList.remove('visible');
        }, 3000);
    }

    /**
     * Set mascot facial expression.
     */
    function setFace(type) {
        if (!eyesGroup || !mouthPath) return;

        if (faceResetTimeout) clearTimeout(faceResetTimeout);

        if (type === 'pass') {
            // Happy ^_^ eyes + big grin
            eyesGroup.innerHTML = `
                <path d="M 30 39 Q 33 34 36 39" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M 44 39 Q 47 34 50 39" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round"/>
            `;
            mouthPath.setAttribute('d', 'M 32 45 Q 40 56 48 45');
        } else if (type === 'fail') {
            // Sad / dead X_X eyes + frown
            eyesGroup.innerHTML = `
                <path d="M 31 36 L 36 41 M 36 36 L 31 41" stroke="#000" stroke-width="2" stroke-linecap="round"/>
                <path d="M 45 36 L 50 41 M 50 36 L 45 41" stroke="#000" stroke-width="2" stroke-linecap="round"/>
            `;
            mouthPath.setAttribute('d', 'M 32 50 Q 40 43 48 50');
        } else {
            // Neutral face (default)
            eyesGroup.innerHTML = `
                <circle cx="33" cy="38" r="2.5" fill="#000"/>
                <circle cx="47" cy="38" r="2.5" fill="#000"/>
            `;
            mouthPath.setAttribute('d', 'M 32 46 Q 40 52 48 46');
        }

        // Return to neutral face after 3.5 seconds
        if (type !== 'neutral') {
            faceResetTimeout = setTimeout(() => {
                setFace('neutral');
            }, 3500);
        }
    }

    /**
     * Mascot reaction dispatcher.
     */
    function mascotReact(type) {
        if (type === 'pass') {
            setFace('pass');
            const phrase = PASS_PHRASES[Math.floor(Math.random() * PASS_PHRASES.length)];
            showSpeech(phrase);
        } else if (type === 'fail') {
            setFace('fail');
            const phrase = FAIL_PHRASES[Math.floor(Math.random() * FAIL_PHRASES.length)];
            showSpeech(phrase);
        } else if (type === 'idle') {
            const phrase = IDLE_PHRASES[Math.floor(Math.random() * IDLE_PHRASES.length)];
            showSpeech(phrase);
        }
    }

    /**
     * Smooth cursor tracking loop with lerp 0.05.
     */
    function animateCursorFollowing() {
        if (!isMobile && isTracking && mascotContainer) {
            // Lerp with 0.05 factor
            posX += (targetX - posX) * 0.05;
            posY += (targetY - posY) * 0.05;

            // Viewport boundary clamp
            const mascotW = 90;
            const mascotH = 110;
            const clampedX = Math.max(10, Math.min(window.innerWidth - mascotW, posX));
            const clampedY = Math.max(10, Math.min(window.innerHeight - mascotH, posY));

            mascotContainer.style.transform = `translate3d(${clampedX.toFixed(1)}px, ${clampedY.toFixed(1)}px, 0)`;
        }

        requestAnimationFrame(animateCursorFollowing);
    }

    /**
     * Initialize Mascot Container and Events.
     */
    function initMascot() {
        mascotContainer = document.getElementById('mascot-container');
        if (!mascotContainer) {
            mascotContainer = document.createElement('div');
            mascotContainer.id = 'mascot-container';
            document.body.appendChild(mascotContainer);
        }

        // Check mobile
        isMobile = (window.innerWidth < 768) || ('ontouchstart' in window);

        // Speech bubble
        speechBubble = mascotContainer.querySelector('.mascot-speech');
        if (!speechBubble) {
            speechBubble = document.createElement('div');
            speechBubble.className = 'mascot-speech';
            mascotContainer.appendChild(speechBubble);
        }

        // Add SVG
        const svgElement = createMascotSVG();
        mascotContainer.appendChild(svgElement);

        eyesGroup = mascotContainer.querySelector('#mascot-eyes');
        mouthPath = mascotContainer.querySelector('#mascot-mouth');

        if (isMobile) {
            // Mobile: keep pinned bottom-left
            mascotContainer.style.position = 'fixed';
            mascotContainer.style.bottom = '20px';
            mascotContainer.style.left = '20px';
            mascotContainer.style.top = 'auto';
            mascotContainer.style.transform = 'none';
        } else {
            // Desktop: prepare absolute positioning for translate3d
            mascotContainer.style.position = 'fixed';
            mascotContainer.style.top = '0px';
            mascotContainer.style.left = '0px';
            mascotContainer.style.bottom = 'auto';

            // Initial position bottom left
            posX = 30;
            posY = Math.max(100, window.innerHeight - 150);
            targetX = posX;
            targetY = posY;
            mascotContainer.style.transform = `translate3d(${posX}px, ${posY}px, 0)`;

            window.addEventListener('mousemove', function (e) {
                isTracking = true;
                // Mascot slightly offset from cursor so it doesn't block clicks
                targetX = e.clientX + 25;
                targetY = e.clientY + 25;
            }, { passive: true });

            requestAnimationFrame(animateCursorFollowing);
        }

        // Idle speech interval (every 20-30s)
        function scheduleNextIdleSpeech() {
            const delay = Math.floor(20000 + Math.random() * 10000);
            setTimeout(() => {
                mascotReact('idle');
                scheduleNextIdleSpeech();
            }, delay);
        }
        scheduleNextIdleSpeech();

        // Resize handler for responsive switch
        window.addEventListener('resize', function () {
            isMobile = (window.innerWidth < 768) || ('ontouchstart' in window);
            if (isMobile) {
                mascotContainer.style.top = 'auto';
                mascotContainer.style.bottom = '20px';
                mascotContainer.style.left = '20px';
                mascotContainer.style.transform = 'none';
            } else {
                mascotContainer.style.top = '0px';
                mascotContainer.style.left = '0px';
                mascotContainer.style.bottom = 'auto';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initMascot);

    // Global exposure
    window.mascotReact = mascotReact;
})();
