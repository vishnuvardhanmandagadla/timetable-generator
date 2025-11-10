import ast
import os
import pandas as pd
import numpy as np
from django.conf import settings
from django.shortcuts import render, redirect
import random

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

# Ensure the DEPARTMENT_timetables and FACULTY_timetables directories are empty
department_dir = os.path.join(base_dir, 'media', 'DEPARTMENT_timetables')
if os.path.exists(department_dir):
    for file in os.listdir(department_dir):
        os.remove(os.path.join(department_dir, file))
else:
    os.makedirs(department_dir)

faculty_dir = os.path.join(base_dir, 'media', 'FACULTY_timetables')
if os.path.exists(faculty_dir):
    for file in os.listdir(faculty_dir):
        os.remove(os.path.join(faculty_dir, file))
else:
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

def generate_timetable(year, department, timetable, existing_timetables):
    """Generate timetable for a given year and department."""

    # Fetch and multiply lab records
    labs_filtered = labs[(labs['academic_year'] == year) & (labs['department'] == department)]
    labs_list = labs_filtered.to_dict('records') * 2  # Adjust the multiplication factor if needed

    i = 0

    def place_labs():
        """Place labs into the timetable."""
        nonlocal i
        for day in days:
            two_labs_placed = False
            lab_no = 0

            while lab_no < len(labs_list):
                if lab_no >= len(labs_list):  # End of labs_list
                    break

                time_of_day, three_periods = all_slots[i % len(all_slots)]
                if i == 4:
                    i = 0
                    time_of_day, three_periods = all_slots[i % len(all_slots)]

                if two_labs_placed or not labs_list:
                    i += 1
                    break

                lab_item = labs_list[lab_no]
                lab_name = lab_item['lab_name']
                faculty_name = lab_item['faculty']
                room_no = lab_item['room_no']
                lab_slicing = lab_item['slice']

                if time_of_day == "Morning":
                    room_col = "M_" + room_no
                else:
                    room_col = "A_" + room_no

                slot_idx = check_room_availability(room_col, day, room_no)
                if slot_idx is not None:
                    # Check faculty collision
                    if not check_faculty_collision(faculty_name, day, periods[three_periods[0]], existing_timetables):
                        # Check if the lab can be shared or if all periods are free
                        if lab_slicing == 1:
                            # Allow sharing if at least one period is free
                            can_share = any(timetable.at[day, periods[period]] in ["Free", [(lab_name, faculty_name)]] for period in three_periods)
                            if can_share:
                                for period in three_periods:
                                    if timetable.at[day, periods[period]] == "Free":
                                        timetable.at[day, periods[period]] = [(lab_name, faculty_name)]
                                    elif len(timetable.at[day, periods[period]]) < 2:
                                        timetable.at[day, periods[period]].append((lab_name, faculty_name))

                                update_lab_rooms(day, room_col, slot_idx, year, department, lab_name, faculty_name)
                                update_faculty_timetable(faculty_name, day, three_periods[0], f"{lab_name} ({year}, {department})")
                                labs_list.pop(lab_no)
                                two_labs_placed = True
                                break  # Move to the next day after placing the lab
                        else:
                            if all(timetable.at[day, periods[period]] == "Free" for period in three_periods):
                                for period in three_periods:
                                    timetable.at[day, periods[period]] = [(lab_name, faculty_name)]

                                update_lab_rooms(day, room_col, slot_idx, year, department, lab_name, faculty_name)
                                update_faculty_timetable(faculty_name, day, three_periods[0], f"{lab_name} ({year}, {department})")
                                labs_list.pop(lab_no)
                                two_labs_placed = True
                                break  # Move to the next day after placing the lab
                    else:
                        lab_no += 1
                else:
                    lab_no += 1

        existing_timetables[(year, department)] = timetable

    def check_faculty_collision(faculty_name, day, period, existing_timetables):
        """Check if there's a faculty collision in the given period."""
        for existing_timetable in existing_timetables.values():
            if existing_timetable.at[day, period] != "Free":
                for _, faculty in existing_timetable.at[day, period]:
                    if faculty == faculty_name:
                        return True
        return False

    def check_room_availability(room_col, day, room_no):
        """Check if the room is available for the lab."""
        slot_values = lab_rooms.loc[lab_rooms['Day'] == day, room_col].values[0]
        if pd.isna(slot_values):
            slot_list = ['Free']
        else:
            slot_list = ast.literal_eval(slot_values)

        for idx, slot in enumerate(slot_list):
            if slot == 'Free':
                return idx

        return None

    def update_lab_rooms(day, room_col, slot_idx, year, department, lab_name, faculty_name):
        """Update the lab_rooms DataFrame."""
        slot_list = ast.literal_eval(lab_rooms.loc[lab_rooms['Day'] == day, room_col].values[0]) if not pd.isna(lab_rooms.loc[lab_rooms['Day'] == day, room_col].values[0]) else ['Free']
        slot_list[slot_idx] = (year, department, lab_name, faculty_name)
        lab_rooms.loc[lab_rooms['Day'] == day, room_col] = str(slot_list)
        lab_rooms.to_csv(lab_rooms_path, index=False)

    # Call the nested function to place labs
    place_labs()

    return timetable

import random

def count_free_slots(timetable):
    free_count = 0
    for day in days:
        for period in periods:
            if period != "Lunch Break" and timetable.at[day, period] == "Free":
                free_count += 1
    return free_count

def place_courses(year, department, timetable, existing_timetables):
    courses_filtered = courses[(courses['academic_year'] == year) & (courses['department'] == department)]
    
    print(f"\nPlacing courses for Year {year}, Department {department}:")
    print(courses_filtered)
    
    period_names = [
        "09:00 - 10:00", "10:00 - 10:50", "11:10 - 12:00", "12:00 - 12:50", 
        "Lunch Break", 
        "01:30 - 02:20", "02:20 - 03:10", "03:10 - 04:00"
    ]
    
    courses_list = []
    importance_course = []

    for _, course_item in courses_filtered.iterrows():
        importance = course_item['importance']
        importance_course.extend([course_item.to_dict()] * importance)
    
    courses_list.extend(importance_course)

    best_timetable = timetable.copy()
    best_free_count = count_free_slots(timetable)
    best_faculty_updates = []

    for k in range(7):  # Try different shuffles
        shuffle_seed=k+3  #contol random
        random.seed(shuffle_seed)
        shuffled_courses_list = courses_list.copy()
        random.shuffle(shuffled_courses_list)
        temp_timetable = timetable.copy()
        temp_course_counts = {day: {course_item['course']: 0 for _, course_item in courses_filtered.iterrows()} for day in days}
        temp_existing_timetables = existing_timetables.copy()
        temp_faculty_updates = []

        for day in days:
            for period_idx, period in enumerate(period_names):
                if period == "Lunch Break":
                    continue

                if temp_timetable.at[day, period] == "Free":
                    for course_item in shuffled_courses_list:
                        course_name = course_item['course']
                        faculty_name = course_item['faculty']
                        faculty_collision = False

                        if temp_course_counts[day][course_name] >= 2:
                            continue

                        if period_idx > 0 and temp_timetable.at[day, period_names[period_idx - 1]] != "Free":
                            previous_period_entries = temp_timetable.at[day, period_names[period_idx - 1]]
                            if isinstance(previous_period_entries, list):
                                for _, faculty in previous_period_entries:
                                    if faculty == faculty_name:
                                        faculty_collision = True
                                        break

                        if not faculty_collision:
                            for existing_timetable in temp_existing_timetables.values():
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
                            if temp_timetable.at[day, period] == "Free":
                                temp_timetable.at[day, period] = [(course_name, faculty_name)]
                            else:
                                temp_timetable.at[day, period].append((course_name, faculty_name))

                            shuffled_courses_list.remove(course_item)
                            temp_course_counts[day][course_name] += 1

                            temp_faculty_updates.append((faculty_name, day, period, f"{course_name} ({year}, {department})"))
                            break

        current_free_count = count_free_slots(temp_timetable)
        if current_free_count < best_free_count:
            best_free_count = current_free_count
            best_timetable = temp_timetable.copy()
            best_faculty_updates = temp_faculty_updates.copy()

    existing_timetables[(year, department)] = best_timetable

    # Apply the best faculty updates
    for faculty_name, day, period, entry in best_faculty_updates:
        update_faculty_timetable(faculty_name, day, period, entry)


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