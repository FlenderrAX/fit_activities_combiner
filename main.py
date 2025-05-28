import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog
from fitparse import FitFile


def get_file_path(prompt: str) -> str:
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=FILETYPES, title=prompt)
    if not file_path:
        print("No file selected. Exiting.")
        sys.exit(1)
    return file_path

def get_activity_distance(fit_file: FitFile) -> float:
    sessions = list(fit_file.get_messages("session"))
    total_distance: float = next((
        data.value
        for session in sessions
        for data in session
        if data.name == 'total_distance'
    ), 0.0)
    return total_distance

def get_activity_type(fit_file: FitFile) -> str:
    sessions = list(fit_file.get_messages("session"))
    sport = "".join(
        data.value
        for session in sessions
        for data in session
        if data.name == 'sport'
    )
    return sport

def check_activities_type(activities: list):
    if len(activities) < 2:
        raise Exception("You must select at least 2 activities !")
    
    activities_type = []
    for activ in activities:
        activities_type.append(get_activity_type(activ))

    if len(set(activities_type)) != 1:
        raise Exception("Activities must have the same types !")

def extract_activity_info(fit_file):
    records = list(fit_file.get_messages("record"))
    sessions = list(fit_file.get_messages("session"))
    return {
        "distance": [round(data.value, 2)
                     for record in records for data in record
                     if data.name == 'distance'],
        "speed": [round(data.value, 1)
                  for record in records
                  for data in record
                  if data.name == 'speed'],
        "cadence": [
            data.value
            for record in records
            for data in record
            if data.name == 'cadence'
        ],
        "heart_rate": [
            data.value
            for record in records
            for data in record
            if data.name == 'heart_rate'
        ],
        "position_lat": [
            data.value
            for record in records
            for data in record
            if data.name == 'position_lat'
        ],
        "position_long": [
            data.value
            for record in records
            for data in record
            if data.name == 'position_long'
        ],
        "total_distance": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'total_distance'
        ), 0.0),
        "sport": "".join(
            data.value
            for session in sessions
            for data in session
            if data.name == 'sport'
        ),
        "sub_sport": "".join(
            data.value
            for session in sessions
            for data in session
            if data.name == 'sub_sport'
        ),
        "avg_heart_rate": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'avg_heart_rate'
        ), 0),
        "max_heart_rate": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'max_heart_rate'
        ), 0),
        "total_timer_time": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'total_timer_time'
        ), 0.0),
        "total_elapsed_time": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'total_elapsed_time'
        ), 0.0),
        "start_time": next((
            data.value
            for session in sessions
            for data in session
            if data.name == 'start_time'
        ), 0.0),
    }

def generate_new_activity(first_activity: dict, second_activity: dict) -> dict:
    largest_distance: float = max(
        [first_activity.get("total_distance"),
        second_activity.get("total_distance")]
    )

    activities_list: list[dict] = [first_activity, second_activity]

    longest_activity: dict = next((
        d for d in activities_list
        if d.get("total_distance") == largest_distance),
        None
    )

    shortest_activity = activities_list[1] \
        if longest_activity == activities_list[0] \
        else activities_list[0]

    start_time: datetime = min(first_activity.get("start_time"),
                               second_activity.get("start_time"))
    total_elapsed_time: float = (first_activity.get("total_elapsed_time") +
                                 second_activity.get("total_elapsed_time"))
    total_timer_time: float = (first_activity.get("total_timer_time") +
                               second_activity.get("total_timer_time"))
    total_distance: float = (first_activity.get("total_distance") +
                             second_activity.get("total_distance"))
    sport: str = first_activity.get("sport")
    sub_sport: str = first_activity.get("sub_sport")
    avg_heart_rate: float = (
            (first_activity.get("avg_heart_rate") +
            second_activity.get("avg_heart_rate")) / 2
    )
    max_heart_rate: float = (max(
        first_activity.get("max_heart_rate"),
        second_activity.get("max_heart_rate"))
    )

    second_distances: list = [
        round(dist + longest_activity.get("total_distance"), 2)
        for dist in shortest_activity.get("distance")
    ]

    new_activity: dict = {
        "start_time": start_time,
        "total_elapsed_time": total_elapsed_time,
        "total_timer_time": total_timer_time,
        "sport": sport,
        "sub_sport": sub_sport,
        "total_distance": total_distance,
        "avg_heart_rate": avg_heart_rate,
        "max_heart_rate": max_heart_rate,
        "distances": (
            longest_activity.get("distance") +
            second_distances
        ),
        "position_lat": (
                longest_activity.get("position_lat") +
                shortest_activity.get("position_lat")
        ),
        "position_long": (
                longest_activity.get("position_long") +
                shortest_activity.get("position_long")
        ),
        "speeds": (
            longest_activity.get("speed") +
            shortest_activity.get("speed")
        ),
        "heart_rate": (
            longest_activity.get("heart_rate") +
            shortest_activity.get("heart_rate")
        ),
        "cadence": (
            longest_activity.get("cadence") +
            shortest_activity.get("cadence")
        )
    }

    return new_activity

if __name__ == "__main__":
    FILETYPES = [("FIT Files", "*.fit")]

    first_fit_file_path = get_file_path("Select First FIT File")
    second_fit_file_path = get_file_path("Select Second FIT File")

    first_fit_file: str = FitFile(os.path.basename(first_fit_file_path))
    second_fit_file: str = FitFile(os.path.basename(second_fit_file_path))

    activities = [first_fit_file, second_fit_file]

    check_activities_type(activities)

    first_activity_info = extract_activity_info(first_fit_file)
    second_activity_info = extract_activity_info(second_fit_file)

    new_activity_info: dict = generate_new_activity(first_activity_info, second_activity_info)

    print(new_activity_info)