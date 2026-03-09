"""
translations.py — Dynamic API-driven Translation System
Uses deep-translator (Google Translate backend) to translate the game
into any language. Results are cached in st.session_state to avoid
repeated API calls on every page render.
"""
from deep_translator import GoogleTranslator

# ── Language catalogue ──────────────────────────────────────────────────────
# Keys are what deep-translator / Google Translate accepts.
LANGUAGES = {
	"🇬🇧 English":             "en",
	"🇮🇩 Bahasa Indonesia":    "id",
	"🇲🇾 Bahasa Melayu":       "ms",
	"🇨🇳 中文 (简体)":         "zh-CN",
	"🇯🇵 日本語":               "ja",
	"🇰🇷 한국어":               "ko",
	"🇸🇦 العربية":             "ar",
	"🇫🇷 Français":            "fr",
	"🇪🇸 Español":             "es",
	"🇩🇪 Deutsch":             "de",
	"🇮🇳 हिन्दी":              "hi",
}

# ── Base English strings (source of truth) ───────────────────────────────────
EN_UI = {
	"app_title": "🌍 Student Climate Simulator (AI Powered)",
	"model_error": "Model not found! Please run the training script first to generate 'climate_ai_model.pkl'.",
	"welcome": "Welcome to the Climate Simulator. Read your Stage Mission carefully!",
	"mission_label": "**Your Mission:** ",
	"win_goal_label": "🎯 **Win Goal:** ",
	"progress_label": "Stage Progress (Round {round} of {max_rounds})",
	"about_stage": "About This Stage",
	"under_hood": "⚙️ What is happening under the hood? (AI Models)",
	"under_hood_desc": (
		"When you make a policy choice, it alters hidden parameters of our country "
		"(like urbanization or fertilizer use). Those numbers are fed into a "
		"**Machine Learning AI Model** (Random Forest Regressor) which uses past "
		"scientific data to instantly predict the carbon emissions, temperature, "
		"budget, and public support! Here is the raw data going into the AI right now:"
	),
	"data_trends": "📈 Data & Trends",
	"sci_feedback": "**🧪 Scientific Feedback (Result of Last Action):**\n\n{feedback}",
	"temp_tracking": "Temperature Tracking",
	"budget_tracking": "Budget Tracking",
	"action_center": "⚡ Action Center",
	"choose_policy": "Choose Your Next Policy:",
	"hint_label": "💡 *Hint: {hint}*",
	"ai_prediction": (
		"📊 **AI Prediction:** Temp: ``{temp_diff}°C`` | "
		"Carbon: ``{carb_diff} Mt`` | Budget: ``${budg_diff}M`` | Support: ``{supp_diff}%``"
	),
	"implement_policy_btn": "Implement Policy",
	"num_impact_label": (
		"\n\n**Numerical Impact:** Temp: {temp_diff}°C | Carbon: {carb_diff} Mt | "
		"Budget: ${budg_diff}M | Support: {supp_diff}%"
	),
	"fail_temp": (
		"🔥 Global Temperature met or exceeded 2.0°C! The climate has reached a "
		"tipping point, leading to catastrophic and irreversible environmental damage."
	),
	"fail_support": (
		"😡 Public Support dropped below 20%. "
		"The citizens have rioted to overthrow your government!"
	),
	"fail_budget": (
		"💸 The National Budget has hit zero. "
		"The country has defaulted on its debt and the government cannot function!"
	),
	"stage_clear": "✅ You successfully cleared {title}! You met all the requirements.",
	"goal_not_met": "🚨 GOAL NOT MET: {fail_msg}",
	"restart_btn": "🔄 Restart Game",
	"win_msg": "🎉 YOU WIN! You have completed all stages and stabilized the global climate!",
	"report_card_title": "📊 Final Policy Report Card",
	"report_card_desc": "Here is how your leadership balanced the key metrics:",
	"play_again_btn": "🔄 Play Again",
	"metric_temp": "Global Temp",
	"metric_temp_help": (
		"Global average temperature rise since pre-industrial levels. "
		"Exceeding 2.0°C causes catastrophic tipping points (Instant Game Over)."
	),
	"metric_carb": "Carbon Emission",
	"metric_carb_help": "Megatons (Mt) of CO2 released into the atmosphere per year.",
	"metric_budg": "Budget",
	"metric_budg_help": (
		"Millions of dollars left in the government discretionary budget. "
		"Hitting $0 means bankruptcy (Instant Game Over)."
	),
	"metric_supp": "Public Support",
	"metric_supp_help": (
		"Percentage of citizens who currently approve of your leadership. "
		"Dropping below 20% causes government overthrow (Instant Game Over)."
	),
	"lang_sidebar_title": "🌍 Language",
	"lang_sidebar_subtitle": "Select your preferred language:",
	"lang_changed": "Language updated! The page will refresh.",
	"translating": "Translating… please wait a moment.",
}

# ── English stage missions (source of truth) ─────────────────────────────────
def _en_missions():
	return {
		1: {
			"title": "Stage 1: Protecting Our Forests & Food",
			"sdg": "🌱 **SDG 15: Life on Land** | 🌾 **SDG 2: Zero Hunger**",
			"problem": (
				"Deforestation and harsh farming chemicals are hurting our land and animals. "
				"As a leader, you must protect nature while keeping people fed and happy."
			),
			"goal_text": "Lower Carbon Emissions to 160.0 Mt or lower AND keep Public Support above 50%.",
			"context": (
				"Forests act as 'carbon sinks,' meaning they absorb massive amounts of CO2 from the air. "
				"When forests are cut down for agriculture or timber, that trapped carbon is released, "
				"making global warming worse. At the same time, harsh chemical fertilizers used in farming "
				"run off into rivers, polluting the water. However, abruptly stopping farming can lead to "
				"food shortages and angry citizens. You must find a balance between protecting nature and "
				"sustaining livelihoods."
			),
			"max_rounds": 3,
			"check_win": lambda state: state.carbon <= 160.0 and state.support > 50.0,
			"fail_message": "You failed to lower emissions enough, or you angered the public too much!",
		},
		2: {
			"title": "Stage 2: Green Cities & Smart Transit",
			"sdg": "🏙️ **SDG 11: Sustainable Cities** | 🏭 **SDG 9: Industry & Infrastructure**",
			"problem": (
				"Our cities are filled with smog and traffic jams. "
				"You need to fix how people travel without going bankrupt!"
			),
			"goal_text": "Keep the Budget above $300M AND ensure Public Support is exactly or above 60%.",
			"context": (
				"Transportation is one of the largest sources of greenhouse gases globally. "
				"Traditional cars rely on fossil fuels, releasing carbon monoxide and smog that choke city "
				"air and harm public health. Shifting thousands of people onto public transit (like buses or "
				"trains) drastically reduces the 'carbon footprint' per person. However, building huge "
				"infrastructure like railways is incredibly expensive and takes years to complete. "
				"Can you afford to modernize the city?"
			),
			"max_rounds": 2,
			"check_win": lambda state: state.budget >= 300.0 and state.support >= 60.0,
			"fail_message": "You either bankrupted the city or the citizens protested your transit policies!",
		},
		3: {
			"title": "Stage 3: The Energy Transition",
			"sdg": "⚡ **SDG 7: Affordable & Clean Energy** | 🌍 **SDG 13: Climate Action**",
			"problem": (
				"The country runs on dirty coal power. "
				"You must upgrade the power grid before the planet gets too hot!"
			),
			"goal_text": "Keep Global Temperature at or below 1.5°C.",
			"context": (
				"For decades, humanity has burned fossil fuels (coal, oil, and gas) to generate electricity. "
				"This releases massive amounts of CO2, acting like a blanket trapping the sun's heat—causing "
				"Global Warming. A rise of more than 1.5°C will cause catastrophic sea-level rise and extreme "
				"weather. To stop this, we must transition to renewable energy sources like solar, wind, or "
				"nuclear power. But these transitions disrupt established industries and can cost billions."
			),
			"max_rounds": 2,
			"check_win": lambda state: state.temperature <= 1.5,
			"fail_message": "Global temperatures exceeded the 1.5°C threshold. The energy grid failed the climate.",
		},
	}


# ── English policy choices (source of truth) ─────────────────────────────────
def _en_choices():
	return {
		1: {
			1: [
				{"label": "🚫 🌱 Option A: Total Ban on Logging",
				 "hint": "[SDG 15] Fast nature recovery, but requires expensive budget enforcement.",
				 "effects": {"deforestation_rate": -30, "carbon_tax_level": +5, "carbon": -15.0, "temperature": -0.05},
				 "explanation": "Banning logging immediately stopped large-scale tree cutting. However, the government had to spend millions hiring forest rangers to enforce the ban!"},
				{"label": "🤝 🌾 Option B: Empower Local Communities",
				 "hint": "[SDG 2] Slower recovery, but cheaper and highly supported by locals.",
				 "effects": {"deforestation_rate": -15, "support": +10, "budget": -10, "carbon": -5.0, "temperature": -0.01},
				 "explanation": "Giving local indigenous groups the rights to manage their own forests led to sustainable, careful logging practices. The people love you for trusting them!"},
				{"label": "💣 🪓 Option C: Sell Forests to Logging Conglomerate",
				 "hint": "[SDG 15] Massive instant wealth, but nature is completely destroyed and citizens will riot.",
				 "effects": {"deforestation_rate": +50, "support": -85, "budget": +200, "carbon": +30.0, "temperature": +0.15},
				 "explanation": "You sold off the final state-protected lands. The country made hundreds of millions of dollars overnight, but the forests were clear-cut within weeks. Citizens have lost their jobs and homes, and the rioting has begun."},
			],
			2: [
				{"label": "🥩 🌾 Option A: Tax Meat Products",
				 "hint": "[SDG 2] Creates a huge budget surplus, but causes major public protests.",
				 "effects": {"livestock_population": -25, "support": -15, "budget": +50, "carbon": -20.0, "temperature": -0.08},
				 "explanation": "Cows produce a lot of methane (a greenhouse gas 25x worse than carbon dioxide). Making meat expensive dropped emissions rapidly, but citizens protested in the streets over the cost of their food!"},
				{"label": "🧪 💡 Option B: Fund Fake-Meat Research",
				 "hint": "[SDG 9] Very popular with citizens, but drains the national budget.",
				 "effects": {"livestock_population": -10, "support": +15, "budget": -40, "carbon": -8.0, "temperature": -0.03},
				 "explanation": "By putting government money into plant-based meat startups, fake meat became cheaper than real meat. People loved the tasty burgers, but the scientific grants drained government funds."},
			],
			3: [
				{"label": "🌱 🌊 Option A: Subsidize Safe Fertilizers",
				 "hint": "[SDG 14] Improves soil safely but costs money.",
				 "effects": {"fertilizer_use": -20, "support": +5, "budget": -30, "carbon": -5.0},
				 "explanation": "Paying farmers extra to use natural, organic fertilizers stopped the rivers from being polluted with chemicals. It was expensive, but the farmers appreciated the help."},
				{"label": "⚠️ 🌊 Option B: Ban Toxic Chemicals Instantly",
				 "hint": "[SDG 14] Stops pollution immediately, but causes farmers to lose money and protest.",
				 "effects": {"fertilizer_use": -40, "support": -20, "budget": 0, "carbon": -10.0, "temperature": -0.02},
				 "explanation": "An instant ban on synthetic nitrogen fertilizers completely fixed the water pollution. Unfortunately, crop sizes shrank drastically, and furious farmers are demanding your resignation!"},
			],
		},
		2: {
			1: [
				{"label": "🚌 🏙️ Option A: Buy Thousands of Electric Buses",
				 "hint": "[SDG 11] Greatly lowers footprints, but increases city crowding/urbanization.",
				 "effects": {"public_buses_deployed": +40, "car_pooling_rate": +10, "urbanization_rate": +5, "budget": -50, "carbon": -25.0, "temperature": -0.10},
				 "explanation": "The massive fleet of new electric buses took thousands of cars off the road. However, because transit became so easy, more people moved from the countryside into the city, increasing crowding."},
				{"label": "🚄 🏭 Option B: Build a Mega High-Speed Railway",
				 "hint": "[SDG 9] Massive national pride and shift from cars, but costs a fortune.",
				 "effects": {"fossil_fuel_use": -15, "budget": -120, "support": +15, "carbon": -15.0, "temperature": -0.05},
				 "explanation": "The bullet train project was an incredible feat of engineering. Citizens are incredibly proud to ride it instead of flying or driving, but the construction cost almost bankrupted the state!"},
				{"label": "💣 🚗 Option C: Abolish Public Transit & Build 10-Lane Highways",
				 "hint": "[SDG 11] Solves public transit budget issues by eliminating them, but causes unbreathable smog.",
				 "effects": {"public_buses_deployed": -50, "car_pooling_rate": -20, "budget": +100, "fossil_fuel_use": +40, "carbon": +45.0, "temperature": +0.20},
				 "explanation": "You shut down all bus and rail services, forcing everyone into cars. While the government saved tons of money on maintenance, the city became a massive traffic jam. The air quality index hit dangerous levels immediately."},
			],
			2: [
				{"label": "🛑 🏙️ Option A: Force Mandatory Carpooling",
				 "hint": "[SDG 11] Costs $0, drastically cuts emissions, but citizens HATE being forced.",
				 "effects": {"car_pooling_rate": +30, "support": -15, "carbon": -20.0, "temperature": -0.06},
				 "explanation": "You passed a law making it illegal to drive alone. The city air cleared up overnight and it cost the government nothing, but annoyed commuters are furious at losing their freedom."},
				{"label": "⚡ 🌍 Option B: Subsidize Electric Cars for Everyone",
				 "hint": "[SDG 13] Clears the air and people love it, but takes a huge chunk of your budget.",
				 "effects": {"fossil_fuel_use": -10, "air_pollution_control": +20, "support": +10, "budget": -60, "carbon": -35.0, "temperature": -0.12},
				 "explanation": "By paying for half the cost of electric vehicles (EVs), practically everyone traded in their gas guzzlers. The smog is gone and people love their new cars, but it was an extremely expensive policy."},
			],
		},
		3: {
			1: [
				{"label": "☀️ ⚡ Option A: Build the World's Largest Solar Farm",
				 "hint": "[SDG 7] Safe and effective, but extremely expensive.",
				 "effects": {"renewable_investment": +40, "fossil_fuel_use": -20, "budget": -100, "carbon": -40.0, "temperature": -0.15},
				 "explanation": "Miles and miles of solar panels now collect the sun's energy, allowing you to shut down several dirty coal plants. The air is cleaner, but installing all those panels cost billions."},
				{"label": "⚛️ ⚡ Option B: Build a Nuclear Power Plant",
				 "hint": "[SDG 7] Produces massive amounts of clean power, but scares the public.",
				 "effects": {"renewable_investment": +50, "fossil_fuel_use": -30, "support": -25, "budget": -80, "carbon": -50.0, "temperature": -0.18},
				 "explanation": "Nuclear fission provides incredible amounts of energy with absolutely zero carbon emissions. Unfortunately, citizens are terrified of a potential meltdown and are protesting the reactor's construction."},
				{"label": "💣 🏭 Option C: Subsidize Unregulated Coal Mining",
				 "hint": "[SDG 13] The cheapest, fastest way to get electricity, but guarantees catastrophic warming.",
				 "effects": {"fossil_fuel_use": +50, "renewable_investment": -30, "budget": +50, "carbon": +60.0, "temperature": +0.30},
				 "explanation": "You doubled down on dirty coal because it was cheap. The economy saw a short boom, but the massive surge in carbon emissions pushed the global temperature past the point of no return!"},
			],
			2: [
				{"label": "💰 🌍 Option A: Charge Polluters a Carbon Tax",
				 "hint": "[SDG 13] Makes the government extremely rich, but businesses and citizens will be outraged.",
				 "effects": {"carbon_tax_level": +50, "budget": +150, "support": -30, "carbon": -25.0, "temperature": -0.05},
				 "explanation": "By forcing companies to pay heavily for every ton of CO2 they emit, they rapidly chose to go green. The government made a fortune in tax revenue, but the companies passed the costs onto consumers, making everything more expensive. People are furious!"},
				{"label": "🏭 💡 Option B: Fund Experimental Carbon Vacuums",
				 "hint": "[SDG 9] Futuristic tech that sucks carbon out of the air—people love it, but it costs millions.",
				 "effects": {"carbon_capture_tech": +40, "budget": -90, "support": +5, "carbon": -80.0, "temperature": -0.25},
				 "explanation": "You funded giant Direct Air Capture (DAC) fans that literally suck carbon dioxide out of the sky and bury it underground. It feels like science fiction and the citizens love it, but it is incredibly expensive to run."},
			],
		},
	}


# ── Core translation helper ──────────────────────────────────────────────────
def _translate_text(text: str, target_lang: str) -> str:
	"""Translate a single string. Falls back to source text on any error."""
	if target_lang == "en" or not text.strip():
		return text
	try:
		return GoogleTranslator(source="en", target=target_lang).translate(text)
	except Exception:
		return text  # graceful fallback — never crash the game


def _tx(d: dict, key: str, lang: str) -> str:
	"""Translate dict[key] text if language is not English."""
	return _translate_text(d[key], lang)


# ── Public API ───────────────────────────────────────────────────────────────
def get_ui_strings(lang: str) -> dict:
	"""Return a UI-string dict with all values translated to `lang`."""
	if lang == "en":
		return EN_UI.copy()
	translated = {}
	for key, value in EN_UI.items():
		# Skip format-placeholder strings — translate the template once
		translated[key] = _translate_text(value, lang)
	return translated


def get_missions(lang: str) -> dict:
	"""Return stage-mission dicts translated to `lang`."""
	en = _en_missions()
	if lang == "en":
		return en
	translated = {}
	for stage_num, mission in en.items():
		t = {}
		for key in ("title", "sdg", "problem", "goal_text", "context", "fail_message"):
			t[key] = _translate_text(mission[key], lang)
		# These must remain as Python objects (not translated strings)
		t["max_rounds"] = mission["max_rounds"]
		t["check_win"] = mission["check_win"]
		translated[stage_num] = t
	return translated


def get_choices(lang: str) -> dict:
	"""Return policy choices with label, hint, and explanation translated to `lang`."""
	en = _en_choices()
	if lang == "en":
		return en
	translated = {}
	for stage_num, rounds in en.items():
		translated[stage_num] = {}
		for round_num, choices in rounds.items():
			translated[stage_num][round_num] = []
			for choice in choices:
				tc = dict(choice)  # copy effects etc.
				tc["label"] = _translate_text(choice["label"], lang)
				tc["hint"] = _translate_text(choice["hint"], lang)
				tc["explanation"] = _translate_text(choice["explanation"], lang)
				translated[stage_num][round_num].append(tc)
	return translated
