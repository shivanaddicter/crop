import csv
import json

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CropPredictionForm, CSVUploadForm
from .ml_model import predict_crop
from .models import CropData, UploadedCSV
from .utils import CROP_RECOMMENDATIONS, get_weather


# ── Auth ──────────────────────────────────────────────────────────────────────

def custom_logout(request):
    """Custom logout view to avoid server crashes."""
    if request.method == "POST":
        auth_logout(request)
        return redirect("login")
    return redirect("dashboard")

def register(request):
    """Handle new user registration."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """Render the analytics dashboard for the logged-in user."""
    queryset = CropData.objects.filter(user=request.user).order_by("-created_at")
    total = queryset.count()

    # Averages
    avgs = queryset.aggregate(
        avg_temp=Avg("temperature"),
        avg_rain=Avg("rainfall"),
        avg_hum=Avg("humidity")
    )

    # Chart data — last 10 records
    recent = list(queryset[:10])
    # Reverse for chronological order in chart
    recent.reverse()
    temps = json.dumps([d.temperature for d in recent])
    rains = json.dumps([d.rainfall for d in recent])
    labels = json.dumps([d.created_at.strftime("%H:%M") for d in recent])

    # Crop distribution for doughnut chart
    crop_counts_map: dict[str, int] = {}
    for d in queryset:
        crop_counts_map[d.result] = crop_counts_map.get(d.result, 0) + 1

    crop_labels = json.dumps(list(crop_counts_map.keys()))
    crop_counts = json.dumps(list(crop_counts_map.values()))

    # Most predicted crop
    most_predicted = (
        max(crop_counts_map, key=crop_counts_map.get)
        if crop_counts_map
        else None
    )

    # Last prediction
    last = queryset.first()

    return render(request, "dashboard.html", {
        "data": queryset,
        "total": total,
        "avgs": avgs,
        "temps": temps,
        "rains": rains,
        "labels": labels,
        "crop_labels": crop_labels,
        "crop_counts": crop_counts,
        "last": last,
        "most_predicted": most_predicted,
        "now": timezone.now(),
    })


# ── Prediction ────────────────────────────────────────────────────────────────

@login_required
def predict(request):
    """Handle AI crop prediction form submission."""
    form = CropPredictionForm(request.POST or None)
    result = None
    recommendation = None

    if request.method == "POST" and form.is_valid():
        temp = form.cleaned_data["temperature"]
        rain = form.cleaned_data["rainfall"]
        humidity = form.cleaned_data["humidity"]

        result = predict_crop(temp, rain, humidity)

        CropData.objects.create(
            user=request.user,
            temperature=temp,
            rainfall=rain,
            humidity=humidity,
            result=result,
        )

        recommendation = CROP_RECOMMENDATIONS.get(result)

    return render(request, "predict.html", {
        "form": form,
        "result": result,
        "recommendation": recommendation,
    })


@login_required
def weather_predict(request):
    """Predict crop based on real-time weather of a city."""
    city = request.GET.get("city", "").strip()
    result = None
    recommendation = None
    weather_data = None
    error = None

    if city:
        try:
            temp, rain, hum = get_weather(city)
            weather_data = {"temp": temp, "rain": rain, "hum": hum, "city": city}
            
            result = predict_crop(temp, rain, hum)
            recommendation = CROP_RECOMMENDATIONS.get(result)
            
            # Save to history
            CropData.objects.create(
                user=request.user,
                temperature=temp,
                rainfall=rain,
                humidity=hum,
                result=result
            )
            messages.success(request, f"Weather data fetched for {city}!")
        except Exception as e:
            error = str(e)

    return render(request, "weather_predict.html", {
        "city": city,
        "result": result,
        "recommendation": recommendation,
        "weather": weather_data,
        "error": error
    })


# ── History ───────────────────────────────────────────────────────────────────

@login_required
def history(request):
    """Display prediction history with optional date filtering."""
    data = CropData.objects.filter(user=request.user).order_by("-created_at")

    from_date = request.GET.get("from", "")
    to_date = request.GET.get("to", "")

    if from_date:
        data = data.filter(created_at__date__gte=from_date)
    if to_date:
        data = data.filter(created_at__date__lte=to_date)

    return render(request, "history.html", {
        "data": data,
        "from_date": from_date,
        "to_date": to_date,
    })


@login_required
def delete_record(request, pk):
    """Delete a single prediction record belonging to the current user."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    record = get_object_or_404(CropData, pk=pk, user=request.user)
    record.delete()
    messages.success(request, f"Record #{pk} deleted successfully.")
    return redirect("history")


@login_required
def delete_all_history(request):
    """Delete every prediction record for the current user."""
    if request.method == "POST":
        count, _ = CropData.objects.filter(user=request.user).delete()
        messages.success(request, f"All {count} record(s) deleted successfully.")
    return redirect("history")


# ── Export ────────────────────────────────────────────────────────────────────

@login_required
def export_csv(request):
    """Export the user's prediction history as a downloadable CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="crop_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Temperature (°C)", "Rainfall (mm)", "Humidity (%)", "Predicted Crop", "Date"])

    for d in CropData.objects.filter(user=request.user).order_by("-created_at"):
        writer.writerow([
            d.temperature,
            d.rainfall,
            d.humidity,
            d.result,
            d.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response


# ── CSV Upload ────────────────────────────────────────────────────────────────

@login_required
def upload_csv(request):
    """Handle batch prediction via CSV file upload."""
    form = CSVUploadForm(request.POST or None, request.FILES or None)
    message = None
    error = None

    if request.method == "POST" and form.is_valid():
        try:
            uploaded_file = form.cleaned_data["file"]
            
            # Save the file record
            UploadedCSV.objects.create(user=request.user, file=uploaded_file)
            
            # Reset file pointer for reading
            uploaded_file.seek(0)
            decoded_lines = uploaded_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_lines)

            count = 0
            errors = []

            for i, row in enumerate(reader, start=2):  # row 1 is header
                try:
                    temp = float(row.get("temperature") or row.get("Temperature") or 0)
                    rain = float(row.get("rainfall") or row.get("Rainfall") or 0)
                    hum = float(row.get("humidity") or row.get("Humidity") or 0)
                except (ValueError, TypeError):
                    errors.append(f"Row {i}: non-numeric value, skipped.")
                    continue

                result = predict_crop(temp, rain, hum)
                CropData.objects.create(
                    user=request.user,
                    temperature=temp,
                    rainfall=rain,
                    humidity=hum,
                    result=result,
                )
                count += 1

            message = f"✅ Successfully processed {count} record(s)."
            if errors:
                message += f" ({len(errors)} row(s) skipped due to errors.)"

        except Exception as exc:
            error = f"❌ Error processing file: {exc}"

    return render(request, "upload.html", {
        "form": form,
        "message": message,
        "error": error,
    })


# ── Founder ───────────────────────────────────────────────────────────────────

@login_required
def founder(request):
    """Render the Founder profile page."""
    skills = [
        "Python", "Flask", "Django", "Java", "SQL",
        "MongoDB", "HTML5", "CSS3", "Bootstrap",
        "JavaScript", "jQuery", "Fullstack Development",
        "AI & Data Science",
    ]
    return render(request, "founder.html", {"skills": skills})