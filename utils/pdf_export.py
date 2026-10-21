
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_trip_pdf(trip: dict) -> bytes:
    """Generate a downloadable PDF for a trip itinerary."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Activity",
            parent=styles["Normal"],
            spaceAfter=6,
            leading=15,
        )
    )

    story = []

    destination = str(trip.get("destination", "Your Trip"))
    days = trip.get("days", 1)
    estimated_cost = trip.get("estimated_total_cost", 0)

    story.append(Paragraph("TripPilot Travel Plan", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Destination: {destination}", styles["Heading1"]))
    story.append(Paragraph(f"Duration: {days} days", styles["Normal"]))
    story.append(
        Paragraph(
            f"Estimated total cost: INR {float(estimated_cost):,.0f}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 18))

    for day in trip.get("itinerary", []):
        day_number = day.get("day", "?")
        title = str(day.get("title", "Explore"))

        story.append(
            Paragraph(
                f"Day {day_number}: {title}",
                styles["Heading2"],
            )
        )

        activities = day.get("activities", [])

        if not activities:
            story.append(Paragraph("No activities listed.", styles["Normal"]))

        for activity in activities:
            time = str(activity.get("time", "Flexible"))
            name = str(activity.get("name", "Activity"))
            description = str(activity.get("description", ""))
            location = str(activity.get("location", ""))
            cost = float(activity.get("estimated_cost", 0))

            text = (
                f"<b>{time} - {name}</b><br/>"
                f"{description}<br/>"
                f"Location: {location}<br/>"
                f"Estimated cost: INR {cost:,.0f}"
            )

            story.append(Paragraph(text, styles["Activity"]))

        story.append(Spacer(1, 10))

    tips = trip.get("travel_tips", [])

    if tips:
        story.append(Paragraph("Travel Tips", styles["Heading2"]))
        for tip in tips:
            story.append(
                Paragraph(f"- {str(tip)}", styles["Activity"])
            )

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Note: Prices and travel details are estimates. "
            "Please verify before booking.",
            styles["Italic"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
