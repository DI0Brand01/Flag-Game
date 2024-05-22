import tkinter as tk
from tkinter import ttk
from random import randint
from PIL import Image, ImageTk, ImageFont, ImageDraw
from configparser import ConfigParser


def config_file_error(err_message="Config file is not correct\nexiting..."):
    print(err_message)
    exit(1)


def load_settings() -> dict:
    config = ConfigParser()
    try:
        # Read the INI file
        config.read("config.ini")

        # Define the expected key-value pairs
        expected_pairs = {
            'settings': {'wait_time': '4', 'match_tolerance': '2', 'flag_width': '500', 'flag_height': '300', 'window_title': 'Flag Game', 'correct_guess_points': '1', 'wrong_guess_points': '-1'},
            'styles': {'window_icon': 'flag-icon-filled.ico', 'base_color': '#1f1f1f', 'correctness_image_font_size': '25', 'correctness_image_background_color': '#ff00ff', 'correctness_image_font_color': '#ffffff', 'latest_answer_font_size': '20', 'previous_answer_font_size': '12', 'entry_box_font_size': '16', 'correctness_image_font_type': 'SpaceMono-Regular.ttf'}
        }

        # Check if every key-value pair exists
        for section, key_values in expected_pairs.items():
            if section in config:
                for key in key_values.keys():
                    if key not in config[section]:
                        config_file_error(
                            f"Missing key-value pair in [{section}]")
            else:
                config_file_error(
                    f"Section '{section}' not found in the INI file.")

    except Exception as e:
        config_file_error(e)
    return config


settings = load_settings()


def load_data():
    data = []
    """
    opens a text file containing lots of image path and thier name the line looks like this :
    {number_of_line}#//#path_to_image.gif#//#{name_of_countr}
    """
    try:
        file = open("game.txt", 'r')
        for line in file:
            lst = [i.strip(' \n') for i in line.split('#//#')]
            data.append(lst)
    except Exception as e:
        print("Cant find \"game.txt\"\nexiting")
        exit(1)
    return data


data = load_data()


def levenshtein_distance(s1, s2):
    """
    Calculate the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(string1: str, string2: str, threshold=1):
    """
    Perform fuzzy string matching based on Levenshtein distance.
    Returns True if the distance between the strings is less than or equal to the threshold,
    indicating a match.
    """
    distance = levenshtein_distance(string1.lower(), string2.lower())
    return distance <= threshold


def get_TK_image(path, image_size=(500, 300)):
    image = ImageTk.PhotoImage(Image.open(path).resize(
        (int(settings['settings']['flag_width']), int(settings['settings']['flag_height']))))
    return image


def make_combined_image(image_path, text, font_size=25):
    img = Image.open(image_path).resize(
        (int(settings['settings']['flag_width']), int(settings['settings']['flag_height'])))
    img_width, img_height = img.size

    text_image = Image.new(mode='RGB', size=(
        img_width, 50), color=settings['styles']['correctness_image_background_color'])
    draw = ImageDraw.Draw(text_image)

    font = ImageFont.truetype(
        settings['styles']['correctness_image_font_type'], int(settings['styles']['correctness_image_font_size']))
    draw.text((0, 0), text, fill=settings['styles']
              ['correctness_image_font_color'], font=font)

    new_image_height = img_height + text_image.height
    new_image = Image.new(
        'RGB', (max(img_width, text_image.width), new_image_height))
    new_image.paste(text_image, (0, 0))
    new_image.paste(img, (0, text_image.height))

    new_image_path = "assets/flagGame_2_correctness.png"
    new_image.save(new_image_path)
    return new_image_path, new_image.size


def check_answer(_=False):
    global correct_answer_score, wrong_answer_score, answer_entry
    _, flag_name, flag_path = random_record
    user_answer = user_input.get()
    result = fuzzy_match(user_answer, flag_name, int(
        settings['settings']['match_tolerance']))
    if result:
        update_correct_answer_label(increase_count=int(settings['settings']['correct_guess_points']))
        get_to_next_image()
    else:
        answer_entry.config(state='disabled')
        check_answer_btn.config(state='disabled')
        update_wrong_answer_label(decrease_count=int(settings['settings']['wrong_guess_points']))
        combined_image, combined_image_size = make_combined_image(
            flag_path, f"This is \'{flag_name}\'")
        update_image_label(combined_image, combined_image_size)
        root.after(int(settings['settings']['wait_time'])
                   * 1000, get_to_next_image)


def get_to_next_image():
    _, _, flag_path = get_random_record()
    update_image_label(flag_path)
    user_input.set("")
    answer_entry.config(state='normal')
    check_answer_btn.config(state='normal')


def update_correct_answer_label(increase_count=1):
    global correct_answer_score
    correct_answer_score += increase_count
    correct_answer.set(f"correct answer : {correct_answer_score}")
    correct_answer_lbl.config(
        font=('arial', settings['styles']['latest_answer_font_size']), fg='green')
    wrong_answer_lbl.config(
        font=('arial', settings['styles']['previous_answer_font_size']), fg='white')


def update_wrong_answer_label(decrease_count=1):
    global wrong_answer_score
    wrong_answer_score += decrease_count
    wrong_answer.set(f"wrong answer : {wrong_answer_score}")
    wrong_answer_lbl.config(
        font=('arial', settings['styles']['latest_answer_font_size']), fg='red')
    correct_answer_lbl.config(
        font=('arial', settings['styles']['previous_answer_font_size']), fg='white')


def get_random_record():
    global random_record
    random_record = data[randint(0, len(data) - 1)]
    return random_record


def update_image_label(new_path : str, image_size : tuple =(500, 300)):
    random_image = get_TK_image(new_path, image_size)
    flag_lbl.config(image=random_image)
    flag_lbl.image = random_image

def on_closing():
    root.destroy()

root = tk.Tk()
root.title(settings['settings']['window_title'] + " _ mady by DIO")
root.iconbitmap(settings['styles']['window_icon'])
root.resizable(False, False)
root.configure(bg=settings['styles']['base_color'])
root.protocol('WM_DELETE_WINDOW', on_closing)

global random_record
random_record = get_random_record()

correct_answer_score = 0
correct_answer = tk.StringVar(value=f"correct answer : {correct_answer_score}")
correct_answer_lbl = tk.Label(root, textvariable=correct_answer, font=(
    'arial', 14), fg='white', bg=settings['styles']['base_color'])
correct_answer_lbl.grid(row=0, sticky=tk.W)

wrong_answer_score = 0
wrong_answer = tk.StringVar(value=f"wrong answer : {wrong_answer_score}")
wrong_answer_lbl = tk.Label(root, textvariable=wrong_answer, font=(
    'arial', 14), fg='white', bg=settings['styles']['base_color'])
wrong_answer_lbl.grid(row=0, sticky=tk.E)

frame = tk.Frame(root, bg=settings['styles']['base_color'])
image = get_TK_image(random_record[2])
flag_lbl = tk.Label(frame, image=image)
flag_lbl.pack()

user_input = tk.StringVar()
answer_entry = ttk.Entry(frame, font=('arial', settings['styles']['entry_box_font_size']),
                         justify=tk.CENTER, textvariable=user_input)
answer_entry.focus_set()
answer_entry.pack(pady=5)

check_answer_btn = ttk.Button(frame, text="Check Answer", command=check_answer)
check_answer_btn.pack()

frame.grid(row=1)
root.bind('<Return>', check_answer)
root.mainloop()
