from configparser import ConfigParser

config = ConfigParser()

config['settings'] = {
    'wait_time': 4,
    'match_tolerance': 2,
    'flag_width': 500,
    'flag_height': 300,
    'window_title': 'Flag Game',
    'correct_guess_points': 1,
    'wrong_guess_points': 1
}

config['styles'] = {
    'window_icon': 'assets/flag-icon-filled.ico',
    'base_color': '#1f1f1f',
    'correctness_image_font_size': 25,
    'correctness_image_font_type': 'assets/SpaceMono-Regular.ttf',
    'correctness_image_background_color': '#ff00ff',
    'correctness_image_font_color': '#ffffff',
    'latest_answer_font_size': 20,
    'previous_answer_font_size': 12,
    'entry_box_font_size': 16
}

with open('config.ini', 'w') as file:
    config.write(file)
