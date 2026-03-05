import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go


# ==========================================
# 1. LOAD THE TRAINED AI MODEL
# ==========================================
@st.cache_resource
def load_ai_model():
	try:
		return joblib.load("climate_ai_model.pkl")
	except FileNotFoundError:
		st.error("Model not found! Please run the training script first to generate 'climate_ai_model.pkl'.")
		return None


# ==========================================
# 2. STAGE MISSIONS & WIN CONDITIONS
# ==========================================
STAGE_MISSIONS = {
	1: {
		"title": "Stage 1: Land & Agriculture",
		"problem": "ASEAN's forests are disappearing, and agricultural runoff is high. Stabilize the land.",
		"goal_text": "Reduce Carbon Emissions to 160.0 Mt or lower AND keep Public Support above 50%.",
		"max_rounds": 3,
		"check_win": lambda state: state.carbon <= 160.0 and state.support > 50.0,  # CHANGED TO 160.0
		"fail_message": "You failed to lower emissions enough, or you angered the public too much!"
	},
	2: {
		"title": "Stage 2: Urban Transportation",
		"problem": "Traffic congestion and fossil-fuel vehicles are choking ASEAN cities with smog.",
		"goal_text": "Keep the Budget above $300M AND ensure Public Support is exactly or above 60%.",
		"max_rounds": 2,
		"check_win": lambda state: state.budget >= 300.0 and state.support >= 60.0,
		"fail_message": "You either bankrupted the city or the citizens protested your transit policies!"
	},
	3: {
		"title": "Stage 3: The Energy Transition",
		"problem": "The national energy grid relies heavily on coal. It is time to transition to renewables.",
		"goal_text": "Keep Global Temperature at or below 1.5°C.",
		"max_rounds": 2,
		"check_win": lambda state: state.temperature <= 1.5,
		"fail_message": "Global temperatures exceeded the 1.5°C threshold. The energy grid failed the climate."
	}
}


# ==========================================
# 3. CORE ENGINE & STATE MANAGEMENT
# ==========================================
class GameState:
	def __init__(self, model):
		self.game_over = False
		self.game_won = False
		self.last_explanation = "Welcome to the Climate Simulator. Read your Stage Mission carefully!"
		self.stage_clear_message = ""

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

	state.temperature = round(predictions[0], 2)
	state.carbon = round(predictions[1], 1)
	state.budget = round(predictions[2], 1)
	state.support = round(predictions[3], 1)


# ==========================================
# 4. DECISION DATA
# ==========================================
CHOICES = {
	1: {
		1: [
			{"label": "🌲 Implement Strict Logging Bans",
			 "hint": "Effective at preserving sinks, but slightly raises taxes.",
			 "effects": {"deforestation_rate": -30, "carbon_tax_level": +5},
			 "explanation": "Banning logging reduced deforestation but required budget enforcement."},
			{"label": "🤝 Community Forest Management",
			 "hint": "Cheaper and boosts support, but slower emissions impact.",
			 "effects": {"deforestation_rate": -15, "support": +10, "budget": -10},
			 "explanation": "Empowering communities led to sustainable logging practices."}
		],
		2: [
			{"label": "🐄 Implement a Meat Tax", "hint": "Reduces methane quickly, but causes public outrage.",
			 "effects": {"livestock_population": -25, "support": -15, "budget": +50},
			 "explanation": "Taxing meat dropped methane levels but sparked protests."},
			{"label": "🌱 Subsidize Plant-Based Alternatives", "hint": "Highly popular, but expensive for the budget.",
			 "effects": {"livestock_population": -10, "support": +15, "budget": -40},
			 "explanation": "Subsidies made plant-based meat accessible. The public loved it."}
		],
		3: [
			{"label": "🧪 Subsidize Eco-Fertilizers", "hint": "Improves agriculture and support, but costs money.",
			 "effects": {"fertilizer_use": -20, "support": +5, "budget": -30},
			 "explanation": "Changing practices lowered runoff, increasing public support."},
			{"label": "🚫 Ban Synthetic Fertilizers", "hint": "Massively cuts chemical use, but hurts crop yields.",
			 "effects": {"fertilizer_use": -40, "support": -20, "budget": 0},
			 "explanation": "The sudden ban dropped chemical emissions, but farmers protested."}
		]
	},
	2: {
		1: [
			{"label": "🚌 Massive Bus Deployment", "hint": "Cuts individual footprints, but increases urbanization.",
			 "effects": {"public_buses_deployed": +40, "car_pooling_rate": +10, "urbanization_rate": +5, "budget": -50},
			 "explanation": "Buses reduced footprints significantly. Urbanization increased."},
			{"label": "🚄 Build High-Speed Rail",
			 "hint": "Incredibly expensive, but creates a massive shift from fossil fuels.",
			 "effects": {"fossil_fuel_use": -15, "budget": -120, "support": +15},
			 "explanation": "The railway became a national pride, but costs were massive."}
		],
		2: [
			{"label": "🚗 Mandatory Carpool Lanes", "hint": "Free policy to drop emissions, but highly unpopular.",
			 "effects": {"car_pooling_rate": +30, "support": -15},
			 "explanation": "Emissions dropped, but forced commuting changes angered citizens."},
			{"label": "⚡ Subsidize Electric Vehicles (EVs)",
			 "hint": "Popular and reduces smog, but requires a large budget.",
			 "effects": {"fossil_fuel_use": -10, "air_pollution_control": +20, "support": +10, "budget": -60},
			 "explanation": "EV adoption soared, clearing up city smog."}
		]
	},
	3: {
		1: [
			{"label": "☀️ Build Mega Solar Farm", "hint": "Ultimate solution to cut fossil fuels, but drains budget.",
			 "effects": {"renewable_investment": +40, "fossil_fuel_use": -20, "budget": -100},
			 "explanation": "Solar infrastructure massively cut fossil fuel reliance."},
			{"label": "⚛️ Invest in Nuclear Energy", "hint": "Massive clean energy, but lowers public support.",
			 "effects": {"renewable_investment": +50, "fossil_fuel_use": -30, "support": -25, "budget": -80},
			 "explanation": "Nuclear power stabilized the grid, but sparked fear."}
		],
		2: [
			{"label": "💰 Implement Aggressive Carbon Tax",
			 "hint": "Floods budget with revenue, but causes intense backlash.",
			 "effects": {"carbon_tax_level": +50, "budget": +150, "support": -30},
			 "explanation": "The carbon tax deterred emissions, but the public is furious."},
			{"label": "🏭 Fund Carbon Capture Tech",
			 "hint": "Removes carbon without angering the public, but expensive.",
			 "effects": {"carbon_capture_tech": +40, "budget": -90, "support": +5},
			 "explanation": "The experimental tech successfully scrubbed carbon from the atmosphere."}
		]
	}
}


# ==========================================
# 5. STREAMLIT APP & UI
# ==========================================
def main():
	st.set_page_config(page_title="Climate Simulator", page_icon="🌍", layout="centered")
	model = load_ai_model()

	if model is None:
		return

	if 'game' not in st.session_state:
		st.session_state.game = GameState(model)

	game = st.session_state.game

	st.title("🌍 Climate Simulator (AI Powered)")

	# --- GAME OVER STATE ---
	if game.game_over:
		st.error(f"🚨 GAME OVER: {STAGE_MISSIONS[game.stage]['fail_message']}")
		if st.button("🔄 Restart Game", type="primary"):
			st.session_state.game = GameState(model)
			st.rerun()
		return

	# --- GAME WON STATE (NEW RADAR CHART) ---
	if game.game_won:
		st.success("🎉 YOU WIN! You have completed all stages and stabilized the ASEAN climate!")
		st.balloons()

		st.subheader("📊 Final Policy Report Card")
		st.write("Here is how your leadership balanced the key metrics:")

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

		st.plotly_chart(fig)

		if st.button("🔄 Play Again", type="primary"):
			st.session_state.game = GameState(model)
			st.rerun()
		return

	# --- MAIN DASHBOARD ---
	if game.stage_clear_message:
		st.success(game.stage_clear_message)

	current_mission = STAGE_MISSIONS[game.stage]

	with st.container(border=True):
		st.subheader(current_mission["title"])
		st.write(f"**Problem:** {current_mission['problem']}")
		st.info(f"🎯 **Stage Goal:** {current_mission['goal_text']}")

		progress_val = (game.round - 1) / current_mission["max_rounds"]
		st.progress(progress_val, text=f"Stage Progress (Round {game.round} of {current_mission['max_rounds']})")

		st.divider()
		col1, col2, col3, col4 = st.columns(4)

		temp_delta = round(game.temperature - game.prev_temperature, 2)
		carb_delta = round(game.carbon - game.prev_carbon, 1)
		budg_delta = round(game.budget - game.prev_budget, 1)
		supp_delta = round(game.support - game.prev_support, 1)

		col1.metric("Global Temp", f"{game.temperature}°C", f"{temp_delta}°C", delta_color="inverse")
		col2.metric("Carbon Emission", f"{game.carbon} Mt", f"{carb_delta} Mt", delta_color="inverse")
		col3.metric("Budget", f"${game.budget}M", f"${budg_delta}M", delta_color="normal")
		col4.metric("Public Support", f"{game.support}%", f"{supp_delta}%", delta_color="normal")

		# --- NEW: HISTORICAL TREND GRAPHS ---
		st.write("📈 **Stage Trends**")
		chart_col1, chart_col2 = st.columns(2)
		with chart_col1:
			st.caption("Temperature Tracking")

			st.line_chart(game.history.set_index("Round")["Temperature"], color="#ff4b4b")
		with chart_col2:
			st.caption("Budget Tracking")
			st.line_chart(game.history.set_index("Round")["Budget"], color="#00b4d8")

	st.success(f"**🔬 Scientific Feedback:**\n\n{game.last_explanation}")

	st.subheader("Choose Your Next Policy")
	current_choices = CHOICES.get(game.stage, {}).get(game.round, [])

	for idx, choice in enumerate(current_choices):
		with st.container(border=True):
			st.write(f"**{choice['label']}**")
			st.caption(f"💡 **Hint:** {choice['hint']}")

			if st.button("Implement Policy", key=f"choice_{game.stage}_{game.round}_{idx}"):
				game.stage_clear_message = ""
				run_ai_inference(game, model, choice["effects"])
				game.last_explanation = choice["explanation"]

				# --- NEW: Update History Dataframe ---
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
							game.stage_clear_message = f"✅ You successfully cleared {current_mission['title']}!"
							game.setup_stage(next_stage, model)
					else:
						game.game_over = True
				else:
					game.round += 1

				st.rerun()

	with st.expander("⚙️ View Under-the-Hood AI Features"):
		st.json(game.features)


if __name__ == "__main__":
	main()