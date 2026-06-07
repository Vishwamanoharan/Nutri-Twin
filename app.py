"""
Streamlit frontend for Nutrition AI backend.
Backend: http://127.0.0.1:8000
Endpoints: GET /health, POST /plan/day, POST /plan/week
Run: streamlit run app.py
"""

import requests
import streamlit as st

# ---------- CONSTANTS ----------
BASE_URL = "http://127.0.0.1:8001"
API_TIMEOUT = 60


# ---------- SIDEBAR – USER INPUT FORM ----------
def build_user_payload():
    """Build UserInput-shaped dict from sidebar widgets."""
    payload = {
        "age": int(st.session_state.get("age", 30)),
        "gender": st.session_state.get("gender", "Female").lower(),
        "height": float(st.session_state.get("height", 162)),
        "weight": float(st.session_state.get("weight", 68)),
        "activity_level": st.session_state.get("activity_level", "light"),
        "goal": st.session_state.get("goal", "fat_loss"),
    }
    if st.session_state.get("blood_pressure"):
        payload["blood_pressure"] = "high"
    if st.session_state.get("blood_sugar"):
        payload["blood_sugar"] = "high"
    if st.session_state.get("pcos") is not None:
        payload["pcos"] = st.session_state["pcos"]
    if st.session_state.get("thyroid") is not None:
        payload["thyroid"] = st.session_state["thyroid"]
    if st.session_state.get("digestive_issues"):
        payload["digestive_issues"] = "ibs"
    allergies = st.session_state.get("allergies") or []
    if allergies:
        payload["allergies"] = list(allergies)
    culture = (st.session_state.get("culture") or "").strip()
    if culture:
        payload["culture"] = culture
    region = (st.session_state.get("region") or "").strip()
    if region:
        payload["region"] = region
    state = (st.session_state.get("state") or "").strip()
    if state:
        payload["state"] = state
    return payload


def render_sidebar():
    st.sidebar.header("User profile")
    st.sidebar.subheader("Basic info")
    st.sidebar.number_input("Age", min_value=1, max_value=120, value=30, key="age")
    st.sidebar.selectbox("Gender", ["Male", "Female"], key="gender")
    st.sidebar.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=162.0, key="height")
    st.sidebar.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=68.0, key="weight")

    st.sidebar.subheader("Lifestyle")
    st.sidebar.selectbox(
        "Activity level",
        ["sedentary", "light", "moderate", "active"],
        key="activity_level",
    )
    st.sidebar.selectbox(
        "Goal",
        ["fat_loss", "maintenance", "muscle_gain"],
        key="goal",
    )

    st.sidebar.subheader("Health conditions")
    st.sidebar.checkbox("High blood pressure", key="blood_pressure")
    st.sidebar.checkbox("Diabetes", key="blood_sugar")
    st.sidebar.checkbox("PCOS", key="pcos")
    st.sidebar.checkbox("Thyroid", key="thyroid")
    st.sidebar.checkbox("Digestive issues (IBS)", key="digestive_issues")

    st.sidebar.subheader("Allergies")
    st.sidebar.multiselect(
        "Allergies",
        ["peanut", "lactose", "gluten", "shellfish", "egg", "soy", "tree_nut"],
        key="allergies",
    )

    st.sidebar.subheader("Culture & region")
    st.sidebar.text_input("Culture", value="Indian", key="culture")
    st.sidebar.selectbox(
        "Region",
        ["North", "South", "East", "West", ""],
        key="region",
    )
    st.sidebar.text_input("State", key="state")


# ---------- API CALLS ----------
def fetch_day_plan(payload):
    with st.spinner("Generating today's plan..."):
        r = requests.post(
            f"{BASE_URL}/plan/day",
            json=payload,
            timeout=API_TIMEOUT,
        )
    return r


def fetch_week_plan(payload):
    with st.spinner("Generating weekly plan..."):
        r = requests.post(
            f"{BASE_URL}/plan/week",
            json=payload,
            timeout=API_TIMEOUT,
        )
    return r


def _json_safe(obj):
    """Convert dict/list/values to JSON-serializable types (e.g. numpy -> float)."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()  # numpy scalar
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return obj


def fetch_plan_with_feedback(payload, feedback: dict):
    """POST /plan/feedback with user profile + meal tracking (eaten/skipped)."""
    body = {
        "user_input": _json_safe(payload),
        "feedback": _json_safe(feedback),
    }
    with st.spinner("Generating plan with your feedback..."):
        r = requests.post(
            f"{BASE_URL}/plan/feedback",
            json=body,
            timeout=API_TIMEOUT,
        )
    return r


# ---------- DISPLAY DAILY PLAN ----------
def render_meal_card(meal_label: str, meal_data: dict):
    if not meal_data:
        st.markdown(f"**{meal_label}** — No data")
        return
    name = meal_data.get("dish_name", "—")
    st.markdown(f"**{meal_label}**")
    st.markdown(f"**Dish:** {name}")
    st.markdown(f"Calories: {meal_data.get('calories', '—')}")
    st.markdown(f"Protein: {meal_data.get('protein', '—')} g")
    st.markdown(f"Carbs: {meal_data.get('carbs', '—')} g")
    st.markdown(f"Fats: {meal_data.get('fats', '—')} g")
    st.markdown(f"Fibre: {meal_data.get('fibre', '—')} g")


def render_daily_plan(response_data: dict):
    plan = response_data.get("plan") or {}
    col1, col2, col3 = st.columns(3)
    with col1:
        render_meal_card("Breakfast", plan.get("breakfast") or {})
    with col2:
        render_meal_card("Lunch", plan.get("lunch") or {})
    with col3:
        render_meal_card("Dinner", plan.get("dinner") or {})

    totals = plan.get("totals") or {}
    st.subheader("Totals")
    st.markdown(
        f"**Calories:** {totals.get('calories', '—')} | "
        f"**Protein:** {totals.get('protein', '—')} g | "
        f"**Carbs:** {totals.get('carbs', '—')} g | "
        f"**Fats:** {totals.get('fats', '—')} g | "
        f"**Fibre:** {totals.get('fibre', '—')} g"
    )

    explanation = response_data.get("explanation", "")
    if explanation:
        with st.expander("AI explanation"):
            st.write(explanation)


# ---------- DISPLAY WEEKLY PLAN ----------
def render_weekly_plan(response_data: dict):
    week_plan = response_data.get("week_plan") or {}
    summary = response_data.get("weekly_summary") or {}

    st.subheader("Weekly summary")
    st.markdown(
        f"**Avg calories:** {summary.get('avg_calories', '—')} | "
        f"**Avg protein:** {summary.get('avg_protein', '—')} g | "
        f"**Avg fibre:** {summary.get('avg_fibre', '—')} g | "
        f"**Unique dishes:** {summary.get('unique_dishes', '—')}"
    )

    tab_names = [f"Day {i}" for i in range(1, 8)]
    tabs = st.tabs(tab_names)
    for i, tab in enumerate(tabs):
        day_key = f"day_{i + 1}"
        day_plan = week_plan.get(day_key) or {}
        with tab:
            c1, c2, c3 = st.columns(3)
            with c1:
                render_meal_card("Breakfast", day_plan.get("breakfast") or {})
            with c2:
                render_meal_card("Lunch", day_plan.get("lunch") or {})
            with c3:
                render_meal_card("Dinner", day_plan.get("dinner") or {})


# ---------- MAIN ----------
def main():
    st.set_page_config(page_title="Nutrition AI", layout="wide")
    st.title("Nutrition AI")

    render_sidebar()

    if "last_daily" not in st.session_state:
        st.session_state["last_daily"] = None
    if "last_weekly" not in st.session_state:
        st.session_state["last_weekly"] = None

    payload = build_user_payload()

    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("Generate Today's Plan"):
            if payload.get("age", 0) < 1 or payload.get("height", 0) <= 0 or payload.get("weight", 0) <= 0:
                st.error("Please set valid Age, Height, and Weight in the sidebar.")
            else:
                try:
                    r = fetch_day_plan(payload)
                    if r.status_code == 200:
                        st.session_state["last_daily"] = r.json()
                        st.session_state["last_weekly"] = None
                    else:
                        st.error(f"API error: {r.status_code} — {r.text[:200]}")
                except requests.RequestException as e:
                    st.error(f"Request failed: {e}")
    with col_btn2:
        if st.button("Generate Weekly Plan"):
            if payload.get("age", 0) < 1 or payload.get("height", 0) <= 0 or payload.get("weight", 0) <= 0:
                st.error("Please set valid Age, Height, and Weight in the sidebar.")
            else:
                try:
                    r = fetch_week_plan(payload)
                    if r.status_code == 200:
                        st.session_state["last_weekly"] = r.json()
                        st.session_state["last_daily"] = None
                    else:
                        st.error(f"API error: {r.status_code} — {r.text[:200]}")
                except requests.RequestException as e:
                    st.error(f"Request failed: {e}")

    if st.session_state["last_daily"]:
        st.header("Today's plan")
        render_daily_plan(st.session_state["last_daily"])

        # ---------- MEAL TRACKING (eaten / skipped) ----------
        last_plan = st.session_state["last_daily"].get("plan") or {}
        if last_plan.get("breakfast") or last_plan.get("lunch") or last_plan.get("dinner"):
            st.subheader("Track your meals")
            st.caption("Did you eat each meal? This helps the next plan adapt.")
            if "track_breakfast" not in st.session_state:
                st.session_state["track_breakfast"] = "eaten"
            if "track_lunch" not in st.session_state:
                st.session_state["track_lunch"] = "eaten"
            if "track_dinner" not in st.session_state:
                st.session_state["track_dinner"] = "eaten"

            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                st.radio("Breakfast", ["eaten", "skipped"], key="track_breakfast", horizontal=True)
            with tc2:
                st.radio("Lunch", ["eaten", "skipped"], key="track_lunch", horizontal=True)
            with tc3:
                st.radio("Dinner", ["eaten", "skipped"], key="track_dinner", horizontal=True)

            st.subheader("How did you feel?")
            st.caption("Optional: help personalize the next plan.")
            if "fb_hunger" not in st.session_state:
                st.session_state["fb_hunger"] = 5
            if "fb_energy" not in st.session_state:
                st.session_state["fb_energy"] = 6
            if "fb_weight_change" not in st.session_state:
                st.session_state["fb_weight_change"] = 0.0
            if "fb_suggestions" not in st.session_state:
                st.session_state["fb_suggestions"] = ""

            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.slider("Hunger (1–10)", min_value=1, max_value=10, value=st.session_state["fb_hunger"], key="fb_hunger")
            with fc2:
                st.slider("Energy (1–10)", min_value=1, max_value=10, value=st.session_state["fb_energy"], key="fb_energy")
            with fc3:
                st.number_input("Weight change (kg)", value=float(st.session_state["fb_weight_change"]), step=0.1, key="fb_weight_change")

            st.text_input("Suggestions (optional)", key="fb_suggestions", placeholder="e.g. lighter lunch, more protein")

            if st.button("Generate next plan (with feedback)"):
                if payload.get("age", 0) < 1 or payload.get("height", 0) <= 0 or payload.get("weight", 0) <= 0:
                    st.error("Please set valid Age, Height, and Weight in the sidebar.")
                else:
                    try:
                        feedback = {
                            "yesterday_plan": last_plan,
                            "hunger": st.session_state.get("fb_hunger"),
                            "energy": st.session_state.get("fb_energy"),
                            "weight_change": st.session_state.get("fb_weight_change"),
                            "meal_feedback": {
                                "breakfast": st.session_state["track_breakfast"],
                                "lunch": st.session_state["track_lunch"],
                                "dinner": st.session_state["track_dinner"],
                            },
                            "suggestions": (st.session_state.get("fb_suggestions") or "").strip() or None,
                        }
                        r = fetch_plan_with_feedback(payload, feedback)
                        if r.status_code == 200:
                            st.session_state["last_daily"] = r.json()
                            st.session_state["last_weekly"] = None
                            if hasattr(st, "rerun"):
                                st.rerun()
                            else:
                                st.experimental_rerun()
                        else:
                            st.error(f"API error: {r.status_code} — {r.text[:500]}")
                    except requests.RequestException as e:
                        st.error(f"Request failed: {e}")

    if st.session_state["last_weekly"]:
        st.header("Weekly plan")
        render_weekly_plan(st.session_state["last_weekly"])


if __name__ == "__main__":
    main()
