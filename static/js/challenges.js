/**
 * AURA FARMERS ANONYMOUS — challenges.js
 * Challenge-Specific UI Logic & Interactive Systems
 * "Log in. Lose your dignity."
 */

(function () {
    'use strict';

    let isTimerAutoSubmit = false;
    let isSubmitting = false;

    /* ──────────────────────────────────────────────
       1. Sigma Timer Challenge
       ────────────────────────────────────────────── */
    function initSigmaTimer() {
        const timerBar = document.querySelector('.timer-bar');
        const timerContainer = document.querySelector('.timer-bar-container') || (timerBar ? timerBar.parentElement : null);
        const timerText = document.querySelector('.timer-text');
        const form = document.querySelector('form.challenge-form') || document.querySelector('form[action*="trial"]');
        const phraseEl = document.querySelector('.phrase-display') || document.querySelector('[data-expected-phrase]');
        const inputField = document.querySelector('input[name="answer"], textarea[name="answer"]');

        if (!timerBar && !timerText) return;

        // Read time limit from data attribute or fallback
        let timeLimit = 20;
        if (timerContainer && timerContainer.dataset.timeLimit) {
            timeLimit = parseFloat(timerContainer.dataset.timeLimit);
        } else if (timerBar && timerBar.dataset.timeLimit) {
            timeLimit = parseFloat(timerBar.dataset.timeLimit);
        } else if (form && form.dataset.timeLimit) {
            timeLimit = parseFloat(form.dataset.timeLimit);
        }

        const totalTimeMs = timeLimit * 1000;
        const startTime = Date.now();
        let timedOutField = document.querySelector('input[name="timed_out"]');
        if (!timedOutField && form) {
            timedOutField = document.createElement('input');
            timedOutField.type = 'hidden';
            timedOutField.name = 'timed_out';
            timedOutField.value = 'false';
            form.appendChild(timedOutField);
        }

        // Real-time accuracy badge
        const expectedPhrase = (phraseEl ? phraseEl.textContent.trim() : '') ||
            (document.querySelector('input[name="expected_phrase"]') ? document.querySelector('input[name="expected_phrase"]').value : '');

        let accuracyBadge = document.querySelector('.typing-accuracy');
        if (!accuracyBadge && inputField) {
            accuracyBadge = document.createElement('div');
            accuracyBadge.className = 'typing-accuracy';
            accuracyBadge.style.fontFamily = 'var(--font-heading, monospace)';
            accuracyBadge.style.fontSize = '1.1rem';
            accuracyBadge.style.marginTop = '0.5rem';
            accuracyBadge.style.textAlign = 'center';
            accuracyBadge.style.color = 'var(--electric-cyan, #00f0ff)';
            accuracyBadge.textContent = 'Typing Accuracy: 0%';
            inputField.parentElement.appendChild(accuracyBadge);
        }

        if (inputField && expectedPhrase) {
            inputField.addEventListener('input', function () {
                const typed = inputField.value;
                let matches = 0;
                const minLen = Math.min(typed.length, expectedPhrase.length);
                for (let i = 0; i < minLen; i++) {
                    if (typed[i] === expectedPhrase[i]) {
                        matches++;
                    }
                }
                const pct = expectedPhrase.length > 0 ? Math.round((matches / expectedPhrase.length) * 100) : 0;
                if (accuracyBadge) {
                    if (pct === 100 && typed === expectedPhrase) {
                        accuracyBadge.textContent = '🔥 100% SIGMA MATCH! SUBMIT NOW! 🔥';
                        accuracyBadge.style.color = 'var(--lime, #7dff00)';
                    } else {
                        accuracyBadge.textContent = `Typing Accuracy: ${pct}% (${matches}/${expectedPhrase.length})`;
                        accuracyBadge.style.color = pct > 75 ? 'var(--lime, #7dff00)' : pct > 40 ? 'var(--acid-yellow, #fff200)' : 'var(--electric-cyan, #00f0ff)';
                    }
                }
            });
        }

        // Countdown interval
        const timerInterval = setInterval(() => {
            const elapsed = Date.now() - startTime;
            const remaining = Math.max(0, totalTimeMs - elapsed);
            const remainingSec = (remaining / 1000).toFixed(1);
            const percentage = (remaining / totalTimeMs) * 100;

            if (timerText) {
                timerText.textContent = `${remainingSec}s`;
            }

            if (timerBar) {
                timerBar.style.width = `${percentage}%`;

                // Color thresholds
                if (percentage > 50) {
                    timerBar.classList.remove('warning', 'danger');
                } else if (percentage >= 25 && percentage <= 50) {
                    timerBar.classList.add('warning');
                    timerBar.classList.remove('danger');
                } else {
                    timerBar.classList.remove('warning');
                    timerBar.classList.add('danger');
                }
            }

            if (remaining <= 0) {
                clearInterval(timerInterval);
                if (timerBar) timerBar.style.width = '0%';
                if (timerText) timerText.textContent = '0.0s — TIME EXPIRED!';

                if (timedOutField) timedOutField.value = 'true';
                isTimerAutoSubmit = true;

                if (window.AuraSound && typeof window.AuraSound.playFail === 'function') {
                    window.AuraSound.playFail();
                }

                if (form) {
                    // Auto-submit form without triggering analysis overlay delay
                    form.submit();
                }
            }
        }, 50);
    }

    /* ──────────────────────────────────────────────
       2. Slider of Doom Challenge
       ────────────────────────────────────────────── */
    function initSliderOfDoom() {
        const slider = document.querySelector('.doom-slider');
        if (!slider) return;

        const form = slider.closest('form') || document.querySelector('form[action*="trial"]');
        const display = document.querySelector('.slider-value');
        const targetContainer = document.querySelector('.slider-target') || document.querySelector('[data-target-value]');

        // Target value
        let target = 50;
        if (slider.dataset.target) {
            target = parseInt(slider.dataset.target, 10);
        } else if (targetContainer && targetContainer.dataset.targetValue) {
            target = parseInt(targetContainer.dataset.targetValue, 10);
        } else if (targetContainer && targetContainer.textContent.match(/\d+/)) {
            target = parseInt(targetContainer.textContent.match(/\d+/)[0], 10);
        }

        function updateSliderDisplay() {
            if (display) {
                display.textContent = slider.value;
                const diff = Math.abs(parseInt(slider.value, 10) - target);
                if (diff === 0) {
                    display.style.color = 'var(--lime, #7dff00)';
                } else if (diff <= 3) {
                    display.style.color = 'var(--acid-yellow, #fff200)';
                } else {
                    display.style.color = 'var(--electric-cyan, #00f0ff)';
                }
            }
        }

        slider.addEventListener('input', updateSliderDisplay);
        updateSliderDisplay();

        // 1. JITTER: every 500ms, randomly nudge slider value by ±1-3
        const jitterInterval = setInterval(() => {
            if (document.hidden) return;
            const currentVal = parseInt(slider.value, 10);
            const delta = (Math.random() < 0.5 ? -1 : 1) * Math.floor(1 + Math.random() * 3);
            const min = parseInt(slider.min || 0, 10);
            const max = parseInt(slider.max || 100, 10);

            const newVal = Math.min(max, Math.max(min, currentVal + delta));
            slider.value = newVal;
            updateSliderDisplay();
        }, 500);

        // 2. DRIFT: slider slowly drifts toward 50 over time
        const driftInterval = setInterval(() => {
            if (document.hidden) return;
            const currentVal = parseInt(slider.value, 10);
            if (currentVal > 50) {
                slider.value = currentVal - 1;
                updateSliderDisplay();
            } else if (currentVal < 50) {
                slider.value = currentVal + 1;
                updateSliderDisplay();
            }
        }, 1200);

        // On form submit, copy current slider value to hidden field
        if (form) {
            form.addEventListener('submit', function () {
                let hiddenInput = form.querySelector('input[name="slider_value"]');
                if (!hiddenInput) {
                    hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'slider_value';
                    form.appendChild(hiddenInput);
                }
                hiddenInput.value = slider.value;

                let targetInput = form.querySelector('input[name="target_value"]');
                if (!targetInput) {
                    targetInput = document.createElement('input');
                    targetInput.type = 'hidden';
                    targetInput.name = 'target_value';
                    form.appendChild(targetInput);
                }
                targetInput.value = target;
            });
        }
    }

    /* ──────────────────────────────────────────────
       3. Choice Cards
       ────────────────────────────────────────────── */
    function initChoiceCards() {
        const cards = document.querySelectorAll('.choice-card');
        if (cards.length === 0) return;

        const form = cards[0].closest('form') || document.querySelector('form[action*="trial"]');

        let hiddenAnswer = document.querySelector('input[name="answer"]');
        if (!hiddenAnswer && form) {
            hiddenAnswer = document.createElement('input');
            hiddenAnswer.type = 'hidden';
            hiddenAnswer.name = 'answer';
            form.appendChild(hiddenAnswer);
        }

        cards.forEach(card => {
            card.addEventListener('click', function () {
                cards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');

                const chosenText = card.textContent.trim();
                if (hiddenAnswer) {
                    hiddenAnswer.value = chosenText;
                }

                if (window.AuraSound && typeof window.AuraSound.playTung === 'function') {
                    window.AuraSound.playTung();
                }
            });
        });
    }

    /* ──────────────────────────────────────────────
       4. Analysis Overlay
       ────────────────────────────────────────────── */
    const DEFAULT_STEPS = [
        "Consulting the Council of Sigmas...",
        "Measuring your aura radius...",
        "Scanning for skibidi residue...",
        "Buffering rizz on quantum mainframe...",
        "Article 7 Compliance Verification complete."
    ];

    function initAnalysisOverlay() {
        const form = document.querySelector('form.challenge-form') || document.querySelector('form[action*="trial"]');
        const overlay = document.querySelector('.analysis-overlay');
        if (!form || !overlay) return;

        form.addEventListener('submit', function (e) {
            // If triggered by timer auto-submit, do not delay or intercept
            if (isTimerAutoSubmit) {
                return;
            }

            // Prevent double-submissions
            if (isSubmitting) {
                e.preventDefault();
                return;
            }

            e.preventDefault();
            isSubmitting = true;

            overlay.classList.add('active');

            // Find or setup step display container
            let stepsContainer = overlay.querySelector('.analysis-steps-container');
            if (!stepsContainer) {
                stepsContainer = document.createElement('div');
                stepsContainer.className = 'analysis-steps-container';
                stepsContainer.style.display = 'flex';
                stepsContainer.style.flexDirection = 'column';
                stepsContainer.style.alignItems = 'center';
                stepsContainer.style.gap = '0.5rem';
                overlay.appendChild(stepsContainer);
            }
            stepsContainer.innerHTML = '';

            // Read steps from template or fallback
            let stepsToDisplay = [];
            const existingStepElements = overlay.querySelectorAll('.analysis-step-item');
            if (existingStepElements.length > 0) {
                existingStepElements.forEach(el => stepsToDisplay.push(el.textContent.trim()));
            } else if (window.SERVER_ANALYSIS_STEPS && Array.isArray(window.SERVER_ANALYSIS_STEPS) && window.SERVER_ANALYSIS_STEPS.length > 0) {
                stepsToDisplay = window.SERVER_ANALYSIS_STEPS;
            } else {
                stepsToDisplay = DEFAULT_STEPS;
            }

            let currentStepIdx = 0;
            const stepDelayMs = 450; // 400-600ms delays

            function showNextStep() {
                if (currentStepIdx < stepsToDisplay.length) {
                    const stepText = stepsToDisplay[currentStepIdx];
                    const stepEl = document.createElement('div');
                    stepEl.className = 'analysis-step';
                    stepEl.textContent = `⚡ ${stepText}`;
                    stepsContainer.appendChild(stepEl);

                    if (window.AuraSound && typeof window.AuraSound.playTung === 'function') {
                        window.AuraSound.playTung();
                    }

                    currentStepIdx++;
                    setTimeout(showNextStep, stepDelayMs);
                } else {
                    // All steps shown! Wait 300ms and actually submit
                    setTimeout(() => {
                        form.submit();
                    }, 350);
                }
            }

            showNextStep();
        });
    }

    /* ──────────────────────────────────────────────
       5. Auto-Init on DOMContentLoaded
       ────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', function () {
        initSigmaTimer();
        initSliderOfDoom();
        initChoiceCards();
        initAnalysisOverlay();
    });
})();
