/**
 * AURA FARMERS ANONYMOUS — main.js
 * Core UI Logic, Easter Eggs, Modals, & Absurd Chaos
 * "Log in. Lose your dignity."
 */

(function () {
    'use strict';

    /**
     * Escape HTML string helper
     */
    function escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /* ──────────────────────────────────────────────
       1. Splash Screen Handler
       ────────────────────────────────────────────── */
    function initSplashScreen() {
        const splash = document.querySelector('.splash-screen');
        if (!splash) return;

        if (sessionStorage.getItem('splashDismissed') === 'true') {
            if (splash.parentNode) splash.parentNode.removeChild(splash);
            return;
        }

        function dismissSplash() {
            sessionStorage.setItem('splashDismissed', 'true');
            if (window.AuraSound && typeof window.AuraSound.unlock === 'function') {
                window.AuraSound.unlock();
            }
            splash.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            splash.style.opacity = '0';
            splash.style.transform = 'scale(1.05)';
            setTimeout(() => {
                if (splash.parentNode) splash.parentNode.removeChild(splash);
            }, 360);
        }

        splash.addEventListener('click', dismissSplash);
        window.addEventListener('keydown', function onKey(e) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
                dismissSplash();
                window.removeEventListener('keydown', onKey);
            }
        });
    }

    /* ──────────────────────────────────────────────
       2. Emoji Rain
       ────────────────────────────────────────────── */
    const RAIN_EMOJIS = ['💀', '🔥', '🚽', '🗿', '😂', '💅', '🧠', '👁️', '🐐', '✨'];

    function getEmojiRainContainer() {
        let container = document.getElementById('emoji-rain');
        if (!container) {
            container = document.createElement('div');
            container.id = 'emoji-rain';
            document.body.prepend(container);
        }
        return container;
    }

    function createSingleEmojiDrop(container, isBonus) {
        const drop = document.createElement('span');
        drop.className = 'emoji-drop';
        drop.textContent = RAIN_EMOJIS[Math.floor(Math.random() * RAIN_EMOJIS.length)];

        const leftPos = Math.random() * 96; // 0% to 96%
        const sizeRem = (1 + Math.random() * 1.5).toFixed(2); // 1 to 2.5rem
        const durationSec = (8 + Math.random() * 12).toFixed(1); // 8s to 20s
        const delaySec = isBonus ? '0.0s' : (Math.random() * 8).toFixed(1) + 's';
        const driftPx = (Math.random() * 60 - 30).toFixed(0); // slight horizontal parallax drift

        drop.style.left = leftPos + '%';
        drop.style.fontSize = sizeRem + 'rem';
        drop.style.animationDuration = durationSec + 's';
        drop.style.animationDelay = delaySec;
        drop.style.setProperty('--drift-x', driftPx + 'px');

        drop.addEventListener('animationiteration', () => {
            drop.textContent = RAIN_EMOJIS[Math.floor(Math.random() * RAIN_EMOJIS.length)];
            drop.style.left = (Math.random() * 96) + '%';
        });

        container.appendChild(drop);
    }

    function initEmojiRain(count) {
        const container = getEmojiRainContainer();
        const dropsToCreate = count || 18;
        for (let i = 0; i < dropsToCreate; i++) {
            createSingleEmojiDrop(container, false);
        }
    }

    function boostEmojiRain(extraCount) {
        const container = getEmojiRainContainer();
        for (let i = 0; i < extraCount; i++) {
            createSingleEmojiDrop(container, true);
        }
    }

    /* ──────────────────────────────────────────────
       3. Cookie Banner
       ────────────────────────────────────────────── */
    function initCookieBanner() {
        try {
            if (localStorage.getItem('aura-cookies-dismissed') === 'true') {
                const existing = document.querySelector('.cookie-banner');
                if (existing) existing.classList.add('hidden');
                return;
            }
        } catch (e) {}

        let banner = document.querySelector('.cookie-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.className = 'cookie-banner';
            banner.innerHTML = `
                <div class="cookie-text">
                    🍪 <strong>BRAINROT COOKIES:</strong> We use cookies to measure your aura,
                    track your mewing posture, and calculate your Ohio tax bracket.
                </div>
                <div class="cookie-buttons">
                    <button type="button" class="btn btn-small btn-primary cookie-btn" data-action="all">Accept All (Sigma)</button>
                    <button type="button" class="btn btn-small btn-secondary cookie-btn" data-action="tax">Pay Fanum Tax</button>
                    <button type="button" class="btn btn-small btn-warning cookie-btn" data-action="reject">Reject &amp; Lose 50 Aura</button>
                </div>
            `;
            document.body.appendChild(banner);
        }

        // Show after 2 seconds
        setTimeout(() => {
            if (banner) banner.classList.remove('hidden');
        }, 2000);

        banner.addEventListener('click', function (e) {
            const btn = e.target.closest('button');
            if (!btn) return;

            const action = btn.dataset.action || 'default';
            const funnyLogs = {
                all: '🍪 Cookies accepted: Your soul, browsing history, and mewing records are now stored on the Ohio server.',
                tax: '🍪 Fanum tax collected: 20% of your current cookie bandwidth was surrendered to Kai Cenat.',
                reject: '🍪 Cookies rejected: The Bouncer noted your refusal in your permanent aura file.',
                default: '🍪 Cookie banner dismissed with peak sigma energy.'
            };
            console.log(funnyLogs[action] || funnyLogs.default);

            banner.classList.add('hidden');
            try {
                localStorage.setItem('aura-cookies-dismissed', 'true');
            } catch (err) {}
        });
    }

    /* ──────────────────────────────────────────────
       4. Fake System Notifications
       ────────────────────────────────────────────── */
    const DEFAULT_NOTIFICATIONS = [
        "Your aura is being audited by the Sigma Council",
        "3 sigmas are viewing your profile right now",
        "Your mewing technique has been flagged for review",
        "Ohio Department of Aura sent you a notice",
        "BREAKING: Your rizz license is about to expire",
        "A skibidi toilet just rated your aura 2/10",
        "The Fanum Tax collector is approaching your session",
        "Your password was spotted mewing in public",
        "ALERT: Unauthorized sigma detected in your vicinity",
        "Your aura portfolio lost 12% overnight",
        "The Council of Elders requests your meme credentials",
        "A wild NPC appeared in your login session",
        "Your digital footprint smells like Ohio",
        "Someone just screenshotted your aura rating",
        "Brainrot levels: CRITICALLY HIGH"
    ];

    function getNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.left = '20px';
            container.style.zIndex = '7000';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.gap = '10px';
            container.style.pointerEvents = 'none';
            document.body.appendChild(container);
        }
        return container;
    }

    function showNotification(text) {
        const container = getNotificationContainer();
        const popup = document.createElement('div');
        popup.className = 'notification-popup';
        popup.style.position = 'relative';
        popup.style.top = '0';
        popup.style.left = '0';
        popup.style.pointerEvents = 'auto';
        popup.textContent = text;

        container.appendChild(popup);

        // Auto remove after 5s
        setTimeout(() => {
            popup.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            popup.style.opacity = '0';
            popup.style.transform = 'translateX(-30px)';
            setTimeout(() => {
                if (popup.parentNode) popup.parentNode.removeChild(popup);
            }, 400);
        }, 5000);
    }

    function initSystemNotifications() {
        const list = (window.SERVER_NOTIFICATIONS && window.SERVER_NOTIFICATIONS.length > 0)
            ? window.SERVER_NOTIFICATIONS
            : DEFAULT_NOTIFICATIONS;

        function scheduleNextNotification() {
            const delay = Math.floor(15000 + Math.random() * 15000); // 15 to 30 seconds
            setTimeout(() => {
                const randomMsg = list[Math.floor(Math.random() * list.length)];
                showNotification(randomMsg);
                scheduleNextNotification();
            }, delay);
        }

        // First notification after 10s
        setTimeout(() => {
            const randomMsg = list[Math.floor(Math.random() * list.length)];
            showNotification(randomMsg);
            scheduleNextNotification();
        }, 10000);
    }

    /* ──────────────────────────────────────────────
       5. Chaos Level Slider
       ────────────────────────────────────────────── */
    function initChaosControl() {
        let savedChaos = '3';
        try {
            savedChaos = localStorage.getItem('chaos-level') || '3';
        } catch (e) {}

        document.body.dataset.chaos = savedChaos;

        const slider = document.querySelector('.chaos-slider');
        if (slider) {
            slider.value = savedChaos;
            slider.addEventListener('input', function (e) {
                const val = e.target.value;
                document.body.dataset.chaos = val;
                try {
                    localStorage.setItem('chaos-level', val);
                } catch (err) {}
            });
        }
    }

    /* ──────────────────────────────────────────────
       6. Mute Toggle Button
       ────────────────────────────────────────────── */
    function initMuteButton() {
        let muteBtn = document.querySelector('.mute-toggle');
        if (!muteBtn) {
            muteBtn = document.createElement('button');
            muteBtn.type = 'button';
            muteBtn.className = 'mute-toggle no-tung';
            muteBtn.title = 'Toggle Sound';
            document.body.appendChild(muteBtn);
        }

        function updateMuteIcon() {
            const muted = window.AuraSound ? window.AuraSound.isMuted() : false;
            muteBtn.textContent = muted ? '🔇' : '🔊';
            muteBtn.setAttribute('aria-label', muted ? 'Unmute audio' : 'Mute audio');
        }

        updateMuteIcon();

        muteBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            if (window.AuraSound && typeof window.AuraSound.toggleMute === 'function') {
                window.AuraSound.toggleMute();
            }
            updateMuteIcon();
        });

        window.addEventListener('aura-mute-changed', updateMuteIcon);
    }

    /* ──────────────────────────────────────────────
       7. Konami Code Easter Egg
       ────────────────────────────────────────────── */
    function initKonamiCode() {
        const targetSequence = [
            'ArrowUp', 'ArrowUp',
            'ArrowDown', 'ArrowDown',
            'ArrowLeft', 'ArrowRight',
            'ArrowLeft', 'ArrowRight',
            'b', 'a'
        ];
        let currentPosition = 0;

        window.addEventListener('keydown', function (e) {
            const key = e.key;
            const expected = targetSequence[currentPosition];

            const matches = (key === expected) || (key.toLowerCase() === expected.toLowerCase());

            if (matches) {
                currentPosition++;
                if (currentPosition === targetSequence.length) {
                    currentPosition = 0;
                    activateUltraBrainrotMode();
                }
            } else {
                // If it was the first key again, reset to 1, otherwise 0
                const matchesFirst = (key === targetSequence[0]);
                currentPosition = matchesFirst ? 1 : 0;
            }
        });
    }

    function activateUltraBrainrotMode() {
        const isUltra = document.body.classList.toggle('ultra-brainrot');

        if (window.AuraSound && typeof window.AuraSound.setPitchShift === 'function') {
            window.AuraSound.setPitchShift(isUltra);
        }

        if (isUltra) {
            boostEmojiRain(20);
            showAchievement(
                '🔥 ULTRA BRAINROT MODE ACTIVATED 🔥',
                'Reality inverted. 2x pitch shift. Sigma frequencies maximum. fr fr.'
            );
        } else {
            showAchievement(
                'NPC RESTORATION',
                'Standard brainrot parameters restored. You are now merely mid.'
            );
        }
    }

    /* ──────────────────────────────────────────────
       8. Fake Loading Bars
       ────────────────────────────────────────────── */
    function initFakeLoadingBars() {
        const loadingContainers = document.querySelectorAll('.fake-loading');
        loadingContainers.forEach(container => {
            let bar = container.querySelector('.fake-loading-bar');
            if (!bar) {
                bar = document.createElement('div');
                bar.className = 'fake-loading-bar';
                container.appendChild(bar);
            }
            // Trigger animation
            bar.style.animation = 'none';
            // Force reflow
            void bar.offsetHeight;
            bar.style.animation = '';
        });
    }

    /* ──────────────────────────────────────────────
       9. Modal Helper & Triple Confirmation Logout
       ────────────────────────────────────────────── */
    function createModal(title, text, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay active';
        overlay.innerHTML = `
            <div class="modal-content">
                <h3 class="modal-title">${escapeHTML(title)}</h3>
                <p class="modal-text">${escapeHTML(text)}</p>
                <div class="modal-buttons">
                    <button type="button" class="btn btn-danger btn-modal-confirm">CONFIRM</button>
                    <button type="button" class="btn btn-secondary btn-modal-cancel">CANCEL</button>
                </div>
            </div>
        `;

        function closeModal() {
            overlay.classList.remove('active');
            setTimeout(() => {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            }, 300);
        }

        const confirmBtn = overlay.querySelector('.btn-modal-confirm');
        const cancelBtn = overlay.querySelector('.btn-modal-cancel');

        confirmBtn.addEventListener('click', () => {
            closeModal();
            if (typeof onConfirm === 'function') onConfirm();
        });

        cancelBtn.addEventListener('click', () => {
            closeModal();
            if (typeof onCancel === 'function') onCancel();
        });

        document.body.appendChild(overlay);
        return overlay;
    }

    function initTripleConfirmLogout() {
        document.addEventListener('submit', function (e) {
            const form = e.target;
            const action = form.getAttribute('action') || '';
            const isLogout = action.includes('logout') || form.id === 'logout-form' || form.classList.contains('logout-form');

            if (!isLogout) return;

            // Prevent direct submit
            e.preventDefault();

            // Step 1
            createModal(
                'LOGOUT CONFIRMATION (1/3)',
                'Are you sure you want to logout? The Bouncer might dock 100 aura for abandoning the grind.',
                function () {
                    // Step 2
                    createModal(
                        'LOGOUT CONFIRMATION (2/3)',
                        'Are you REALLY sure? Once you leave, your mewing streak will reset to Ohio.',
                        function () {
                            // Step 3
                            createModal(
                                'FINAL LOGOUT CONFIRMATION (3/3)',
                                'Are you sure you\'re sure you\'re REALLY sure? 🤨 The Council will judge this.',
                                function () {
                                    // Confirmed all 3 times, submit form programmatically
                                    form.submit();
                                },
                                function () {
                                    showAchievement('SIGMA COMMITMENT', 'Logout canceled. You stay on the grind! 📈');
                                }
                            );
                        },
                        function () {
                            showAchievement('CLOSE CALL', 'Logout canceled at checkpoint 2.');
                        }
                    );
                },
                function () {
                    showAchievement('AURA PRESERVED', 'Logout aborted. Stay locked in.');
                }
            );
        });
    }

    /* ──────────────────────────────────────────────
       10. Achievement Toast
       ────────────────────────────────────────────── */
    function showAchievement(title, description) {
        if (window.AuraSound && typeof window.AuraSound.playSuccess === 'function') {
            window.AuraSound.playSuccess();
        }

        const toast = document.createElement('div');
        toast.className = 'achievement-toast';
        toast.innerHTML = `
            <h4>🏆 ${escapeHTML(title)}</h4>
            <p>${escapeHTML(description)}</p>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 400);
        }, 4000);
    }

    /* ──────────────────────────────────────────────
       11. Password Expiry Countdown (Dashboard)
       ────────────────────────────────────────────── */
    function initPasswordExpiryTimer() {
        const timerContainer = document.getElementById('expiry-timer') || document.querySelector('.expiry-timer');
        if (!timerContainer) return;

        let display = timerContainer.querySelector('.expiry-time') || timerContainer;
        let seconds = 59;

        function updateDisplay() {
            display.textContent = (seconds < 10 ? '0' : '') + seconds + 's';
        }

        updateDisplay();

        const interval = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                // Show modal: JK LOL 😂
                createModal(
                    'SECURITY NOTICE: EXPIRED',
                    'JK LOL 😂 Did you really think we have passwords that expire? Resetting back to 59s. Your aura is safe for now.',
                    function () {
                        // modal closed
                    },
                    function () {
                        // modal closed
                    }
                );
                seconds = 59;
            }
            updateDisplay();
        }, 1000);
    }

    /* ──────────────────────────────────────────────
       DOM Content Loaded Initialization
       ────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', function () {
        initSplashScreen();
        initEmojiRain(18);
        initCookieBanner();
        initSystemNotifications();
        initChaosControl();
        initMuteButton();
        initKonamiCode();
        initFakeLoadingBars();
        initTripleConfirmLogout();
        initPasswordExpiryTimer();
        initEmojiPickers();
        initPasswordToggles();
    });

    /* ──────────────────────────────────────────────
       Emoji Picker & Password Visibility Toggles
       ────────────────────────────────────────────── */
    function initEmojiPickers() {
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.emoji-btn');
            if (!btn) return;
            e.preventDefault();
            e.stopPropagation();

            const emoji = btn.dataset.emoji || btn.textContent.trim();
            const container = btn.closest('.emoji-picker-bar') || btn.closest('.emoji-picker-container');
            const targetId = (container && container.dataset.target) || btn.dataset.target;
            let targetInput = targetId ? document.getElementById(targetId) : null;
            if (!targetInput) {
                const formGroup = btn.closest('.form-group');
                if (formGroup) {
                    targetInput = formGroup.querySelector('input, textarea');
                }
            }

            if (targetInput) {
                targetInput.focus();
                const start = (typeof targetInput.selectionStart === 'number') ? targetInput.selectionStart : targetInput.value.length;
                const end = (typeof targetInput.selectionEnd === 'number') ? targetInput.selectionEnd : targetInput.value.length;
                const val = targetInput.value;
                targetInput.value = val.substring(0, start) + emoji + val.substring(end);
                const newPos = start + emoji.length;
                try {
                    targetInput.setSelectionRange(newPos, newPos);
                } catch (err) {}

                targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                targetInput.dispatchEvent(new Event('change', { bubbles: true }));

                // Animation feedback
                btn.style.transform = 'scale(1.4)';
                setTimeout(() => { btn.style.transform = ''; }, 150);
            }
        });
    }

    function initPasswordToggles() {
        document.addEventListener('click', function (e) {
            const toggle = e.target.closest('.password-toggle-btn');
            if (!toggle) return;
            e.preventDefault();
            e.stopPropagation();

            const targetId = toggle.dataset.target;
            const input = targetId ? document.getElementById(targetId) : (toggle.closest('.form-group') ? toggle.closest('.form-group').querySelector('input') : null);
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                toggle.textContent = isPassword ? '🙈 Hide' : '👁️ Show';
                input.focus();
            }
        });
    }

    // Global AuraUI API
    window.AuraUI = {
        showAchievement: showAchievement,
        createModal: createModal,
        showNotification: showNotification
    };
})();
