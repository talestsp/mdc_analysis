import seaborn as sns
import random

def pick_random_color():
    palette = sns.color_palette("bright").as_hex()
    random_n = random.randint(0, len(palette) - 1)

    return palette[random_n]

