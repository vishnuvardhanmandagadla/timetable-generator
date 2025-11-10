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
            file_path = os.path.join(settings.BASE_DIR, 'myapp', 'media', file.name)
            
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
        script_path = os.path.join(settings.BASE_DIR, 'myapp', 'timetable_generator.py')
        try:
            subprocess.Popen(['python', script_path])
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
    file_path = os.path.join(settings.MEDIA_ROOT, 'FACULTY_timetables', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


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