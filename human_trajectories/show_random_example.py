import csv
import os
import numpy as np
import random

trajectories_dir = "./trajectories/"

activity_files = os.listdir(trajectories_dir)
# choose a random activity
activity_file = random.choice(activity_files)

# read a random line from the activity file
with open(trajectories_dir + activity_file, "r") as f:
    lines = f.readlines()
    line = random.choice(lines)
    line_split = [
        '"{}"'.format(x)
        for x in list(csv.reader([line], delimiter=",", quotechar='"'))[0]
    ]
    trajectory_id = line_split[0]
    trajectory_steps = line_split[1:]
    # remove the empty steps
    trajectory_steps = [
        step
        for step in trajectory_steps
        if step != "" and step != "\n" and step != '""'
    ]
print("Activity file: ", activity_file)
print("Trajectory id: ", trajectory_id)
print("Trajectory steps: ")
for i, step in enumerate(trajectory_steps):
    print("{}. {}".format(i + 1, step))
