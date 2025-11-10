# Timetable Generator

Timetable Generator is a Django web application that produces departmental and faculty-wise timetables from uploaded CSV data. It combines laboratory allocations and course schedules to export ready-to-distribute `.csv` timetables while offering a simple browser-based workflow for administrators.

## Features
- Upload labs, lab room availability, and course metadata directly from the web UI.
- Generate consolidated timetables per department (`myapp/media/DEPARTMENT_timetables/`) and per faculty (`myapp/media/FACULTY_timetables/`).
- Review generated files in the browser before downloading.
- Ships with sample datasets so you can explore the workflow immediately.

## Project Structure
```
myproject/
├── manage.py
├── myapp/
│   ├── media/                 # Sample CSV inputs and generated outputs
│   ├── static/                # Front-end assets used by the UI
│   ├── templates/             # Django templates (index, inputs, outputs, etc.)
│   ├── timetable_generator.py # Core timetable generation script
│   └── views.py               # Request handlers for uploads and generation
└── myproject/
    └── settings.py            # Project configuration
```

## Requirements
- Python 3.11+ (tested with 3.12)
- pip
- SQLite (bundled with Python, used by default)

## Getting Started

1. **Clone the repository**
   ```powershell
   git clone https://github.com/vishnuvardhanmandagadla/timetable-generator.git
   cd timetable-generator/myproject
   ```

2. **Create and activate a virtual environment (recommended)**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install django pandas numpy
   ```

4. **Apply migrations**
   ```powershell
   python manage.py migrate
   ```

5. **Run the development server**
   ```powershell
   python manage.py runserver
   ```
   The site is now available at `http://127.0.0.1:8000/`.

6. **Generate timetables**
   - Navigate to `http://127.0.0.1:8000/inputs.html` to upload updated CSV files if needed.
   - Trigger timetable generation from the landing page (`Generate Timetable` button). This launches `timetable_generator.py` in a background process.
   - Visit `http://127.0.0.1:8000/outputs.html` to download the generated CSV files.

## Data Inputs
Sample CSV files live under `myapp/media/`. Replace them with your institution’s datasets:
- `labs.csv` – laboratory metadata (academic year, department, faculty, room numbers, etc.).
- `lab_rooms.csv` – room availability template.
- `courses.csv` – theory course information, including relative importance for scheduling.

The generator will overwrite `lab_rooms.csv` and clean the output directories on each run. Back up or version control any customized files you care about.

## Alternative Launch Script
On Windows you can double-click `launch_TimeTable_genaretor.bat` from the repository root. The batch script upgrades `pip`, installs dependencies, runs database migrations, and starts the development server automatically.

## Troubleshooting
- If uploads fail, ensure the target files in `myapp/media/` are not open in another program.
- When running the generator repeatedly, confirm old timetables are cleared or archived if you need to preserve history.
- Review console logs for `Remaining labs that were not placed` messages; these highlight conflicts that need manual adjustment in the CSV inputs.

## License
This project is currently published without an explicit license. Add one before distributing or deploying outside of personal use.

