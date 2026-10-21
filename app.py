
import streamlit as st

from config import (
    APP_NAME,
    APP_TAGLINE,
    SUPPORTED_BUDGETS,
    SUPPORTED_PACES,
    SUPPORTED_PARTIES,
)
from services.ai_service import generate_json
from utils.pdf_export import generate_trip_pdf
from services.ai_service import generate_json

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ TripPilot")
st.caption(APP_TAGLINE)

st.markdown("### Plan your next adventure")
st.write("Tell us your preferences, and let AI help plan your trip.")

with st.form("trip_form"):
    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input(
            "Destination",
            placeholder="e.g. Jaipur, Manali, Goa",
        )

        days = st.number_input(
            "Trip duration (days)",
            min_value=1,
            max_value=30,
            value=3,
            step=1,
        )

        budget = st.selectbox(
            "Travel budget",
            SUPPORTED_BUDGETS,
        )

        total_budget = st.number_input(
            "Total budget (₹)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000,
        )

    with col2:
        travel_party = st.selectbox(
            "Who is travelling?",
            SUPPORTED_PARTIES,
        )

        pace = st.selectbox(
            "Travel pace",
            SUPPORTED_PACES,
        )

        interests = st.multiselect(
            "Your interests",
            [
                "Nature",
                "History",
                "Adventure",
                "Food",
                "Shopping",
                "Photography",
                "Culture",
                "Relaxation",
            ],
            default=["Culture", "Food"],
        )

        additional_notes = st.text_area(
            "Additional preferences",
            placeholder="e.g. vegetarian food, famous local places...",
        )

    submitted = st.form_submit_button(
        "✨ Generate My Trip",
        use_container_width=True,
    )


if submitted:
    if not destination.strip():
        st.error("Please enter a destination.")
    else:
       
      prompt = f"""
Create a practical travel itinerary in valid JSON.

Destination: {destination}
Duration: {days} days
Travel style: {budget}
Total budget in INR: {total_budget}
Travel party: {travel_party}
Travel pace: {pace}
Interests: {", ".join(interests) if interests else "General sightseeing"}
Additional preferences: {additional_notes or "None"}

Return a JSON object with this structure:
{{
  "destination": "{destination}",
  "days": {days},
  "overview": "Short trip overview",
  "estimated_total_cost": 5000,
  "budget_notes": "Brief budget explanation",
  "itinerary": [
    {{
      "day": 1,
      "title": "Day title",
      "activities": [
        {{
          "time": "09:00 AM",
          "name": "Activity name",
          "description": "Short description",
          "estimated_cost": 500,
          "location": "Place name"
        }}
      ]
    }}
  ],
  "travel_tips": ["Tip 1", "Tip 2"]
}}

IMPORTANT PLANNING RULES:
1. Include exactly {days} itinerary days.
2. Group attractions in the same or nearby areas on the same day.
3. Arrange activities in a logical geographic order to reduce unnecessary travel.
4. Include realistic time slots and reasonable travel time between activities.
5. Avoid scheduling distant attractions back-to-back.
6. Consider opening hours and avoid unrealistic schedules.
7. Match activities to the selected interests, travel pace, and travel party.
8. Keep estimated total cost within INR {total_budget} when practical.
9. Ensure estimated_total_cost is the sum of estimated expenses,
   including activities and other stated travel expenses.
10. Use realistic suggestions and approximate costs.
11. Do not invent exact distances, coordinates, live prices,
    opening hours, or availability.
12. Make each day's activities distinct and avoid repetition.
13. If the budget is insufficient, explain this in budget_notes.

Return valid JSON only. Do not include Markdown.
"""



    with st.spinner("Planning your trip with AI..."):
            try:
                result = generate_json(prompt)
                st.session_state["trip_result"] = result
                st.session_state["trip_budget"] = total_budget
            except Exception as exc:
                st.error(f"Could not generate your trip: {exc}")


result = st.session_state.get("trip_result")

if result:
    st.divider()
    st.header(f"🌍 {result.get('destination', 'Your Trip')}")

    overview = result.get("overview")
    if overview:
        st.write(overview)

    estimated_cost = float(result.get("estimated_total_cost", 0))
    current_budget = st.session_state.get("trip_budget", 0)
    remaining = current_budget - estimated_cost

    col1, col2, col3 = st.columns(3)

    col1.metric("Your Budget", f"₹{current_budget:,.0f}")
    col2.metric("Estimated Cost", f"₹{estimated_cost:,.0f}")
    col3.metric("Remaining", f"₹{remaining:,.0f}")

    if remaining < 0:
        st.warning("This itinerary may exceed your budget.")
    else:
        st.progress(
            min(estimated_cost / current_budget, 1.0)
            if current_budget > 0
            else 0.0
        )

    budget_notes = result.get("budget_notes")
    if budget_notes:
        st.info(budget_notes)

    st.subheader("🗓️ Your Day-wise Itinerary")

    itinerary = result.get("itinerary", [])

    for day_plan in itinerary:
        day_number = day_plan.get("day", "?")
        day_title = day_plan.get("title", "Explore")

        with st.expander(
            f"Day {day_number}: {day_title}",
            expanded=True,
        ):
            activities = day_plan.get("activities", [])

            for activity in activities:
                st.markdown(
                    f"**{activity.get('time', 'Flexible')} — "
                    f"{activity.get('name', 'Activity')}**"
                )

                description = activity.get("description")
                if description:
                    st.write(description)

                location = activity.get("location")
                if location:
                    st.caption(f"📍 {location}")

                cost = activity.get("estimated_cost", 0)
                st.write(f"Estimated cost: ₹{float(cost):,.0f}")
                st.divider()

    tips = result.get("travel_tips", [])
    if tips:
        st.subheader("💡 Travel Tips")
        for tip in tips:
            st.write(f"- {tip}")

    st.caption(
        "AI-generated estimates are approximate. "
        "Verify prices, opening hours, and travel details before booking."
    )
 
# --- Trip History ---
from services.storage import save_trip, get_all_trips

st.divider()
st.header("📚 Trip History")

if st.session_state.get("trip_result"):
    if st.button("💾 Save Current Trip"):
        trip_to_save = {
            "destination": st.session_state["trip_result"].get(
                "destination", "Unknown"
            ),
            "days": st.session_state["trip_result"].get("days", 1),
            "budget": st.session_state.get("trip_budget", 0),
            "itinerary": st.session_state["trip_result"],
        }

        save_trip(trip_to_save)
        st.success("Trip saved successfully!")

saved_trips = get_all_trips()

if saved_trips:
    for trip in reversed(saved_trips):
        with st.expander(
            f"🌍 {trip.get('destination', 'Unknown')} — "
            f"{trip.get('days', 1)} days"
        ):
            st.write(f"Budget: ₹{trip.get('budget', 0):,.0f}")

            if st.button("Open Trip", key=f"open_{trip['id']}"):
                st.session_state["trip_result"] = trip.get("itinerary", {})
                st.session_state["trip_budget"] = trip.get("budget", 0)
                st.rerun()
else:
    st.info("No saved trips yet. Generate and save your first trip!")

    st.divider()
st.subheader("📄 Download Your Itinerary")

current_trip = st.session_state.get("trip_result")

if current_trip:
    try:
        pdf_bytes = generate_trip_pdf(current_trip)

        filename = (
            f"{current_trip.get('destination', 'trip')}"
            .strip()
            .replace(" ", "_")
            .lower()
        )

        st.download_button(
            label="⬇️ Download Trip PDF",
            data=pdf_bytes,
            file_name=f"{filename}_itinerary.pdf",
            mime="application/pdf",
        )
    except Exception as exc:
        st.error(f"Could not generate PDF: {exc}")
else:
    st.info("Generate or open a trip first.")
    
# --- Regenerate a Single Day ---
st.divider()
st.header("🔄 Customize Your Itinerary")

current_trip = st.session_state.get("trip_result")

if current_trip and current_trip.get("itinerary"):
    itinerary = current_trip["itinerary"]

    selected_day = st.selectbox(
        "Which day do you want to change?",
        options=list(range(1, len(itinerary) + 1)),
        format_func=lambda day: f"Day {day}",
        key="regenerate_day_select",
    )

    preferences = st.text_input(
        "What would you like to change?",
        placeholder="e.g. more nature, less walking, cheaper activities",
    )

    if st.button("Regenerate Selected Day"):
        old_day = itinerary[selected_day - 1]

        prompt = f"""
Return a valid JSON object for a travel itinerary day.

Destination: {current_trip.get('destination', 'Unknown')}
Day number: {selected_day}
Travel preferences: {preferences or 'Keep the original travel style'}
Previous day plan: {old_day}

Return this structure:
{{
  "day": {selected_day},
  "title": "Day title",
  "activities": [
    {{
      "time": "09:00 AM",
      "name": "Activity name",
      "description": "Short description",
      "estimated_cost": 500,
      "location": "Place name"
    }}
  ]
}}

Return only JSON. Keep the activities practical and suitable
for the destination.
"""

        with st.spinner(f"Regenerating Day {selected_day}..."):
            try:
                new_day = generate_json(prompt)

                if not isinstance(new_day.get("activities"), list):
                    raise ValueError("AI returned an invalid day plan.")

                new_day["day"] = selected_day

                updated_trip = current_trip.copy()
                updated_trip["itinerary"] = itinerary.copy()
                updated_trip["itinerary"][selected_day - 1] = new_day

                st.session_state["trip_result"] = updated_trip
                st.success(f"Day {selected_day} updated!")
                st.rerun()

            except Exception as exc:
                st.error(f"Could not regenerate this day: {exc}")
else:
    st.info("Generate or open a trip first.")

