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
		"title": "Stage 1: Protecting Our Forests & Food",
		"sdg": "🌱 **SDG 15: Life on Land** | 🌾 **SDG 2: Zero Hunger**",
		"problem": "Deforestation and harsh farming chemicals are hurting our land and animals. As a leader, you must protect nature while keeping people fed and happy.",
		"goal_text": "Lower Carbon Emissions to 160.0 Mt or lower AND keep Public Support above 50%.",
		"context": "Forests act as 'carbon sinks,' meaning they absorb massive amounts of CO2 from the air. When forests are cut down for agriculture or timber, that trapped carbon is released, making global warming worse. At the same time, harsh chemical fertilizers used in farming run off into rivers, polluting the water. However, abruptly stopping farming can lead to food shortages and angry citizens. You must find a balance between protecting nature and sustaining livelihoods.",
		"max_rounds": 3,
		"check_win": lambda state: state.carbon <= 160.0 and state.support > 50.0,
		"fail_message": "You failed to lower emissions enough, or you angered the public too much!"
	},
	2: {
		"title": "Stage 2: Green Cities & Smart Transit",
		"sdg": "🏙️ **SDG 11: Sustainable Cities** | 🏭 **SDG 9: Industry & Infrastructure**",
		"problem": "Our cities are filled with smog and traffic jams. You need to fix how people travel without going bankrupt!",
		"goal_text": "Keep the Budget above $300M AND ensure Public Support is exactly or above 60%.",
		"context": "Transportation is one of the largest sources of greenhouse gases globally. Traditional cars rely on fossil fuels, releasing carbon monoxide and smog that choke city air and harm public health. Shifting thousands of people onto public transit (like buses or trains) drastically reduces the 'carbon footprint' per person. However, building huge infrastructure like railways is incredibly expensive and takes years to complete. Can you afford to modernize the city?",
		"max_rounds": 2,
		"check_win": lambda state: state.budget >= 300.0 and state.support >= 60.0,
		"fail_message": "You either bankrupted the city or the citizens protested your transit policies!"
	},
	3: {
		"title": "Stage 3: The Energy Transition",
		"sdg": "⚡ **SDG 7: Affordable & Clean Energy** | 🌍 **SDG 13: Climate Action**",
		"problem": "The country runs on dirty coal power. You must upgrade the power grid before the planet gets too hot!",
		"goal_text": "Keep Global Temperature at or below 1.5°C.",
		"context": "For decades, humanity has burned fossil fuels (coal, oil, and gas) to generate electricity. This releases massive amounts of CO2, acting like a blanket trapping the sun's heat—causing Global Warming. A rise of more than 1.5°C will cause catastrophic sea-level rise and extreme weather. To stop this, we must transition to renewable energy sources like solar, wind, or nuclear power. But these transitions disrupt established industries and can cost billions.",
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
CHOICES = {
	1: {
		1: [
			{"label": "🚫 🌱 Option A: Total Ban on Logging",
			 "hint": "[SDG 15] Fast nature recovery, but requires expensive budget enforcement.",
			 "expected_impact": "🌳 Deforestation Drops Greatly | 💰 Budget Takes a Hit",
			 "effects": {"deforestation_rate": -30, "carbon_tax_level": +5, "carbon": -15.0, "temperature": -0.05},
			 "explanation": "Banning logging immediately stopped large-scale tree cutting. However, the government had to spend millions hiring forest rangers to enforce the ban!"},
			{"label": "🤝 🌾 Option B: Empower Local Communities",
			 "hint": "[SDG 2] Slower recovery, but cheaper and highly supported by locals.",
			 "expected_impact": "🌳 Deforestation Drops Slightly | 😊 Support Rises | 💰 Budget Takes Small Hit",
			 "effects": {"deforestation_rate": -15, "support": +10, "budget": -10, "carbon": -5.0, "temperature": -0.01},
			 "explanation": "Giving local indigenous groups the rights to manage their own forests led to sustainable, careful logging practices. The people love you for trusting them!"},
			{"label": "💣 🪓 Option C: Sell Forests to Logging Conglomerate",
			 "hint": "[SDG 15] Massive instant wealth, but nature is completely destroyed and citizens will riot.",
			 "expected_impact": "🌳 Deforestation Maxes Out | 😡 Support Plummets | 💰 Budget Skyrockets",
			 "effects": {"deforestation_rate": +50, "support": -85, "budget": +200, "carbon": +30.0, "temperature": +0.15},
			 "explanation": "You sold off the final state-protected lands. The country made hundreds of millions of dollars overnight, but the forests were clear-cut within weeks. Citizens have lost their jobs and homes, and the rioting has begun."}
		],
		2: [
			{"label": "🥩 🌾 Option A: Tax Meat Products", 
			 "hint": "[SDG 2] Creates a huge budget surplus, but causes major public protests.",
			 "expected_impact": "🐄 Methane Drops Fast | 😡 Support Plummets | 💰 Budget Increases Huge",
			 "effects": {"livestock_population": -25, "support": -15, "budget": +50, "carbon": -20.0, "temperature": -0.08},
			 "explanation": "Cows produce a lot of methane (a greenhouse gas 25x worse than carbon dioxide). Making meat expensive dropped emissions rapidly, but citizens protested in the streets over the cost of their food!"},
			{"label": "🧪 💡 Option B: Fund Fake-Meat Research", 
			 "hint": "[SDG 9] Very popular with citizens, but drains the national budget.",
			 "expected_impact": "🐄 Methane Drops Slightly | 😊 Support Increases Huge | 💰 Budget Drops Fast",
			 "effects": {"livestock_population": -10, "support": +15, "budget": -40, "carbon": -8.0, "temperature": -0.03},
			 "explanation": "By putting government money into plant-based meat startups, fake meat became cheaper than real meat. People loved the tasty burgers, but the scientific grants drained government funds."}
		],
		3: [
			{"label": "🌱 🌊 Option A: Subsidize Safe Fertilizers", 
			 "hint": "[SDG 14] Improves soil safely but costs money.",
			 "expected_impact": "🌾 Chemical Runoff Drops | 😊 Support Rises Slightly | 💰 Budget Drops",
			 "effects": {"fertilizer_use": -20, "support": +5, "budget": -30, "carbon": -5.0},
			 "explanation": "Paying farmers extra to use natural, organic fertilizers stopped the rivers from being polluted with chemicals. It was expensive, but the farmers appreciated the help."},
			{"label": "⚠️ 🌊 Option B: Ban Toxic Chemicals Instantly", 
			 "hint": "[SDG 14] Stops pollution immediately, but causes farmers to lose money and protest.",
			 "expected_impact": "🌾 Chemical Runoff Drops Massively | 😡 Support Plummets | 💰 Budget Unaffected",
			 "effects": {"fertilizer_use": -40, "support": -20, "budget": 0, "carbon": -10.0, "temperature": -0.02},
			 "explanation": "An instant ban on synthetic nitrogen fertilizers completely fixed the water pollution. Unfortunately, crop sizes shrank drastically, and furious farmers are demanding your resignation!"}
		]
	},
	2: {
		1: [
			{"label": "🚌 🏙️ Option A: Buy Thousands of Electric Buses", 
			 "hint": "[SDG 11] Greatly lowers footprints, but increases city crowding/urbanization.",
			 "expected_impact": "🚘 Traffic Drops | 🏙️ Crowding Increases | 💰 Budget Drops",
			 "effects": {"public_buses_deployed": +40, "car_pooling_rate": +10, "urbanization_rate": +5, "budget": -50, "carbon": -25.0, "temperature": -0.10},
			 "explanation": "The massive fleet of new electric buses took thousands of cars off the road. However, because transit became so easy, more people moved from the countryside into the city, increasing crowding."},
			{"label": "🚄 🏭 Option B: Build a Mega High-Speed Railway",
			 "hint": "[SDG 9] Massive national pride and shift from cars, but costs a fortune.",
			 "expected_impact": "⛽ Fossil Fuel Use Drops | 😊 Support Increases Huge | 💰 Budget Dropped Massively",
			 "effects": {"fossil_fuel_use": -15, "budget": -120, "support": +15, "carbon": -15.0, "temperature": -0.05},
			 "explanation": "The bullet train project was an incredible feat of engineering. Citizens are incredibly proud to ride it instead of flying or driving, but the construction cost almost bankrupted the state!"},
			{"label": "💣 🚗 Option C: Abolish Public Transit & Build 10-Lane Highways",
			 "hint": "[SDG 11] Solves public transit budget issues by eliminating them, but causes unbreathable smog.",
			 "expected_impact": "🚘 Traffic Skyrockets | 🏙️ Crowding Drops | 💰 Budget Increases",
			 "effects": {"public_buses_deployed": -50, "car_pooling_rate": -20, "budget": +100, "fossil_fuel_use": +40, "carbon": +45.0, "temperature": +0.20},
			 "explanation": "You shut down all bus and rail services, forcing everyone into cars. While the government saved tons of money on maintenance, the city became a massive traffic jam. The air quality index hit dangerous levels immediately."}
		],
		2: [
			{"label": "🛑 🏙️ Option A: Force Mandatory Carpooling", 
			 "hint": "[SDG 11] Costs $0, drastically cuts emissions, but citizens HATE being forced.",
			 "expected_impact": "🚘 Traffic Drops Huge | 😡 Support Plummets | 💰 Budget Unaffected",
			 "effects": {"car_pooling_rate": +30, "support": -15, "carbon": -20.0, "temperature": -0.06},
			 "explanation": "You passed a law making it illegal to drive alone. The city air cleared up overnight and it cost the government nothing, but annoyed commuters are furious at losing their freedom."},
			{"label": "⚡ 🌍 Option B: Subsidize Electric Cars for Everyone",
			 "hint": "[SDG 13] Clears the air and people love it, but takes a huge chunk of your budget.",
			 "expected_impact": "⛽ Fossil Fuel Use Drops | 😊 Support Increases | 💰 Budget Drops Greatly",
			 "effects": {"fossil_fuel_use": -10, "air_pollution_control": +20, "support": +10, "budget": -60, "carbon": -35.0, "temperature": -0.12},
			 "explanation": "By paying for half the cost of electric vehicles (EVs), practically everyone traded in their gas guzzlers. The smog is gone and people love their new cars, but it was an extremely expensive policy."}
		]
	},
	3: {
		1: [
			{"label": "☀️ ⚡ Option A: Build the World's Largest Solar Farm", 
			 "hint": "[SDG 7] Safe and effective, but extremely expensive.",
			 "expected_impact": "⛽ Fossil Fuel Use Drops Greatly | 💰 Budget Drops Massively",
			 "effects": {"renewable_investment": +40, "fossil_fuel_use": -20, "budget": -100, "carbon": -40.0, "temperature": -0.15},
			 "explanation": "Miles and miles of solar panels now collect the sun's energy, allowing you to shut down several dirty coal plants. The air is cleaner, but installing all those panels cost billions."},
			{"label": "⚛️ ⚡ Option B: Build a Nuclear Power Plant", 
			 "hint": "[SDG 7] Produces massive amounts of clean power, but scares the public.",
			 "expected_impact": "⛽ Fossil Fuel Use Drops Massively | 😡 Support Plummets | 💰 Budget Drops Greatly",
			 "effects": {"renewable_investment": +50, "fossil_fuel_use": -30, "support": -25, "budget": -80, "carbon": -50.0, "temperature": -0.18},
			 "explanation": "Nuclear fission provides incredible amounts of energy with absolutely zero carbon emissions. Unfortunately, citizens are terrified of a potential meltdown and are protesting the reactor's construction."},
			{"label": "💣 🏭 Option C: Subsidize Unregulated Coal Mining",
			 "hint": "[SDG 13] The cheapest, fastest way to get electricity, but guarantees catastrophic warming.",
			 "expected_impact": "☁️ Carbon Skyrockets | 😊 Support Rises | 💰 Budget Increases",
			 "effects": {"fossil_fuel_use": +50, "renewable_investment": -30, "budget": +50, "carbon": +60.0, "temperature": +0.30},
			 "explanation": "You doubled down on dirty coal because it was cheap. The economy saw a short boom, but the massive surge in carbon emissions pushed the global temperature past the point of no return!"}
		],
		2: [
			{"label": "💰 🌍 Option A: Charge Polluters a Carbon Tax",
			 "hint": "[SDG 13] Makes the government extremely rich, but businesses and citizens will be outraged.",
			 "expected_impact": "💵 Budget Skyrockets | 😡 Support Plummets Massively",
			 "effects": {"carbon_tax_level": +50, "budget": +150, "support": -30, "carbon": -25.0, "temperature": -0.05},
			 "explanation": "By forcing companies to pay heavily for every ton of CO2 they emit, they rapidly chose to go green. The government made a fortune in tax revenue, but the companies passed the costs onto consumers, making everything more expensive. People are furious!"},
			{"label": "🏭 💡 Option B: Fund Experimental Carbon Vacuums",
			 "hint": "[SDG 9] Futuristic tech that sucks carbon out of the air—people love it, but it costs millions.",
			 "expected_impact": "☁️ Carbon Sucked From Air | 😊 Support Rises Slightly | 💰 Budget Drops Massively",
			 "effects": {"carbon_capture_tech": +40, "budget": -90, "support": +5, "carbon": -80.0, "temperature": -0.25},
			 "explanation": "You funded giant Direct Air Capture (DAC) fans that literally suck carbon dioxide out of the sky and bury it underground. It feels like science fiction and the citizens love it, but it is incredibly expensive to run."}
		]
	}
}


# ==========================================
# 5. STREAMLIT APP & UI
# ==========================================
def main():
	# NEW: Use wide layout for PC optimization
	st.set_page_config(page_title="Climate Simulator", page_icon="🌍", layout="wide")
	model = load_ai_model()

	if model is None:
		return

	if 'game' not in st.session_state:
		st.session_state.game = GameState(model)

	game = st.session_state.game

	st.title("🌍 Student Climate Simulator (AI Powered)")
	# --- GAME OVER STATE ---
	if game.game_over:
		fail_msg = getattr(game, 'dynamic_fail_message', "") or STAGE_MISSIONS[game.stage]['fail_message']
		st.error(f"🚨 GOAL NOT MET: {fail_msg}")
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

		st.plotly_chart(fig, use_container_width=True)

		if st.button("🔄 Play Again", type="primary"):
			st.session_state.game = GameState(model)
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

	metric_col1.metric("Global Temp", f"{game.temperature}°C", f"{temp_delta}°C", delta_color="inverse", help="Global average temperature rise since pre-industrial levels. Exceeding 2.0°C causes catastrophic tipping points (Instant Game Over).")
	metric_col2.metric("Carbon Emission", f"{game.carbon} Mt", f"{carb_delta} Mt", delta_color="inverse", help="Megatons (Mt) of CO2 released into the atmosphere per year.")
	metric_col3.metric("Budget", f"${game.budget}M", f"${budg_delta}M", delta_color="normal", help="Millions of dollars left in the government discretionary budget. Hitting $0 means bankruptcy (Instant Game Over).")
	metric_col4.metric("Public Support", f"{game.support}%", f"{supp_delta}%", delta_color="normal", help="Percentage of citizens who currently approve of your leadership. Dropping below 20% causes government overthrow (Instant Game Over).")

	# --- UNIFIED 3-COLUMN DASHBOARD ---
	# Left (Education 25%) | Center (Data 45%) | Right (Actions 30%)
	left_col, center_col, right_col = st.columns([1, 1.8, 1.2], gap="small")

	with left_col:
		st.subheader(f"🎓 {current_mission['title']}")
		st.markdown(current_mission["sdg"])
		
		# Current Mission Overview
		with st.container(border=True):
			st.markdown(f"**Your Mission:** {current_mission['problem']}")
			st.info(f"🎯 **Win Goal:** {current_mission['goal_text']}")

			progress_val = (game.round - 1) / current_mission["max_rounds"]
			st.progress(progress_val, text=f"Stage Progress (Round {game.round} of {current_mission['max_rounds']})")
			
		# Education Hub Context
		with st.container(border=True):
			st.subheader(f"About This Stage")
			st.markdown(f"{current_mission['context']}")
			
		with st.expander("⚙️ What is happening under the hood? (AI Models)"):
			st.markdown(
				"When you make a policy choice, it alters hidden parameters of our country (like urbanization or fertilizer use). "
				"Those numbers are fed into a **Machine Learning AI Model** (Random Forest Regressor) which uses past scientific data to instantly predict the carbon emissions, temperature, budget, and public support! "
				"Here is the raw data going into the AI right now:"
			)
			st.json(game.features)

	with center_col:
		st.subheader("📈 Data & Trends")
		st.success(f"**🧪 Scientific Feedback (Result of Last Action):**\n\n{game.last_explanation}")
		
		with st.container(border=True):
			st.caption("Temperature Tracking")
			st.line_chart(game.history.set_index("Round")["Temperature"], color="#ff4b4b", height=130)
			
		with st.container(border=True):
			st.caption("Budget Tracking")
			st.line_chart(game.history.set_index("Round")["Budget"], color="#00b4d8", height=130)

	with right_col:
		st.subheader("⚡ Action Center")
		st.write("Choose Your Next Policy:")
		
		current_choices = CHOICES.get(game.stage, {}).get(game.round, [])

		for idx, choice in enumerate(current_choices):
			with st.container(border=True):
				# Educational details before they click
				st.markdown(f"**{choice['label']}**")
				st.caption(f"💡 *Hint: {choice['hint']}*")
				
				# --- NEW: Run Counterfactual AI Prediction ---
				p_temp, p_carb, p_budg, p_supp = predict_policy_impact(game, model, choice["effects"])
				
				# Dynamic Expected Impact
				st.markdown(f"📊 **AI Prediction:** Temp: ``{'+' if p_temp>=0 else ''}{p_temp:.2f}°C`` | "
							f"Carbon: ``{'+' if p_carb>=0 else ''}{p_carb:.1f} Mt`` | "
							f"Budget: ``{'+' if p_budg>=0 else ''}${p_budg:.1f}M`` | "
							f"Support: ``{'+' if p_supp>=0 else ''}{p_supp:.1f}%``")

				if st.button("Implement Policy", key=f"choice_{game.stage}_{game.round}_{idx}", use_container_width=True):
					game.stage_clear_message = ""
					run_ai_inference(game, model, choice["effects"])
					
					temp_diff = game.temperature - game.prev_temperature
					carb_diff = game.carbon - game.prev_carbon
					budg_diff = game.budget - game.prev_budget
					supp_diff = game.support - game.prev_support
					
					feedback = choice["explanation"]
					feedback += f"\n\n**Numerical Impact:** Temp: {'+' if temp_diff>=0 else ''}{temp_diff:.2f}°C | Carbon: {'+' if carb_diff>=0 else ''}{carb_diff:.1f} Mt | Budget: {'+' if budg_diff>=0 else ''}${budg_diff:.1f}M | Support: {'+' if supp_diff>=0 else ''}{supp_diff:.1f}%"
					
					game.last_explanation = feedback

					# --- IMMEDIATE CRITICAL FAILURE CHECKS ---
					if game.temperature >= 2.0:
						game.game_over = True
						game.dynamic_fail_message = "🔥 Global Temperature met or exceeded 2.0°C! The climate has reached a tipping point, leading to catastrophic and irreversible environmental damage."
					elif game.support <= 20.0:
						game.game_over = True
						game.dynamic_fail_message = "😡 Public Support dropped below 20%. The citizens have rioted to overthrow your government!"
					elif game.budget <= 0.0:
						game.game_over = True
						game.dynamic_fail_message = "💸 The National Budget has hit zero. The country has defaulted on its debt and the government cannot function!"

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
								game.stage_clear_message = f"✅ You successfully cleared {current_mission['title']}! You met all the requirements."
								game.setup_stage(next_stage, model)
						else:
							game.game_over = True
					else:
						game.round += 1

					st.rerun()


if __name__ == "__main__":
	main()