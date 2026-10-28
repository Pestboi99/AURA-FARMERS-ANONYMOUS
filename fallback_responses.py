"""Offline Fallback Response Bank for AURA FARMERS ANONYMOUS.

Provides pre-written satirical bouncer verdicts, fake analysis progress steps,
and compliment evaluations for password reset flows when the Gemini API is
unreachable or offline.
"""

from __future__ import annotations

import random
from typing import Any

__all__ = [
    "FALLBACK_RESPONSES",
    "ANALYSIS_STEPS",
    "COMPLIMENT_RESPONSES",
    "get_random_response",
    "get_random_analysis_steps",
    "get_random_compliment_response",
]

# ---------------------------------------------------------------------------
# Fallback Bouncer Responses (36 items: ~61% fail, ~39% pass)
# ---------------------------------------------------------------------------
FALLBACK_RESPONSES: list[dict[str, Any]] = [
    # --- FAILS (22) ---
    {
        "verdict": "fail",
        "message": "Per Article 7 of the Rizz Accords, your meme knowledge is below the legal limit. Case dismissed.",
        "aura_change": -15,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Bro walked in with negative infinite aura. The floorboards are actively groaning under the sheer weight of your cringe. Scram.",
        "aura_change": -35,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Your vibe is giving straight Ohio gas station bathroom at 3 AM. Absolutely cooked. Denied without parole.",
        "aura_change": -25,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "I consulted my enchanted crystal fidget spinner and it exploded. You are banned from the club and from YouTube Shorts.",
        "aura_change": -40,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "Zero rizz detected on all radar frequencies. You couldn't even pull a push-door. Go home and practice mewing.",
        "aura_change": -20,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Bro forgot to pay the Fanum tax on his entry request. The IRS of aura has seized your credentials.",
        "aura_change": -30,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Bro is not him. Bro is not even an honorable mention of him. Bro is an NPC wandering outside the playable map.",
        "aura_change": -22,
        "mood": "chill",
    },
    {
        "verdict": "fail",
        "message": "I fell asleep during your login attempt because your energy is a lullaby of pure mid. Come back when awake.",
        "aura_change": -10,
        "mood": "sleepy",
    },
    {
        "verdict": "fail",
        "message": "Skibidi toilet inspection failed. Residue levels are toxic and you broke sigma quarantine. Evacuate immediately.",
        "aura_change": -45,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "My jawline sensor measured your posture at a 45-degree gamer hunch. You just got mogged by the velvet rope.",
        "aura_change": -18,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Baby Gronk rizzing up Livvy Dunne had more dignity than this login attempt. Major L fr no cap.",
        "aura_change": -16,
        "mood": "chill",
    },
    {
        "verdict": "fail",
        "message": "You are cooked fr no cap. Even an industrial air fryer couldn't crisp up this tragic lack of swagger. Denied.",
        "aura_change": -28,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "Whatever you just tried to do, un-do it immediately. My third eye is crying tears of second-hand embarrassment.",
        "aura_change": -32,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "Bro thinks he's the main character in an anime but he's literally extra #4 in the background crowd. Denied.",
        "aura_change": -15,
        "mood": "chill",
    },
    {
        "verdict": "fail",
        "message": "Hold on... *snores loudly* ...huh? Oh you're still here? No, go away, my memory foam pillow has more aura than you.",
        "aura_change": -12,
        "mood": "sleepy",
    },
    {
        "verdict": "fail",
        "message": "Looksmaxxing license revoked. You broke rule #1: never let the bouncer catch you lacking without an active mewing streak.",
        "aura_change": -24,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "Emergency broadcast: Level 5 beta alert triggered at the main gate. Please retreat to your nearest Subway Surfers clip.",
        "aura_change": -30,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "Bro used speech-to-text with zero charisma. The algorithm shuddered and spat out a 403 Forbidden.",
        "aura_change": -14,
        "mood": "grumpy",
    },
    {
        "verdict": "fail",
        "message": "I checked your Spotify wrapped and it's 10 hours of loopable sad boy phonk. Not in my club.",
        "aura_change": -20,
        "mood": "chill",
    },
    {
        "verdict": "fail",
        "message": "Too tired to even roast you properly. Just take the L and sleep it off. It's way past your bedtime.",
        "aura_change": -10,
        "mood": "sleepy",
    },
    {
        "verdict": "fail",
        "message": "Negative aura quarantine activated! You just vaporized 50 aura points into the stratosphere. Truly tragic.",
        "aura_change": -50,
        "mood": "unhinged",
    },
    {
        "verdict": "fail",
        "message": "The sigma council voted 12-0 against your admission. Even the court jester voted to reject you.",
        "aura_change": -22,
        "mood": "grumpy",
    },
    # --- PASSES (14) ---
    {
        "verdict": "pass",
        "message": "I was gonna fail you but my shift ends in 5 minutes so sure whatever. Don't make it weird.",
        "aura_change": 10,
        "mood": "sleepy",
    },
    {
        "verdict": "pass",
        "message": "The unspoken rizz is frankly terrifying. I won't even check your ID, please don't mog my family.",
        "aura_change": 45,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "W mans detected. Walk right in king, you dropped this crown and also several bundles of unadulterated aura.",
        "aura_change": 35,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "HE'S HIM! HE IS LITERALLY THE PROPHECIED SIGMA FROM THE SACRED TIKTOK COMPILATIONS! ENTER AT ONCE!",
        "aura_change": 50,
        "mood": "unhinged",
    },
    {
        "verdict": "pass",
        "message": "Valid vibe check. No Ohio energy, pure skibidi grace, and jawline sharp enough to cut cheese. You're clear.",
        "aura_change": 25,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "Bro passed the Fanum tax inspection with flying colors. Premium aura verified by the national registry.",
        "aura_change": 30,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "Yawn... yeah fine, you look chill enough. Don't touch the sound system or wake me up.",
        "aura_change": 5,
        "mood": "sleepy",
    },
    {
        "verdict": "pass",
        "message": "I am legally obligated by the Rizz Convention to admit anyone with jawline definition this sharp. Go ahead.",
        "aura_change": 20,
        "mood": "grumpy",
    },
    {
        "verdict": "pass",
        "message": "Absolute cinematic masterpiece of an entrance. You mogged everyone in line without saying a single syllable. In you go.",
        "aura_change": 40,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "My aura detector just shattered into 40,000 glittering pieces. That is either god-tier rizz or nuclear radiation. Welcome!",
        "aura_change": 45,
        "mood": "unhinged",
    },
    {
        "verdict": "pass",
        "message": "Pass granted on technicality: your confidence is so unhinged I am afraid of what happens if I say no.",
        "aura_change": 15,
        "mood": "unhinged",
    },
    {
        "verdict": "pass",
        "message": "Look, I hate everyone equally, but your credentials are unfortunately immaculate. Wipe your feet on the beta mat.",
        "aura_change": 15,
        "mood": "grumpy",
    },
    {
        "verdict": "pass",
        "message": "No cap, that was clean. The sigma grindset pays off yet again. Head inside, VIP section awaits.",
        "aura_change": 30,
        "mood": "chill",
    },
    {
        "verdict": "pass",
        "message": "I was half-asleep but your aura was so bright it woke me up like a flashlight. Get in.",
        "aura_change": 12,
        "mood": "sleepy",
    },
]


# ---------------------------------------------------------------------------
# Ridiculous Fake Analysis Steps (28 items)
# ---------------------------------------------------------------------------
ANALYSIS_STEPS: list[str] = [
    "Consulting the Council of Sigmas...",
    "Measuring your aura radius...",
    "Buffering rizz...",
    "Downloading Ohio.exe...",
    "Checking your sigma license...",
    "Scanning for skibidi residue...",
    "Calculating jawline sharpness angle via mewing lidar...",
    "Checking Fanum tax compliance records...",
    "Translating vibe to Kai Cenat dialect...",
    "Analyzing posture for involuntary beta slouching...",
    "Cross-referencing looksmaxxing history with Subway Surfers clips...",
    "Inspecting bloodstream for Grimace Shake particulates...",
    "Ping testing the rizz servers in Bucharest...",
    "Decompiling your subconscious TikTok algorithm...",
    "Verifying if you are cooked, burnt, or deep-fried...",
    "Detecting imposter aura frequencies (amogus check)...",
    "Calibrating bouncer eyeball gyroscopes...",
    "Synchronizing twin rotators with Baby Gronk...",
    "Extracting spiritual rizz particles...",
    "Querying the Department of Unspoken Rizz...",
    "Evaluating vocal fry decibel levels...",
    "Triangulating distance from closest Ohio border...",
    "Auditing your emotional investment in NPC live streams...",
    "Running heuristic anti-cringe kernel scan...",
    "Calculating canthal tilt and hunter eye coefficient...",
    "Checking if you paid your edge streak renewal fee...",
    "Consulting ancient Romanian kickboxing texts...",
    "Measuring spiritual weight of your air fryer...",
]


# ---------------------------------------------------------------------------
# Compliment Responses for Password Reset (18 items: ~61% accepted, ~39% rejected)
# ---------------------------------------------------------------------------
COMPLIMENT_RESPONSES: list[dict[str, Any]] = [
    # --- REJECTED (7) ---
    {
        "accepted": False,
        "message": "That compliment has less originality than a sigma grindset TikTok. Try harder.",
    },
    {
        "accepted": False,
        "message": "Flattery level: beta. You didn't even mention my jawline or my aura. Denied.",
    },
    {
        "accepted": False,
        "message": "Bro tried to fanum tax my validation. I am spiritually unmoved. Access denied.",
    },
    {
        "accepted": False,
        "message": "That felt like an automated email from LinkedIn. Zero rizz detected.",
    },
    {
        "accepted": False,
        "message": "Nice try, but I saw that exact pickup line in an Ohio meme compilation from 2023. Rejected.",
    },
    {
        "accepted": False,
        "message": "Your compliment gave me negative 500 aura just reading it. Try again when you've looksmaxxed.",
    },
    {
        "accepted": False,
        "message": "Cap detected on line 1. I know I look exhausted, don't gas me up with cheap lies.",
    },
    # --- ACCEPTED (11) ---
    {
        "accepted": True,
        "message": "Okay wait... that actually mogged my insecurities. Password reset approved, don't make it weird.",
    },
    {
        "accepted": True,
        "message": "W compliment fr no cap. My ego just gained +200 aura. Here is your reset link.",
    },
    {
        "accepted": True,
        "message": "Unspoken rizz acknowledged. The Council of Sigmas grants you clemency this once.",
    },
    {
        "accepted": True,
        "message": "Damn, you really hit me with the emotional critical strike. You may proceed, king.",
    },
    {
        "accepted": True,
        "message": "Valid flattery detected. My cold bouncer heart has softened by 4.2%. Resetting.",
    },
    {
        "accepted": True,
        "message": "Genuinely made me stop mewing to smile. You're in, absolute chad.",
    },
    {
        "accepted": True,
        "message": "That was so smooth it bypassed my firewall. Password reset granted.",
    },
    {
        "accepted": True,
        "message": "Bro cooked with that one. Gordon Ramsay of compliments. Access granted.",
    },
    {
        "accepted": True,
        "message": "I am blushing through my sunglasses rn fr. Reset approved.",
    },
    {
        "accepted": True,
        "message": "High aura compliment received. Reset sequence initialized. Stay majestic.",
    },
    {
        "accepted": True,
        "message": "Respectable rizz. I'll allow it because nobody has complimented my bouncer posture in years.",
    },
]


# ---------------------------------------------------------------------------
# Helper Selector Functions
# ---------------------------------------------------------------------------
def get_random_response() -> dict[str, Any]:
    """Return a random fallback bouncer verdict response."""
    return random.choice(FALLBACK_RESPONSES).copy()


def get_random_analysis_steps(count: int = 5) -> list[str]:
    """Return `count` random unique analysis step strings."""
    sample_size = min(max(1, count), len(ANALYSIS_STEPS))
    return random.sample(ANALYSIS_STEPS, sample_size)


def get_random_compliment_response() -> dict[str, Any]:
    """Return a random compliment response for password resets."""
    return random.choice(COMPLIMENT_RESPONSES).copy()
