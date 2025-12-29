# views.py
import os
import subprocess
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import os


def index(request):

    return render(request, 'index.html')

import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import Http404
import shutil

def inputs(request):
    if request.method == 'POST' and request.FILES:
        for file_key in request.FILES:
            file = request.FILES[file_key]
            file_path = os.path.join(settings.BASE_DIR, 'TG_app', 'media', file.name)
            
            # Check if the file already exists in the directory
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # Delete the existing file
                except PermissionError as e:
                    # Handle permission error gracefully
                    print(f"PermissionError: {e}")
                    # Optionally, you can log this error for debugging purposes
                    pass

            # Save the new file without using FileSystemStorage
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        
        return redirect('inputs')  # Redirect to the same page after upload

    return render(request, 'inputs.html')



import os
from pathlib import Path
from django.shortcuts import render
from django.conf import settings

def outputs(request):
    faculty_directory = Path(settings.MEDIA_ROOT) / 'FACULTY_timetables'
    department_directory = Path(settings.MEDIA_ROOT) / 'DEPARTMENT_timetables'
    
    if faculty_directory.exists():
        faculty_file_names = os.listdir(faculty_directory)
    else:
        faculty_file_names = []
        print(f"Faculty directory '{faculty_directory}' does not exist or is empty.")

    if department_directory.exists():
        department_file_names = os.listdir(department_directory)
    else:
        department_file_names = []
        print(f"Department directory '{department_directory}' does not exist or is empty.")

    context = {
        'faculty_file_names': faculty_file_names,
        'department_file_names': department_file_names,
    }
    return render(request, 'outputs.html', context)





def loading_animation(request):
    return render(request, 'loading_animation.html')

def generate_timetable(request):
    if request.method == 'POST':
        script_path = os.path.join(settings.BASE_DIR, 'TG_app', 'timetable_generator.py')
        try:
            # Run the script in background but don't wait for completion
            # This allows the web request to return immediately
            subprocess.Popen(['python', script_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return JsonResponse({'status': 'success', 'message': 'Timetable generation started.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def load_data():
    base_dir = settings.BASE_DIR
    labs_path = os.path.join(base_dir, 'media', 'labs_new.csv')
    courses_path = os.path.join(base_dir, 'media', 'courses_i.csv')
    lab_rooms_path = os.path.join(base_dir, 'media', 'lab_new_rooms.csv')
    
    try:
        labs = pd.read_csv(labs_path)
        courses = pd.read_csv(courses_path)
        lab_rooms = pd.read_csv(lab_rooms_path)
        
        # Debugging: Print head of each dataframe to verify loading
        print(labs.head())
        print(courses.head())
        print(lab_rooms.head())
        
        return labs, courses, lab_rooms
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None


from django.http import HttpResponse
from django.conf import settings
import os

def download_file(request, file_name):
    # Try faculty timetables first
    faculty_file_path = os.path.join(settings.MEDIA_ROOT, 'FACULTY_timetables', file_name)
    department_file_path = os.path.join(settings.MEDIA_ROOT, 'DEPARTMENT_timetables', file_name)
    
    file_path = None
    if os.path.exists(faculty_file_path):
        file_path = faculty_file_path
    elif os.path.exists(department_file_path):
        file_path = department_file_path
    
    if file_path:
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    
    raise Http404("File not found")


def profile(request):
    return render(request, 'profile.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')
def help(request):
    return render(request, 'help.html')

def rules(request):
    return render(request, 'rules.html')

def download_demo(request, filename):
    """Download demo CSV files"""
    from django.http import FileResponse, Http404
    import os
    from django.conf import settings
    
    # Define the demo files directory
    demo_dir = os.path.join(settings.BASE_DIR, 'TG_app', 'media', 'demo_files')
    file_path = os.path.join(demo_dir, filename)
    
    # Security check: ensure filename is one of the allowed demo files
    allowed_files = ['courses.csv', 'lab_rooms.csv', 'labs.csv']
    if filename not in allowed_files:
        raise Http404("File not found")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Return file as download
    response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response