"""
translations.py — Fast Batch API Translation System
────────────────────────────────────────────────────
Uses deep-translator (Google Translate) with BATCH calls so the
entire interface is translated in 3-5 API calls instead of 50+.

Format-string placeholders like {round}, {feedback}, etc. are
temporarily replaced with safe tokens before translating and
restored afterwards, so they survive translation intact.

Translation results are cached in st.session_state so the API is
only called once per language per session.
"""

import re
import json
import hashlib
import os
from deep_translator import GoogleTranslator

# ── Disk cache ────────────────────────────────────────────────────────────────
_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".translation_cache.json")

def _load_cache() -> dict:
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_cache(cache: dict):
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Never crash the game because of cache write failure

def _cache_key(lang: str, texts: list[str]) -> str:
    """SHA-1 of (lang + joined source text) — changes if source text changes."""
    fingerprint = lang + "||" + "|||".join(texts)
    return hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]

# ── Language catalogue ──────────────────────────────────────────────────────
LANGUAGES = {
    "🇬🇧 English":          "en",
    "🇮🇩 Bahasa Indonesia": "id",
    "🇲🇾 Bahasa Melayu":    "ms",
    "🇨🇳 中文 (简体)":      "zh-CN",
    "🇯🇵 日本語":            "ja",
    "🇰🇷 한국어":            "ko",
    "🇸🇦 العربية":          "ar",
    "🇫🇷 Français":         "fr",
    "🇪🇸 Español":          "es",
    "🇩🇪 Deutsch":          "de",
    "🇮🇳 हिन्दी":           "hi",
}

# ── Placeholder protection ────────────────────────────────────────────────────
# Regex to match Python format-string tokens like {round} or {max_rounds}
_PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")

def _protect(text: str):
    """Replace {token} with XTKN0X, XTKN1X … and return (protected, map)."""
    tokens = _PLACEHOLDER_RE.findall(text)
    mapping = {}
    for i, tok in enumerate(tokens):
        marker = f"XTKN{i}X"
        mapping[marker] = tok
        text = text.replace(tok, marker, 1)
    return text, mapping


def _restore(text: str, map_tokens: dict[str, str]) -> str:
    """Restore placeholders to translated strings, handling CJK spacing and full-width."""
    # 1. Normalize full-width Latin/Numeric characters to half-width
    # (Fixes the issue where Japanese/Chinese translations return ＸＴＫＮ０Ｘ)
    normalized_text = ""
    for char in text:
        code = ord(char)
        # 0xFF01 to 0xFF5E are full-width ASCII characters
        if 0xFF01 <= code <= 0xFF5E:
            normalized_text += chr(code - 0xFEE0)
        else:
            normalized_text += char
    text = normalized_text

    # 2. Replace token with regex to ignore accidental spaces and case changes
    for token, original in map_tokens.items():
        # Turns "XTKN0X" into a flexible pattern like r"X\s*T\s*K\s*N\s*0\s*X"
        pattern = r'\s*'.join(list(token))
        text = re.sub(pattern, original, text, flags=re.IGNORECASE)

    return text


def _clean_markdown(text: str) -> str:
    """
    Translators often break markdown by adding spaces (e.g., `** Text **`)
    or converting backticks to local quotes (`「Text」`). This fixes them for Streamlit.
    """
    # Fix bold: ** Text ** -> **Text**
    text = re.sub(r'\*\*\s*(.*?)\s*\*\*', r'**\1**', text)
    # Fix italics: * Text * -> *Text* (negative lookbehind/ahead prevents matching **)
    text = re.sub(r'(?<!\*)\*\s*([^\*]+?)\s*\*(?!\*)', r'*\1*', text)
    # Fix backticks translated to various CJK brackets/quotes (Added 『 』 and 【 】)
    text = re.sub(r'[「“『【]\s*(.*?)\s*[」”』】]', r'``\1``', text)
    # Fix spaces inside double backticks: `` Text `` -> ``Text``
    text = re.sub(r'``\s*(.*?)\s*``', r'``\1``', text)
    return text


# ── Batch translation core ────────────────────────────────────────────────────
_MAX_BATCH = 4500   # Google Translate free endpoint hard-limit per request

def _batch_translate(texts: list[str], target: str) -> list[str]:
    """
    Translate a list of strings using as few API calls as possible.
    Falls back to the original text on any individual error.
    """
    if target == "en":
        return texts

    translator = GoogleTranslator(source="en", target=target)
    results = []
    current_batch: list[str] = []
    current_len = 0
    batches: list[list[str]] = []

    for t in texts:
        if current_len + len(t) + 2 > _MAX_BATCH and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_len = 0
        current_batch.append(t)
        current_len += len(t) + 2
    if current_batch:
        batches.append(current_batch)

    for batch in batches:
        try:
            translated = translator.translate_batch(batch)
            # translate_batch returns None for empty strings; fall back
            results.extend(
                t if t else batch[i]
                for i, t in enumerate(translated)
            )
        except Exception:
            results.extend(batch)   # graceful fall-back

    return results


def _translate_list(raw: list[str], target: str) -> list[str]:
    """
    Translate a list of strings with three-layer caching:
    1. Disk cache (.translation_cache.json) — survives restarts
    2. Placeholder protection — {tokens} won't be garbled
    3. Batch API call — one network request per language
    """
    if target == "en":
        return raw

    key = _cache_key(target, raw)
    cache = _load_cache()
    if key in cache:
        return [_clean_markdown(t) for t in cache[key]]   # ⚡ instant — already translated before

    # Protect format placeholders
    protected, maps = [], []
    for text in raw:
        p, m = _protect(text)
        protected.append(p)
        maps.append(m)

    translated = _batch_translate(protected, target)
    result = [_clean_markdown(_restore(t, m)) for t, m in zip(translated, maps)]

    # Persist to disk so next session is instant
    cache[key] = result
    _save_cache(cache)
    return result


# ── English source strings ────────────────────────────────────────────────────
# All strings that appear in the UI.  Format placeholders MUST use
# the {name} syntax — they are protected from translation automatically.
_EN_UI_ORDERED = [
    ("app_title",         "🌍 Student Climate Simulator (AI Powered)"),
    ("model_error",       "Model not found! Please run the training script first."),
    ("welcome",           "Welcome to the Climate Simulator. Read your Stage Mission carefully!"),
    ("mission_label",     "**Your Mission:** "),
    ("win_goal_label",    "🎯 **Win Goal:** "),
    ("progress_label",    "Stage Progress (Round {round} of {max_rounds})"),
    ("about_stage",       "About This Stage"),
    ("under_hood",        "⚙️ What is happening under the hood? (AI Models)"),
    ("under_hood_desc",
        "When you make a policy choice, it alters hidden parameters of our country "
        "(like urbanization or fertilizer use). Those numbers are fed into a "
        "**Machine Learning AI Model** (Random Forest Regressor) which uses past "
        "scientific data to instantly predict carbon emissions, temperature, budget, "
        "and public support! Here is the raw data going into the AI right now:"),
    ("data_trends",       "📈 Data & Trends"),
    ("sci_feedback",      "**🧪 Scientific Feedback (Result of Last Action):**\n\n{feedback}"),
    ("temp_tracking",     "Temperature Tracking"),
    ("budget_tracking",   "Budget Tracking"),
    ("action_center",     "⚡ Action Center"),
    ("choose_policy",     "Choose Your Next Policy:"),
    ("hint_label",        "💡 *Hint: {hint}*"),
    ("ai_prediction",
        "📊 **AI Prediction:** Temp: ``{temp_diff}°C`` | "
        "Carbon: ``{carb_diff} Mt`` | Budget: ``${budg_diff}M`` | "
        "Support: ``{supp_diff}%``"),
    ("implement_policy_btn", "Implement Policy"),
    ("num_impact_label",
        "\n\n**Numerical Impact:** Temp: {temp_diff}°C | Carbon: {carb_diff} Mt | "
        "Budget: ${budg_diff}M | Support: {supp_diff}%"),
    ("fail_temp",
        "🔥 Global temperatures met or exceeded 2.0°C! Irreversible sea-level rise has flooded "
        "coastal cities, and lethal heatwaves have caused total ecological collapse."),
    ("fail_support",
        "😡 Public Support dropped below 20%. Food shortages and climate anxiety "
        "have sparked massive riots. The citizens have overthrown your government!"),
    ("fail_budget",
        "💸 The National Budget has hit zero. The country has defaulted, leading to "
        "total economic collapse. The government can no longer function or protect its citizens!"),
    ("stage_clear",       "✅ You successfully cleared {title}! You met all requirements."),
    ("goal_not_met",      "🚨 GOAL NOT MET: {fail_msg}"),
    ("restart_btn",       "🔄 Restart Game"),
    ("win_msg",           "🎉 YOU WIN! You have completed all stages and stabilized the global climate!"),
    ("report_card_title", "📊 Final Policy Report Card"),
    ("report_card_desc",  "Here is how your leadership balanced the key metrics:"),
    ("play_again_btn",    "🔄 Play Again"),
    ("metric_temp",       "Global Temp"),
    ("metric_temp_help",
        "Global average temperature rise since pre-industrial levels. "
        "Exceeding 2.0°C causes catastrophic tipping points (Instant Game Over)."),
    ("metric_carb",       "Carbon Emission"),
    ("metric_carb_help",  "Megatons (Mt) of CO2 released into the atmosphere per year."),
    ("metric_budg",       "Budget"),
    ("metric_budg_help",
        "Millions of dollars left in the government budget. "
        "Hitting $0 means bankruptcy (Instant Game Over)."),
    ("metric_supp",       "Public Support"),
    ("metric_supp_help",
        "Percentage of citizens who approve of your leadership. "
        "Dropping below 20% causes government overthrow (Instant Game Over)."),
]

_EN_UI = dict(_EN_UI_ORDERED)

# ── Mission text fields (translated) ─────────────────────────────────────────
_EN_MISSIONS = {
    1: {
        "title":        "Stage 1: Protecting Our Forests & Food",
        "sdg":          "🌱 **SDG 15: Life on Land** | 🌾 **SDG 2: Zero Hunger**",
        "problem":      "Deforestation and harsh farming chemicals are hurting our land and animals. As a leader, you must protect nature while keeping people fed and happy.",
        "goal_text":    "Lower Carbon Emissions to 160.0 Mt or lower AND keep Public Support above 50%.",
        "context":      "Forests act as 'carbon sinks,' meaning they absorb massive amounts of CO2 from the air. When forests are cut down for agriculture or timber, that trapped carbon is released, making global warming worse. At the same time, harsh chemical fertilizers used in farming run off into rivers, polluting the water. However, abruptly stopping farming can lead to food shortages. You must find a balance between protecting nature and sustaining livelihoods.",
        "fail_message": "You failed to lower emissions, or angered the public too much! Severe droughts and agricultural collapse have devastated the land.",
        "max_rounds":   3,
        "check_win":    lambda s: s.carbon <= 160.0 and s.support > 50.0,
    },
    2: {
        "title":        "Stage 2: Green Cities & Smart Transit",
        "sdg":          "🏙️ **SDG 11: Sustainable Cities** | 🏭 **SDG 9: Industry & Infrastructure**",
        "problem":      "Our cities are filled with smog and traffic jams. You need to fix how people travel without going bankrupt!",
        "goal_text":    "Keep the Budget above $300M AND ensure Public Support is at or above 60%.",
        "context":      "Transportation is one of the largest sources of greenhouse gases globally. Traditional cars rely on fossil fuels, releasing smog that chokes city air. Shifting thousands of people onto public transit drastically reduces the 'carbon footprint' per person. However, building railways is incredibly expensive. Can you afford to modernize the city?",
        "fail_message": "You bankrupted the city or citizens protested! Urban infrastructure has crumbled under extreme, unbreathable smog.",
        "max_rounds":   2,
        "check_win":    lambda s: s.budget >= 300.0 and s.support >= 60.0,
    },
    3: {
        "title":        "Stage 3: The Energy Transition",
        "sdg":          "⚡ **SDG 7: Affordable & Clean Energy** | 🌍 **SDG 13: Climate Action**",
        "problem":      "The country runs on dirty coal power. You must upgrade the power grid before the planet gets too hot!",
        "goal_text":    "Keep Global Temperature at or below 1.5°C.",
        "context":      "For decades, humanity has burned fossil fuels to generate electricity. This releases CO2, acting like a blanket trapping the sun's heat—causing Global Warming. A rise of more than 1.5°C will cause catastrophic sea-level rise and extreme weather. We must transition to renewable energy like solar, wind, or nuclear. But these transitions disrupt established industries and can cost billions.",
        "fail_message": "Global temperatures exceeded the 1.5°C threshold. The energy grid failed the climate, unleashing super-monsoons and devastating typhoons across the region.",
        "max_rounds":   2,
        "check_win":    lambda s: s.temperature <= 1.5,
    },
}

_MISSION_TEXT_KEYS = ("title", "sdg", "problem", "goal_text", "context", "fail_message")

# ── Choice text fields (translated) ──────────────────────────────────────────
_EN_CHOICES = {
    1: {
        1: [
            {"label": "🚫 🌱 Option A: Total Ban on Logging",
             "hint": "[SDG 15] Fast nature recovery, but requires expensive enforcement.",
             "effects": {"deforestation_rate": -30, "carbon_tax_level": +5, "carbon": -15.0, "temperature": -0.05},
             "explanation": "Banning logging immediately stopped large-scale tree cutting. However, the government had to spend millions hiring forest rangers to enforce the ban!"},
            {"label": "🤝 🌾 Option B: Empower Local Communities",
             "hint": "[SDG 2] Slower recovery, but cheaper and highly supported by locals.",
             "effects": {"deforestation_rate": -15, "support": +10, "budget": -10, "carbon": -5.0, "temperature": -0.01},
             "explanation": "Giving local indigenous groups the rights to manage their own forests led to sustainable logging practices. The people love you for trusting them!"},
            {"label": "💣 🪓 Option C: Sell Forests to Logging Conglomerate",
             "hint": "[SDG 15] Massive instant wealth, but nature is completely destroyed and citizens will riot.",
             "effects": {"deforestation_rate": +50, "support": -85, "budget": +200, "carbon": +30.0, "temperature": +0.15},
             "explanation": "You sold off the final protected lands. The country made hundreds of millions overnight, but the forests were clear-cut in weeks. Citizens lost their homes to extreme flooding, and the riots have begun."},
        ],
        2: [
            {"label": "🥩 🌾 Option A: Tax Meat Products",
             "hint": "[SDG 2] Creates a huge budget surplus, but causes major public protests.",
             "effects": {"livestock_population": -25, "support": -15, "budget": +50, "carbon": -20.0, "temperature": -0.08},
             "explanation": "Cows produce a lot of methane—a greenhouse gas 25x worse than CO2. Making meat expensive dropped emissions rapidly, but citizens protested in the streets over food costs!"},
            {"label": "🧪 💡 Option B: Fund Fake-Meat Research",
             "hint": "[SDG 9] Very popular with citizens, but drains the national budget.",
             "effects": {"livestock_population": -10, "support": +15, "budget": -40, "carbon": -8.0, "temperature": -0.03},
             "explanation": "By funding plant-based meat startups, fake meat became cheaper than real meat. People loved the tasty burgers, but the scientific grants drained government funds."},
        ],
        3: [
            {"label": "🌱 🌊 Option A: Subsidize Safe Fertilizers",
             "hint": "[SDG 14] Improves soil safely but costs money.",
             "effects": {"fertilizer_use": -20, "support": +5, "budget": -30, "carbon": -5.0},
             "explanation": "Paying farmers extra to use organic fertilizers stopped rivers from being polluted with chemicals. It was expensive, but farmers appreciated the help."},
            {"label": "⚠️ 🌊 Option B: Ban Toxic Chemicals Instantly",
             "hint": "[SDG 14] Stops pollution immediately, but causes farmers to lose money and protest.",
             "effects": {"fertilizer_use": -40, "support": -20, "budget": 0, "carbon": -10.0, "temperature": -0.02},
             "explanation": "An instant ban on synthetic fertilizers completely fixed water pollution. Unfortunately, crop sizes shrank drastically, and furious farmers demand your resignation!"},
        ],
    },
    2: {
        1: [
            {"label": "🚌 🏙️ Option A: Buy Thousands of Electric Buses",
             "hint": "[SDG 11] Greatly lowers carbon footprints, but increases city crowding.",
             "effects": {"public_buses_deployed": +40, "car_pooling_rate": +10, "urbanization_rate": +5, "budget": -50, "carbon": -25.0, "temperature": -0.10},
             "explanation": "The massive fleet of new electric buses took thousands of cars off the road. However, because transit became so easy, more people moved from the countryside into the city, increasing crowding."},
            {"label": "🚄 🏭 Option B: Build a Mega High-Speed Railway",
             "hint": "[SDG 9] Massive national pride and shift from cars, but costs a fortune.",
             "effects": {"fossil_fuel_use": -15, "budget": -120, "support": +15, "carbon": -15.0, "temperature": -0.05},
             "explanation": "The bullet train project was an incredible feat of engineering. Citizens are proud to ride it, but the construction cost almost bankrupted the state!"},
            {"label": "💣 🚗 Option C: Abolish Public Transit & Build 10-Lane Highways",
             "hint": "[SDG 11] Saves transit costs but causes unbreathable smog.",
             "effects": {"public_buses_deployed": -50, "car_pooling_rate": -20, "budget": +100, "fossil_fuel_use": +40, "carbon": +45.0, "temperature": +0.20},
             "explanation": "You shut down all bus and train services, forcing everyone to use cars. The city became a massive traffic jam. Air quality hit danger levels immediately, causing mass hospitalizations from lethal smog."},
        ],
        2: [
            {"label": "🛑 🏙️ Option A: Force Mandatory Carpooling",
             "hint": "[SDG 11] Costs $0, drastically cuts emissions, but citizens HATE being forced.",
             "effects": {"car_pooling_rate": +30, "support": -15, "carbon": -20.0, "temperature": -0.06},
             "explanation": "You passed a law making it illegal to drive alone. The city air cleared up overnight and it cost the government nothing, but annoyed commuters are furious at losing their freedom."},
            {"label": "⚡ 🌍 Option B: Subsidize Electric Cars for Everyone",
             "hint": "[SDG 13] Clears the air and people love it, but takes a huge chunk of your budget.",
             "effects": {"fossil_fuel_use": -10, "air_pollution_control": +20, "support": +10, "budget": -60, "carbon": -35.0, "temperature": -0.12},
             "explanation": "By paying for half the cost of EVs, practically everyone traded in their gas guzzlers. The smog is gone and people love their new cars, but it was extremely expensive."},
        ],
    },
    3: {
        1: [
            {"label": "☀️ ⚡ Option A: Build the World's Largest Solar Farm",
             "hint": "[SDG 7] Safe and effective, but extremely expensive.",
             "effects": {"renewable_investment": +40, "fossil_fuel_use": -20, "budget": -100, "carbon": -40.0, "temperature": -0.15},
             "explanation": "Miles of solar panels now collect the sun's energy, allowing you to shut down several dirty coal plants. The air is cleaner, but installing all those panels cost billions."},
            {"label": "⚛️ ⚡ Option B: Build a Nuclear Power Plant",
             "hint": "[SDG 7] Produces massive amounts of clean power, but scares the public.",
             "effects": {"renewable_investment": +50, "fossil_fuel_use": -30, "support": -25, "budget": -80, "carbon": -50.0, "temperature": -0.18},
             "explanation": "Nuclear fission provides incredible amounts of energy with zero carbon emissions. Unfortunately, citizens are terrified of a potential meltdown and are protesting its construction."},
            {"label": "💣 🏭 Option C: Subsidize Unregulated Coal Mining",
             "hint": "[SDG 13] The cheapest way to get electricity, but guarantees catastrophic warming.",
             "effects": {"fossil_fuel_use": +50, "renewable_investment": -30, "budget": +50, "carbon": +60.0, "temperature": +0.30},
             "explanation": "You bet on dirty coal because it was cheap. The economy saw a short boom, but the massive surge in carbon emissions pushed the temperature past the point of no return, guaranteeing lethal heatwaves!"},
        ],
        2: [
            {"label": "💰 🌍 Option A: Charge Polluters a Carbon Tax",
             "hint": "[SDG 13] Makes the government extremely rich, but businesses and citizens will be outraged.",
             "effects": {"carbon_tax_level": +50, "budget": +150, "support": -30, "carbon": -25.0, "temperature": -0.05},
             "explanation": "By forcing companies to pay heavily for every ton of CO2 they emit, they rapidly chose to go green. The government made a fortune, but companies passed the costs to consumers, making everything more expensive. People are furious!"},
            {"label": "🏭 💡 Option B: Fund Experimental Carbon Vacuums",
             "hint": "[SDG 9] Futuristic tech that sucks carbon out of the air—people love it, but costs millions.",
             "effects": {"carbon_capture_tech": +40, "budget": -90, "support": +5, "carbon": -80.0, "temperature": -0.25},
             "explanation": "You funded giant Direct Air Capture (DAC) fans that literally suck CO2 from the sky and bury it underground. It feels like science fiction and citizens love it, but it is incredibly expensive to run."},
        ],
    },
}

_CHOICE_TEXT_KEYS = ("label", "hint", "explanation")


# ── Public API ────────────────────────────────────────────────────────────────
def get_ui_strings(lang: str) -> dict:
    """Return the full UI string dict, translated if needed."""
    if lang == "en":
        return _EN_UI.copy()
    keys = [k for k, _ in _EN_UI_ORDERED]
    values = [v for _, v in _EN_UI_ORDERED]
    translated = _translate_list(values, lang)
    return dict(zip(keys, translated))


def get_missions(lang: str) -> dict:
    """Return stage mission dicts, text fields translated."""
    if lang == "en":
        return _EN_MISSIONS.copy()

    # Collect all translatable text in order so we can do one batch
    order = []
    for stage_num in sorted(_EN_MISSIONS):
        mission = _EN_MISSIONS[stage_num]
        for k in _MISSION_TEXT_KEYS:
            order.append((stage_num, k, mission[k]))

    translated_texts = _translate_list([t for _, _, t in order], lang)

    result = {}
    i = 0
    for stage_num in sorted(_EN_MISSIONS):
        m = dict(_EN_MISSIONS[stage_num])
        for k in _MISSION_TEXT_KEYS:
            m[k] = translated_texts[i]
            i += 1
        result[stage_num] = m
    return result


def get_choices(lang: str) -> dict:
    """Return policy choice dicts, text fields translated."""
    if lang == "en":
        return _EN_CHOICES.copy()

    # Flatten text for one batch call
    order = []       # (stage, round, choice_idx, key)
    for stage in sorted(_EN_CHOICES):
        for rnd in sorted(_EN_CHOICES[stage]):
            for ci, choice in enumerate(_EN_CHOICES[stage][rnd]):
                for k in _CHOICE_TEXT_KEYS:
                    order.append((stage, rnd, ci, k, choice[k]))

    translated_texts = _translate_list([t for *_, t in order], lang)

    # Rebuild structure
    result = {s: {r: [dict(c) for c in lst]
                  for r, lst in rnd_map.items()}
              for s, rnd_map in _EN_CHOICES.items()}
    for idx, (stage, rnd, ci, k, _) in enumerate(order):
        result[stage][rnd][ci][k] = translated_texts[idx]
    return result