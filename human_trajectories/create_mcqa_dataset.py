import numpy as np
import csv
import json

import argparse
import pandas as pd

from statistics import mean

from tqdm import tqdm
import os

if not os.path.exists("datasets"):
    os.makedirs("datasets")


def generate_prompt_data(args):
    window_size = args.window_size

    trajectories_dir = "./trajectories/"

    activity_files = sorted(os.listdir(trajectories_dir))
    dataset_sizes = []
    for activity_file in tqdm(activity_files):
        with open(trajectories_dir + activity_file, "r") as f:
            lines = f.readlines()[1:]
            trajectories = []

        df = pd.DataFrame(
            columns=[
                "task_step",
                "task_completion_percentage",
                "previous_actions",
                "choices",
                "correct_choice",
                "correct_action",
            ]
        )

        for line in lines:
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
            trajectories.append(trajectory_steps)

            previous_actions = []
            for step, trajectory_step in enumerate(trajectory_steps):
                if step == 0:
                    task_completion_percentage = 0
                    previous_actions = []
                else:
                    previous_actions = trajectory_steps[:step]
                    task_completion_percentage = step / len(trajectory_steps)

                # sample wrong choice using the window size either side of the correct choice
                wrong_choices = (
                    trajectory_steps[: step - window_size]
                    + trajectory_steps[step + window_size :]
                )
                if len(wrong_choices) == 0:
                    continue
                wrong_choice = np.random.choice(wrong_choices)
                correct_choice = trajectory_step.replace('"', "")
                if correct_choice == wrong_choice:
                    continue
                if np.random.rand() > 0.5:
                    correct_action = 0
                    choices = [correct_choice, wrong_choice]
                else:
                    correct_action = 1
                    choices = [wrong_choice, correct_choice]

                previous_actions = [
                    action.replace('"', "") for action in previous_actions
                ]
                choices = [choice.replace('"', "") for choice in choices]

                df.loc[len(df)] = [
                    step,
                    task_completion_percentage,
                    previous_actions.copy(),
                    choices,
                    correct_choice,
                    correct_action,
                ]
        df.to_csv(
            "./datasets/mcqa_dataset_" + str(activity_file),
            index=False,
        )
        # save a json file
        with open(
            "./datasets/mcqa_dataset_"
            + str(activity_file).replace(".csv", "")
            + ".json",
            "w",
        ) as f:
            json.dump(df.to_dict("records"), f)

        # print("Saved dataset for", activity_file, "dataset size:", len(df))
        dataset_sizes.append(len(df))

    # print generated dataset summary
    for activity_file, dataset_size in zip(activity_files, dataset_sizes):
        activity_file = activity_file.replace(".csv", "").replace("_", " ")
        print(f"{activity_file}, {dataset_size}")
    print(f"Average dataset size: {mean(dataset_sizes)}")


def generate_trajectories(args):
    generate_prompt_data(
        args,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--window_size", type=int, default=2)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--scenario",
        type=str,
        default="planting a tree",
        choices=[
            "baking a cake",
            "borrowing a book from the library",
            "changing batteries in an alarm clock",
            "checking in at an airport",
            "cleaning up a flat",
            "cooking pasta",
            "doing laundry",
            "eating in a fast food restaurant",
            "flying in an airplane",
            "fueling a car",
            "getting a hair cut",
            "going bowling",
            "going grocery shopping",
            "going on a train",
            "going to a funeral",
            "going to the dentist",
            "going to the sauna",
            "going to the swimming pool",
            "going to the theater",
            "having a barbecue",
            "ironing laundry",
            "making a bonfire",
            "making coffee",
            "making scrambled eggs",
            "paying with a credit card",
            "planting a tree",
            "playing tennis",
            "renovating a room",
            "repairing a flat bicycle tire",
            "riding on a bus",
            "sending food back (in a restaurant)",
            "sewing a button",
            "taking a bath",
            "taking a child to bed",
            "taking a driving lesson",
            "taking a shower",
            "taking the underground",
            "washing dishes",
            "washing one_s hair",
            "all",
        ],
    )
    args = parser.parse_args()
    # set seed
    np.random.seed(args.seed)

    if args.scenario == "all":
        generate_trajectories(args)
    else:
        generate_trajectories(args)
