from django import forms


class CropPredictionForm(forms.Form):
    """Form for single-record crop prediction."""

    temperature = forms.FloatField(
        min_value=-50,
        max_value=60,
        widget=forms.NumberInput(attrs={
            "id": "id_temp",
            "class": "form-input",
            "placeholder": "e.g. 28.5",
            "step": "0.1",
        }),
        error_messages={
            "required": "Temperature is required.",
            "invalid": "Enter a valid number.",
            "min_value": "Temperature must be at least -50°C.",
            "max_value": "Temperature cannot exceed 60°C.",
        },
    )

    rainfall = forms.FloatField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={
            "id": "id_rain",
            "class": "form-input",
            "placeholder": "e.g. 150",
            "step": "0.1",
        }),
        error_messages={
            "required": "Rainfall is required.",
            "invalid": "Enter a valid number.",
            "min_value": "Rainfall cannot be negative.",
            "max_value": "Rainfall seems unrealistically high (max 5000 mm).",
        },
    )

    humidity = forms.FloatField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            "id": "id_hum",
            "class": "form-input",
            "placeholder": "e.g. 65",
            "step": "0.1",
        }),
        error_messages={
            "required": "Humidity is required.",
            "invalid": "Enter a valid number.",
            "min_value": "Humidity must be between 0 and 100%.",
            "max_value": "Humidity must be between 0 and 100%.",
        },
    )


class CSVUploadForm(forms.Form):
    """Form for batch CSV upload."""

    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            "id": "fileInput",
            "accept": ".csv",
            "style": "display:none;",
        }),
        error_messages={
            "required": "Please select a CSV file to upload.",
        },
    )

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if f:
            if not f.name.lower().endswith(".csv"):
                raise forms.ValidationError("Only .csv files are accepted.")
            if f.size > 5 * 1024 * 1024:  # 5 MB limit
                raise forms.ValidationError("File size must be under 5 MB.")
        return f