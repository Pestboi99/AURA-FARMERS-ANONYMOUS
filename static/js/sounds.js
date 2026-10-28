/**
 * AURA FARMERS ANONYMOUS — sounds.js
 * Global Audio System & Sound Synthesizer
 * "Log in. Lose your dignity."
 */

(function () {
    'use strict';

    let audioCtx = null;
    let tungAudio = null;
    let pitchShiftEnabled = false;
    let isUnlocked = false;

    /**
     * Get or lazily create AudioContext with autoplay policy handling.
     */
    function getAudioContext() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume().catch(() => {});
        }
        return audioCtx;
    }

    /**
     * Unlock audio on first user gesture.
     */
    function unlock() {
        const ctx = getAudioContext();
        if (ctx && ctx.state === 'suspended') {
            ctx.resume().catch(() => {});
        }
        isUnlocked = true;
    }

    /**
     * Check if audio is currently muted.
     */
    function isMuted() {
        try {
            return localStorage.getItem('aura-muted') === 'true';
        } catch (e) {
            return false;
        }
    }

    /**
     * Toggle muted state and persist to localStorage.
     */
    function toggleMute() {
        const newState = !isMuted();
        try {
            localStorage.setItem('aura-muted', newState ? 'true' : 'false');
        } catch (e) {
            console.warn('LocalStorage unavailable for mute toggle', e);
        }
        window.dispatchEvent(new CustomEvent('aura-mute-changed', { detail: { muted: newState } }));
        return newState;
    }

    /**
     * Set pitch shift (2x frequency) for Ultra Brainrot Mode.
     */
    function setPitchShift(enabled) {
        pitchShiftEnabled = Boolean(enabled);
    }

    /**
     * Create distortion curve for the Vine Boom fail sound.
     */
    function makeDistortionCurve(amount) {
        const k = typeof amount === 'number' ? amount : 50;
        const n_samples = 44100;
        const curve = new Float32Array(n_samples);
        const deg = Math.PI / 180;
        for (let i = 0; i < n_samples; ++i) {
            const x = (i * 2) / n_samples - 1;
            curve[i] = ((3 + k) * x * 20 * deg) / (Math.PI + k * Math.abs(x));
        }
        return curve;
    }

    /**
     * Synthesize wooden thump with WebAudio:
     * ~80Hz oscillator with quick decay (attack 0ms, decay 100ms) + noise burst.
     */
    function synthesizeWoodenThump() {
        const ctx = getAudioContext();
        if (!ctx) return;

        const now = ctx.currentTime;
        const rateMultiplier = pitchShiftEnabled ? 2.0 : 1.0;

        // 1. Low body oscillator thump
        const osc = ctx.createOscillator();
        const oscGain = ctx.createGain();

        const baseFreq = 80 * rateMultiplier;
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(baseFreq, now);
        osc.frequency.exponentialRampToValueAtTime(Math.max(20, baseFreq * 0.4), now + 0.1);

        oscGain.gain.setValueAtTime(0.8, now);
        oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

        osc.connect(oscGain);
        oscGain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + 0.12);

        // 2. Wooden click / noise burst
        const bufferSize = Math.floor(ctx.sampleRate * 0.035); // 35ms burst
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.3));
        }

        const whiteNoise = ctx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;

        const noiseFilter = ctx.createBiquadFilter();
        noiseFilter.type = 'bandpass';
        noiseFilter.frequency.setValueAtTime(650 * rateMultiplier, now);
        noiseFilter.Q.setValueAtTime(1.5, now);

        const noiseGain = ctx.createGain();
        noiseGain.gain.setValueAtTime(0.7, now);
        noiseGain.gain.exponentialRampToValueAtTime(0.01, now + 0.035);

        whiteNoise.connect(noiseFilter);
        noiseFilter.connect(noiseGain);
        noiseGain.connect(ctx.destination);

        whiteNoise.start(now);
        whiteNoise.stop(now + 0.04);
    }

    /**
     * Speech fallback for 'tung tung tung sahur' in a deep satirical voice.
     */
    function speakTungFallback() {
        if (!('speechSynthesis' in window)) return;
        try {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance('tung tung tung sahur');
            utterance.pitch = pitchShiftEnabled ? 0.7 : 0.3;
            utterance.rate = pitchShiftEnabled ? 1.5 : 0.8;
            utterance.volume = 1.0;

            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {
                const deepVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Male') || v.name.includes('David') || v.name.includes('Mark')));
                if (deepVoice) utterance.voice = deepVoice;
            }
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            // Silently swallow speech errors
        }
    }

    /**
     * Play TUNG TUNG TUNG SAHUR:
     * a) Try static/audio/tung.mp3
     * b) If failed/missing: SpeechSynthesis API in deep voice
     * c) PLUS synthesize wooden 'tung' thump with WebAudio
     */
    function playTung() {
        if (isMuted()) return;
        unlock();

        if (!tungAudio) {
            tungAudio = new Audio('/static/audio/tung.mp3');
            tungAudio.preload = 'auto';
        }

        tungAudio.playbackRate = pitchShiftEnabled ? 2.0 : 1.0;
        tungAudio.currentTime = 0;

        const playPromise = tungAudio.play();
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    // Audio element played successfully
                })
                .catch(() => {
                    // Audio failed/404: trigger speech synthesis + wooden WebAudio thump
                    speakTungFallback();
                    synthesizeWoodenThump();
                });
        } else {
            // Older browser fallback
            synthesizeWoodenThump();
        }
    }

    /**
     * FAIL SOUND (Vine boom style):
     * Low frequency oscillator (60-80Hz) with quick attack, medium decay,
     * waveshaper distortion, ~500ms duration.
     */
    function playFail() {
        if (isMuted()) return;
        unlock();

        const ctx = getAudioContext();
        if (!ctx) return;

        const now = ctx.currentTime;
        const rateMultiplier = pitchShiftEnabled ? 2.0 : 1.0;
        const duration = 0.5;

        const osc = ctx.createOscillator();
        const oscGain = ctx.createGain();
        const distortion = ctx.createWaveShaper();
        const lowpass = ctx.createBiquadFilter();

        // 70Hz initial dropping to 32Hz
        const startFreq = 75 * rateMultiplier;
        const endFreq = 30 * rateMultiplier;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(startFreq, now);
        osc.frequency.exponentialRampToValueAtTime(endFreq, now + duration);

        distortion.curve = makeDistortionCurve(45);
        distortion.oversample = '4x';

        lowpass.type = 'lowpass';
        lowpass.frequency.setValueAtTime(260 * rateMultiplier, now);
        lowpass.frequency.exponentialRampToValueAtTime(60 * rateMultiplier, now + duration);

        // Quick attack 5ms, exponential decay over 500ms
        oscGain.gain.setValueAtTime(0.001, now);
        oscGain.gain.linearRampToValueAtTime(1.0, now + 0.008);
        oscGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

        osc.connect(distortion);
        distortion.connect(lowpass);
        lowpass.connect(oscGain);
        oscGain.connect(ctx.destination);

        osc.start(now);
        osc.stop(now + duration + 0.05);
    }

    /**
     * SUCCESS SOUND:
     * Cheerful jingle: 3 ascending tones (C5=523.25Hz, E5=659.25Hz, G5=783.99Hz)
     * Each tone ~150ms with sine wave, short gap between tones.
     */
    function playSuccess() {
        if (isMuted()) return;
        unlock();

        const ctx = getAudioContext();
        if (!ctx) return;

        const rateMultiplier = pitchShiftEnabled ? 2.0 : 1.0;
        const tones = [
            523.25 * rateMultiplier, // C5
            659.25 * rateMultiplier, // E5
            783.99 * rateMultiplier  // G5
        ];

        const toneDuration = 0.14;
        const toneInterval = 0.15;
        const startTime = ctx.currentTime + 0.01;

        tones.forEach((freq, index) => {
            const toneStart = startTime + (index * toneInterval);
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, toneStart);

            // 5ms attack, 135ms decay
            gain.gain.setValueAtTime(0.001, toneStart);
            gain.gain.linearRampToValueAtTime(0.4, toneStart + 0.005);
            gain.gain.exponentialRampToValueAtTime(0.001, toneStart + toneDuration);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start(toneStart);
            osc.stop(toneStart + toneDuration + 0.02);
        });
    }

    /**
     * GLOBAL EVENT DELEGATION:
     * On document click, check if target matches:
     * 'button, a, input[type=submit], .clickable, [type=button]'
     * If so, playTung().
     */
    document.addEventListener('click', function (event) {
        unlock();
        const selector = 'button, a, input[type="submit"], input[type="button"], .clickable, [type="button"]';
        const target = event.target.closest(selector);
        if (target) {
            // If it's not explicitly marked to avoid tung sound
            if (!target.classList.contains('no-tung')) {
                playTung();
            }
        }
    }, true);

    // Initial unlock on any early interaction
    ['touchstart', 'keydown', 'pointerdown'].forEach(ev => {
        window.addEventListener(ev, function () {
            if (!isUnlocked) unlock();
        }, { once: true, passive: true });
    });

    // Expose global AuraSound API
    window.AuraSound = {
        playTung: playTung,
        playFail: playFail,
        playSuccess: playSuccess,
        toggleMute: toggleMute,
        isMuted: isMuted,
        setPitchShift: setPitchShift,
        unlock: unlock
    };
})();
