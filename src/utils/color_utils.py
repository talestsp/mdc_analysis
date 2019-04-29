import seaborn as sns
import random

def pick_random_color():
    palette = sns.color_palette("bright")
    random_n = random.randint(0, len(palette))

    return palette[random_n]

