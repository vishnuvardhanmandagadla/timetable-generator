import ast
import os
import pandas as pd
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect

# Define periods and days
periods = [
    "09:00 - 10:00", "10:00 - 10:50", "11:10 - 12:00", "12:00 - 12:50", 
    "Lunch Break", 
    "01:30 - 02:20", "02:20 - 03:10", "03:10 - 04:00"
]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Define available morning and afternoon slots
morning_slots = [(0, 1, 2), (1, 2, 3)]
afternoon_slot = [(5, 6, 7)]
all_slots = [("Morning", slot) for slot in morning_slots] + [("Afternoon", slot) for slot in afternoon_slot]

# Load data
# Load data
#base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV files
labs_path = os.path.join(base_dir, 'media', 'labs.csv')
courses_path = os.path.join(base_dir, 'media', 'courses.csv')
lab_rooms_path = os.path.join(base_dir, 'media', 'lab_rooms.csv')

# Load data
labs = pd.read_csv(labs_path)
courses = pd.read_csv(courses_path)
lab_rooms = pd.read_csv(lab_rooms_path)

# Initialize lab_rooms to "Free"
def initialize_lab_rooms():
    output_directory = os.path.dirname(lab_rooms_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for day in days:
        for col in lab_rooms.columns:
            if col != 'Day':
                lab_rooms.loc[lab_rooms['Day'] == day, col] = "['Free']"
    
    lab_rooms.to_csv(lab_rooms_path, index=False)

# Initialize the lab rooms to "Free"
initialize_lab_rooms()


# Create an empty timetable DataFrame
timetable_template = pd.DataFrame(index=days, columns=periods)
timetable_template = timetable_template.fillna("Free")
timetable_template["Lunch Break"] = "Lunch Break"

# Create a directory for faculty timetables
faculty_dir = os.path.join(base_dir, 'media', 'FACULTY_timetables')
if not os.path.exists(faculty_dir):
    os.makedirs(faculty_dir)

# Generate initial empty timetables for each faculty
faculty_list = np.unique(np.concatenate((labs['faculty'].unique(), courses['faculty'].unique())))
for faculty in faculty_list:
    faculty_timetable = pd.DataFrame('Free ()', index=days, columns=periods)
    faculty_timetable["Lunch Break"] = "Lunch Break"
    faculty_timetable.to_csv(f"{faculty_dir}/{faculty}_timetable.csv")

# Function to update faculty timetables
def update_faculty_timetable(faculty, day, period, entry):
    faculty_timetable_path = f"{faculty_dir}/{faculty}_timetable.csv"
    faculty_timetable = pd.read_csv(faculty_timetable_path, index_col=0)
    if faculty_timetable.at[day, period] == "Free ()":
        faculty_timetable.at[day, period] = entry
    else:
        faculty_timetable.at[day, period] += f", {entry}"
    faculty_timetable.to_csv(faculty_timetable_path)

# Function to generate the timetable
def generate_timetable(year, department, timetable, existing_timetables):
    labs_filtered = labs[(labs['academic_year'] == year) & (labs['department'] == department)]
    labs_list = labs_filtered.to_dict('records') * 2
    i = 0

    for day in days:
        two_labs_placed = False
        faculty_collision = False
        room_available = True

        lab_no = 0
        while lab_no < len(labs_list):
            if lab_no == len(labs_list): # stopping Empty labs_list: If labs_list is empty or if it doesn't contain enough elements, trying to access an index that doesn't exist will cause this error.
                break
            time_of_day, three_periods = all_slots[i % len(all_slots)]
            if faculty_collision:
                time_of_day, three_periods = all_slots[(i + 1) % len(all_slots)]
            if i == 4:
                i = 0
                time_of_day, three_periods = all_slots[i % len(all_slots)]
            if two_labs_placed or not labs_list:
                i += 1
                break
            if not room_available:
                lab_no += 1
                if lab_no == len(labs_list):
                    i -= 1
                    break
            room_available = False

            lab_item = labs_list[lab_no]
            lab_name = lab_item['lab_name']
            faculty_name = lab_item['faculty']
            room_no = lab_item['room_no']

            if time_of_day == "Morning":
                room_col = "M_" + room_no
            else:
                room_col = "A_" + room_no

            slot_values = lab_rooms.loc[lab_rooms['Day'] == day, room_col].values[0]
            if pd.isna(slot_values):
                slot_list = ['Free']
            else:
                slot_list = ast.literal_eval(slot_values)

            for idx in range(len(slot_list)):
                if slot_list[idx] == 'Free':
                    room_available = True
                    break

            if room_available:
                for period in three_periods:
                    if faculty_collision:
                        break
                    for existing_timetable in existing_timetables.values():
                        if faculty_collision:
                            break
                        if existing_timetable.at[day, periods[period]] != "Free":
                            for _, faculty in existing_timetable.at[day, periods[period]]:
                                if faculty == faculty_name:
                                    faculty_collision = True
                                    break
                        else:
                            faculty_collision = False

            if not faculty_collision and room_available:
                slot_list[idx] = (year, department, lab_name, faculty_name)
                lab_rooms.loc[lab_rooms['Day'] == day, room_col] = str(slot_list)
                lab_rooms.to_csv(lab_rooms_path, index=False)
                for period in three_periods:
                    if timetable.at[day, periods[period]] == "Free":
                        timetable.at[day, periods[period]] = [(lab_name, faculty_name)]
                    else:
                        timetable.at[day, periods[period]].append((lab_name, faculty_name))
                        if len(timetable.at[day, periods[period]]) == 2:
                            two_labs_placed = True

                    update_faculty_timetable(faculty_name, day, periods[period], f"{lab_name} ({year}, {department})")

                labs_list.pop(lab_no)
            else:
                lab_no += 1

            # Ensure lab_no does not exceed the length of labs_list
            if lab_no >= len(labs_list):
                break

        existing_timetables[(year, department)] = timetable

def place_courses(year, department, timetable, existing_timetables):
    # Filter courses based on the academic year and department
    courses_filtered = courses[(courses['academic_year'] == year) & (courses['department'] == department)]
    
    print(f"\nPlacing courses for Year {year}, Department {department}:")
    print(courses_filtered)
    
    period_names = [
        "09:00 - 10:00", "10:00 - 10:50", "11:10 - 12:00", "12:00 - 12:50", 
        "Lunch Break", 
        "01:30 - 02:20", "02:20 - 03:10", "03:10 - 04:00"
    ]
    
    # Initialize courses_list and importance_course
    courses_list = []
    importance_course = []

    # Repeat courses according to their importance and add to importance_course
    for _, course_item in courses_filtered.iterrows():
        importance = course_item['importance']  # assuming importance value is in the column 'importance'
        importance_course.extend([course_item.to_dict()] * importance)
    
    # Add repeated courses to the main courses_list
    courses_list.extend(importance_course)

    # Initialize a dictionary to track course counts per day
    course_counts = {day: {course_item['course']: 0 for _, course_item in courses_filtered.iterrows()} for day in days}

    for day in days:
        for period_idx, period in enumerate(period_names):
            if period == "Lunch Break":
                continue

            if timetable.at[day, period] == "Free":
                for course_item in courses_list:
                    course_name = course_item['course']
                    faculty_name = course_item['faculty']
                    faculty_collision = False

                    # Check if the course has already been scheduled twice for this day
                    if course_counts[day][course_name] >= 2:
                        continue

                    # Check if the course is being placed in a consecutive period
                    if period_idx > 0 and timetable.at[day, period_names[period_idx - 1]] != "Free":
                        previous_period_entries = timetable.at[day, period_names[period_idx - 1]]
                        if isinstance(previous_period_entries, list):
                            for _, faculty in previous_period_entries:
                                if faculty == faculty_name:
                                    faculty_collision = True
                                    break

                    # Check for faculty collision in existing timetables
                    if not faculty_collision:
                        for existing_timetable in existing_timetables.values():
                            if faculty_collision:
                                break
                            if existing_timetable.at[day, period] != "Free":
                                existing_period_entries = existing_timetable.at[day, period]
                                if isinstance(existing_period_entries, list):
                                    for _, faculty in existing_period_entries:
                                        if faculty == faculty_name:
                                            faculty_collision = True
                                            break

                    if not faculty_collision:
                        if timetable.at[day, period] == "Free":
                            timetable.at[day, period] = [(course_name, faculty_name)]
                        else:
                            timetable.at[day, period].append((course_name, faculty_name))

                        courses_list.remove(course_item)
                        course_counts[day][course_name] += 1

                        update_faculty_timetable(faculty_name, day, period, f"{course_name} ({year}, {department})")
                        break

    existing_timetables[(year, department)] = timetable

# Function to print the timetable
def print_timetable(timetable):
    print("{:<10} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format('', *periods))
    for day in days:
        row = [day]
        for period in periods:
            if period == "Lunch Break":
                row.append('Lunch Break')
            else:
                labs_at_timeslot = timetable.at[day, period]
                if labs_at_timeslot == "Free":
                    row.append('Free')
                else:
                    row.append(', '.join([f"{lab} ({faculty})" for lab, faculty in labs_at_timeslot]))
        print("{:<10} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}".format(*row))

# Function to save the timetable as a CSV file with faculty and courses/labs details
def save_timetable(timetable, year, department):
    directory = os.path.join(base_dir, 'media', 'DEPARTMENT_timetables')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/{year}_{department}_timetable.csv"
    
    # Create a copy of the timetable to avoid modifying the original
    timetable_to_save = timetable.copy()
    
    # Iterate through each cell in the timetable
    for day in days:
        for period in periods:
            if period == "Lunch Break":
                continue
            entries = timetable_to_save.at[day, period]
            if entries != "Free":
                entries_str = ', '.join([f"{entry[0]} ({entry[1]})" for entry in entries])
                timetable_to_save.at[day, period] = entries_str
    
    # Save the modified timetable to CSV
    timetable_to_save.to_csv(filename, index_label='Day')

    # Extract faculty and courses details
    courses_filtered = courses[(courses['academic_year'] == year) & (courses['department'] == department)]
    labs_filtered = labs[(labs['academic_year'] == year) & (labs['department'] == department)]
    
    faculty_courses = courses_filtered[['faculty', 'course']].drop_duplicates().sort_values(by='faculty')
    faculty_labs = labs_filtered[['faculty', 'lab_name']].drop_duplicates().sort_values(by='faculty')

    # Append department details below the timetable
    with open(filename, 'a') as file:
        file.write('\n\n')  # Add a few empty lines
        #courses details
        file.write(f"Faculty and Courses for Year {year}, Department {department}:\n")
        file.write(faculty_courses.to_string(index=False) + '\n')
        #labs details
        file.write(f"Faculty and Labs for Year {year}, Department {department}:\n")
        file.write(faculty_labs.to_string(index=False) + '\n')

    print(f"Timetable saved for Year {year}, Department {department}.")
# Main execution
existing_timetables = {}

years = sorted(labs['academic_year'].unique())
departments = sorted(labs['department'].unique())

# First, generate timetables with labs
for year in years:
    # Get departments for the specific year
    departments_for_year = labs[labs['academic_year'] == year]['department'].unique()
    for department in departments_for_year:
        generate_timetable(year, department, timetable_template.copy(), existing_timetables)

# Then, place courses in the same timetables
for year in years:
    # Get departments for the specific year
    departments_for_year = labs[labs['academic_year'] == year]['department'].unique()
    for department in departments_for_year:
        place_courses(year, department, existing_timetables[(year, department)], existing_timetables)
        print(f"\nTimetable for Year {year}, Department {department}:\n")
        print_timetable(existing_timetables[(year, department)])
        save_timetable(existing_timetables[(year, department)], year, department)