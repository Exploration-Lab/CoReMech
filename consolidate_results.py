import os
import numpy as np
import pandas as pd

prediction_files = os.listdir("lm_predictions")
prediction_files = [
    file for file in prediction_files if "prompt_dataset_" in file and "--" in file
]
prediction_files = sorted(prediction_files)
compare_scenarios = True
nshot_tag = "nshot-2"
if compare_scenarios:
    # filter out the zero shot results
    prediction_files = [file for file in prediction_files if nshot_tag in file]


scenarios = [
    x.split("scenario-")[-1].split("_model")[0].replace("_", " ")
    for x in prediction_files
    if "prompt_dataset_" in x
]

print(scenarios)
# scenarios = [s.split(" ")[-1] for s in scenarios]


# extract language model name from the prediction file name prompt_dataset_predictions_test_EleutherAI--gpt-neo-1.3B_nshot-0.csv -> gpt-neo-1.3B
language_models = [
    x.split("model-")[-1].split("_")[0].split("--")[-1]
    for x in prediction_files
    if "prompt_dataset_" in x
]
# nshots = [
#     x.split("_")[5].split("-")[-1].replace(".csv", "")
#     for x in prediction_files
#     if "prompt_dataset_" in x
# ]
nshots = [
    x.split("n_shot")[-1].split("-")[-1].replace(".csv", "")
    for x in prediction_files
    if "prompt_dataset_" in x
]
print(language_models)
print(nshots)
# exit()

if compare_scenarios:
    nshots = language_models.copy()
    tags = scenarios
else:
    tags = nshots
    # language_models = scenarios.copy()

# exit()
# awesome looking color list with 5 colors of matching brightness
color_list = [
    "RoyalBlue",
    "Pink",
    # "Orange",
    # 196, 198, 253
    "LightSkyBlue",
    "LimeGreen",
    # "Goldenrod",
]


success_rates = []
for prediction_file, tag, nshot in zip(prediction_files, tags, nshots):
    prompt_df = pd.read_csv(os.path.join("lm_predictions", prediction_file))
    prompt_df = prompt_df[prompt_df["predicted_token"] != "NONE"]
    success_rate = (
        100
        * prompt_df[prompt_df["predicted_action"] == prompt_df["correct_action"]].shape[
            0
        ]
        / prompt_df.shape[0]
    )
    print(
        tag,
        nshot,
        prompt_df.shape[0],
        success_rate,
    )
    success_rates.append(success_rate)

print(len(np.unique(tags)))

# plot a bar plot of success rate vs language model name with nshot as hue
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
sns.set_context("paper", font_scale=1.5)

if compare_scenarios:
    plt.figure(figsize=(5 / 10 * len(scenarios), 5))
# sort the tags and success rates by nshots
# tags = [tag for _, tag in sorted(zip(nshots, tags))]
# success_rates = [rate for _, rate in sorted(zip(nshots, success_rates))]
# nshots = sorted(nshots)
ax = sns.barplot(x=tags, y=success_rates, palette=color_list, hue=nshots)
# put the values over the bars
for p in ax.patches:
    ax.annotate(
        "{:.1f}".format(p.get_height()),
        (p.get_x() + p.get_width() / 2.0, p.get_height()),
        ha="center",
        va="center",
        fontsize=10,
        xytext=(0, 10),
        textcoords="offset points",
    )
ax.set_xlabel("Language Models")
ax.set_ylabel("Success Rate")
ax.set_title("Success Rate of Language Models over MCQ Evaluation " + nshot_tag)
plt.ylim([0, 100])
if nshots == scenarios:
    plt.legend(
        title="Scenario",
        #    loc="upper left"
    )
elif nshots == language_models:
    plt.legend(
        title="Language Model",
        #    loc="upper left"
    )
    # make the legend outside and horizontal
    plt.legend(
        bbox_to_anchor=(0.5, 1.15),
        loc="lower center",
        # title="Language Model",
        title_fontsize="15",
        fontsize="14",
        ncol=4,
    )

    # rotate x axis labels by 45 degrees
    # plt.xticks(rotation=15)
    ax.set_xlabel("Scenarios")
else:
    plt.legend(
        title="Number of Shots",
        #    loc="upper left"
    )
plt.tight_layout()
plt.savefig("success_rate_vs_lm.png", dpi=300)


# save the consolidated results to a csv file
consolidated_results = pd.DataFrame(
    {
        "Scenario": tags,
        "Language Model": language_models,
        "Success Rate": success_rates,
    }
)
consolidated_results.to_csv("consolidated_results.csv", index=False)
