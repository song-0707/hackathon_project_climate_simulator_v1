import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from translations import LANGUAGES, get_ui_strings, get_missions, get_choices


# ==========================================
# 1. LOAD THE TRAINED AI MODEL
# ==========================================
@st.cache_resource
def load_ai_model():
	try:
		return joblib.load("climate_ai_model.pkl")
	except FileNotFoundError:
		return None


# ==========================================
# 2. STAGE MISSIONS & WIN CONDITIONS
# ==========================================
# Stage missions moved to translations.py


# ==========================================
# 3. CORE ENGINE & STATE MANAGEMENT
# ==========================================
class GameState:
	def __init__(self, model, welcome_msg=""):
		self.game_over = False
		self.game_won = False
		self.last_explanation = ""
		self.stage_clear_message = ""
		self.dynamic_fail_message = ""

		self.setup_stage(1, model)

	def setup_stage(self, stage_num, model):
		self.stage = stage_num
		self.round = 1

		self.features = {
			"car_pooling_rate": 20.0,
			"carbon_tax_level": 5.0,
			"public_buses_deployed": 30.0,
			"fossil_fuel_use": 60.0,
			"renewable_investment": 20.0,
			"deforestation_rate": 50.0,
			"livestock_population": 50.0,
			"fertilizer_use": 40.0,
			"carbon_capture_tech": 10.0,
			"urbanization_rate": 50.0,
			"air_pollution_control": 30.0
		}

		feature_df = pd.DataFrame([self.features])
		predictions = model.predict(feature_df)[0]

		self.temperature = round(predictions[0], 2)
		self.carbon = round(predictions[1], 1)
		self.budget = round(predictions[2], 1)
		self.support = round(predictions[3], 1)

		self.prev_temperature = self.temperature
		self.prev_carbon = self.carbon
		self.prev_budget = self.budget
		self.prev_support = self.support

		# --- NEW: Setup History DataFrame for Line Charts ---
		self.history = pd.DataFrame({
			"Round": [self.round],
			"Temperature": [self.temperature],
			"Carbon": [self.carbon],
			"Budget": [self.budget],
			"Support": [self.support]
		})


def run_ai_inference(state, model, choice_effects):
	state.prev_temperature = state.temperature
	state.prev_carbon = state.carbon
	state.prev_budget = state.budget
	state.prev_support = state.support

	for feature, change in choice_effects.items():
		if feature in state.features:
			state.features[feature] = max(0.0, min(100.0, state.features[feature] + change))

	feature_df = pd.DataFrame([state.features])
	predictions = model.predict(feature_df)[0]

	state.temperature = round(predictions[0] + choice_effects.get("temperature", 0.0), 2)
	state.carbon = round(predictions[1] + choice_effects.get("carbon", 0.0), 1)
	state.budget = round(predictions[2] + choice_effects.get("budget", 0.0), 1)
	state.support = round(predictions[3] + choice_effects.get("support", 0.0), 1)


def predict_policy_impact(state, model, choice_effects):
	"""Runs a counterfactual prediction to show expected impacts before a choice is made."""
	temp_features = state.features.copy()
	for feature, change in choice_effects.items():
		if feature in temp_features:
			temp_features[feature] = max(0.0, min(100.0, temp_features[feature] + change))

	feature_df = pd.DataFrame([temp_features])
	predictions = model.predict(feature_df)[0]

	p_temp = round(predictions[0] + choice_effects.get("temperature", 0.0), 2)
	p_carb = round(predictions[1] + choice_effects.get("carbon", 0.0), 1)
	p_budg = round(predictions[2] + choice_effects.get("budget", 0.0), 1)
	p_supp = round(predictions[3] + choice_effects.get("support", 0.0), 1)

	temp_diff = p_temp - state.temperature
	carb_diff = p_carb - state.carbon
	budg_diff = p_budg - state.budget
	supp_diff = p_supp - state.support

	return temp_diff, carb_diff, budg_diff, supp_diff


# ==========================================
# 4. DECISION DATA
# ==========================================
# Choices moved to translations.py


# ==========================================
# 5. STREAMLIT APP & UI
# ==========================================
def main():
	st.set_page_config(page_title="Climate Simulator", page_icon="🌍", layout="wide")
	
	if 'language' not in st.session_state:
		st.session_state.language = 'en'
		st.session_state.lang_label = '🇬🇧 English'

	# =========================================
	# --- COLLAPSIBLE LANGUAGE SELECTOR SIDEBAR ---
	# =========================================
	with st.sidebar:
		st.markdown("### 🌍 Language")
		st.caption("Select your preferred language:")
		selected_label = st.selectbox(
			"Language",
			list(LANGUAGES.keys()),
			index=list(LANGUAGES.keys()).index(st.session_state.lang_label),
			label_visibility="collapsed"
		)
		if selected_label != st.session_state.lang_label:
			st.session_state.lang_label = selected_label
			st.session_state.language = LANGUAGES[selected_label]
			# Clear cached translations when language changes
			if 'cached_t' in st.session_state:
				del st.session_state['cached_t']
			if 'cached_missions' in st.session_state:
				del st.session_state['cached_missions']
			if 'cached_choices' in st.session_state:
				del st.session_state['cached_choices']
			st.rerun()
		st.divider()

	# Load and cache translations in session_state (avoids re-translating every render)
	lang = st.session_state.language
	need_translate = 'cached_t' not in st.session_state or st.session_state.get('cached_lang') != lang

	if need_translate and lang != 'en':
		# Check if this language already exists in the disk cache
		import json, os
		is_cached_on_disk = False
		try:
			cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.translation_cache.json')
			if os.path.exists(cache_file):
				with open(cache_file, 'r', encoding='utf-8') as f:
					cache_data = json.load(f)
				is_cached_on_disk = len(cache_data) > 0
		except Exception:
			pass

		if not is_cached_on_disk:
			# Only show a warning when a slow API call is genuinely needed
			with st.sidebar:
				st.warning(
					"⏳ **First-time translation!**\n\n"
					"This language has never been loaded before. "
					"The app will call the Google Translate API to translate all text.\n\n"
					"**Estimated time: 30–90 seconds.**\n\n"
					"After this, it will be saved and load instantly forever! ✅\n\n"
					"💡 *Tip: Run `python preload_translations.py` to pre-cache all 11 languages at once.*"
				)

		spinner_msg = "🌐 Translating interface — please wait..." if not is_cached_on_disk else "Loading language..."
		with st.spinner(spinner_msg):
			st.session_state.cached_t = get_ui_strings(lang)
			st.session_state.cached_missions = get_missions(lang)
			st.session_state.cached_choices = get_choices(lang)
			st.session_state.cached_lang = lang

		if not is_cached_on_disk:
			st.toast("✅ Translation complete! Language switched.", icon="🌍")
		# Rerun so the sidebar warning is cleared and the translated UI renders cleanly
		st.rerun()
	elif need_translate:
		st.session_state.cached_t = get_ui_strings(lang)
		st.session_state.cached_missions = get_missions(lang)
		st.session_state.cached_choices = get_choices(lang)
		st.session_state.cached_lang = lang

	t = st.session_state.cached_t
	STAGE_MISSIONS = st.session_state.cached_missions
	CHOICES = st.session_state.cached_choices
	
	model = load_ai_model()

	if model is None:
		st.error(t["model_error"])
		return

	if 'game' not in st.session_state:
		st.session_state.game = GameState(model, t["welcome"])

	game = st.session_state.game

	st.title(t["app_title"])
	
	# --- GAME OVER STATE ---
	if game.game_over:
		fail_msg = getattr(game, 'dynamic_fail_message', "") or STAGE_MISSIONS[game.stage]['fail_message']
		st.error(t["goal_not_met"].format(fail_msg=fail_msg))
		if st.button(t["restart_btn"], type="primary"):
			st.session_state.game = GameState(model, t["welcome"])
			st.rerun()
		return

	# --- GAME WON STATE (RADAR CHART) ---
	if game.game_won:
		st.success(t["win_msg"])
		st.balloons()

		st.subheader(t["report_card_title"])
		st.write(t["report_card_desc"])

		# Normalize scores out of 100 for the radar chart
		support_score = min(100, max(0, game.support))
		budget_score = min(100, max(0, (game.budget / 500) * 100))
		carbon_score = min(100, max(0, 100 - (game.carbon - 50)))
		temp_score = min(100, max(0, 100 - ((game.temperature - 1.0) * 100)))

		categories = ['Public Support', 'Economic Health', 'Carbon Reduction', 'Climate Stability']

		fig = go.Figure(data=go.Scatterpolar(
			r=[support_score, budget_score, carbon_score, temp_score, support_score],
			theta=categories + [categories[0]],
			fill='toself',
			line_color='#2ca02c'
		))
		fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)

		st.plotly_chart(fig, use_container_width=True)

		if st.button(t["play_again_btn"], type="primary"):
			st.session_state.game = GameState(model, t["welcome"])
			st.rerun()
		return

	# --- TOP METRICS BAR ---
	if game.stage_clear_message:
		st.success(game.stage_clear_message)

	current_mission = STAGE_MISSIONS[game.stage]

	st.divider()
	metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

	temp_delta = round(game.temperature - game.prev_temperature, 2)
	carb_delta = round(game.carbon - game.prev_carbon, 1)
	budg_delta = round(game.budget - game.prev_budget, 1)
	supp_delta = round(game.support - game.prev_support, 1)

	metric_col1.metric(t["metric_temp"], f"{game.temperature}°C", f"{temp_delta}°C", delta_color="inverse", help=t["metric_temp_help"])
	metric_col2.metric(t["metric_carb"], f"{game.carbon} Mt", f"{carb_delta} Mt", delta_color="inverse", help=t["metric_carb_help"])
	metric_col3.metric(t["metric_budg"], f"${game.budget}M", f"${budg_delta}M", delta_color="normal", help=t["metric_budg_help"])
	metric_col4.metric(t["metric_supp"], f"{game.support}%", f"{supp_delta}%", delta_color="normal", help=t["metric_supp_help"])

	# --- UNIFIED 3-COLUMN DASHBOARD ---
	left_col, center_col, right_col = st.columns([1, 1.8, 1.2], gap="small")

	with left_col:
		st.subheader(f"🎓 {current_mission['title']}")
		st.markdown(current_mission["sdg"])
		
		with st.container(border=True):
			st.markdown(f"{t['mission_label'].strip()} {current_mission['problem']}")
			st.info(f"{t['win_goal_label'].strip()} {current_mission['goal_text']}")

			progress_val = (game.round - 1) / current_mission["max_rounds"]
			st.progress(progress_val, text=t["progress_label"].format(round=game.round, max_rounds=current_mission['max_rounds']))
			
		with st.container(border=True):
			st.subheader(t["about_stage"])
			st.markdown(f"{current_mission['context']}")
			
		with st.expander(t["under_hood"]):
			st.markdown(t["under_hood_desc"])
			st.json(game.features)

	with center_col:
		st.subheader(t["data_trends"])
		st.success(t["sci_feedback"].format(feedback=game.last_explanation or t["welcome"]))
		
		with st.container(border=True):
			st.caption(t["temp_tracking"])
			st.line_chart(game.history.set_index("Round")["Temperature"], color="#ff4b4b", height=130)
			
		with st.container(border=True):
			st.caption(t["budget_tracking"])
			st.line_chart(game.history.set_index("Round")["Budget"], color="#00b4d8", height=130)

	with right_col:
		st.subheader(t["action_center"])
		st.write(t["choose_policy"])
		
		current_choices = CHOICES.get(game.stage, {}).get(game.round, [])

		for idx, choice in enumerate(current_choices):
			with st.container(border=True):
				st.markdown(f"**{choice['label']}**")
				st.caption(t["hint_label"].format(hint=choice['hint']))
				
				p_temp, p_carb, p_budg, p_supp = predict_policy_impact(game, model, choice["effects"])
				
				# Format strings nicely
				st.markdown(t["ai_prediction"].format(
					temp_diff=f"{'+' if p_temp>=0 else ''}{p_temp:.2f}",
					carb_diff=f"{'+' if p_carb>=0 else ''}{p_carb:.1f}",
					budg_diff=f"{'+' if p_budg>=0 else ''}{p_budg:.1f}",
					supp_diff=f"{'+' if p_supp>=0 else ''}{p_supp:.1f}"
				))

				if st.button(t["implement_policy_btn"], key=f"choice_{game.stage}_{game.round}_{idx}", use_container_width=True):
					game.stage_clear_message = ""
					run_ai_inference(game, model, choice["effects"])
					
					temp_diff_num = game.temperature - game.prev_temperature
					carb_diff_num = game.carbon - game.prev_carbon
					budg_diff_num = game.budget - game.prev_budget
					supp_diff_num = game.support - game.prev_support
					
					feedback = choice["explanation"]
					feedback += t["num_impact_label"].format(
						temp_diff=f"{'+' if temp_diff_num>=0 else ''}{temp_diff_num:.2f}",
						carb_diff=f"{'+' if carb_diff_num>=0 else ''}{carb_diff_num:.1f}",
						budg_diff=f"{'+' if budg_diff_num>=0 else ''}{budg_diff_num:.1f}",
						supp_diff=f"{'+' if supp_diff_num>=0 else ''}{supp_diff_num:.1f}"
					)
					
					game.last_explanation = feedback

					# --- IMMEDIATE CRITICAL FAILURE CHECKS ---
					if game.temperature >= 2.0:
						game.game_over = True
						game.dynamic_fail_message = t["fail_temp"]
					elif game.support <= 20.0:
						game.game_over = True
						game.dynamic_fail_message = t["fail_support"]
					elif game.budget <= 0.0:
						game.game_over = True
						game.dynamic_fail_message = t["fail_budget"]

					# --- Update History Dataframe ---
					new_row = pd.DataFrame({
						"Round": [game.round + 1],
						"Temperature": [game.temperature],
						"Carbon": [game.carbon],
						"Budget": [game.budget],
						"Support": [game.support]
					})
					game.history = pd.concat([game.history, new_row], ignore_index=True)

					if game.round >= current_mission["max_rounds"]:
						if current_mission["check_win"](game):
							if game.stage == len(STAGE_MISSIONS):
								game.game_won = True
							else:
								next_stage = game.stage + 1
								game.stage_clear_message = t["stage_clear"].format(title=current_mission['title'])
								game.setup_stage(next_stage, model)
						else:
							game.game_over = True
					else:
						game.round += 1

					st.rerun()

if __name__ == "__main__":
	main()