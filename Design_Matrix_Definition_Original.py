import csv
import os


input_log_file = 'S01-fMRI_paradigm.csv'
output_Design_Matrix_file = 'S01_r1.txt'


ignore = ['0', '1', '2', '3', '4', '5', '99', 'start_wait']

trials = {
    'questions_Easy': (list(), list()),
    'questions_Medium': (list(), list()),
    'questions_Difficult': (list(), list()),

    'questions_errorImage': (list(), list()),

    'feedback_hit_Easy': (list(), list()),
    'feedback_hit_Medium': (list(), list()),
    'feedback_hit_Difficult': (list(), list()),

    'feedback_incorrect_Easy': (list(), list()),
    'feedback_incorrect_Medium': (list(), list()),
    'feedback_incorrect_Difficult': (list(), list()),

    'feedback_miss_Easy': (list(), list()),
    'feedback_miss_Medium': (list(), list()),
    'feedback_miss_Difficult': (list(), list()),

    'feedback_alternate_hit_Easy': (list(), list()),
    'feedback_alternate_missed_Easy': (list(), list()),
    'feedback_alternate_incorrect_Easy': (list(), list()),

    'feedback_alternate_hit_Medium': (list(), list()),
    'feedback_alternate_missed_Medium': (list(), list()),
    'feedback_alternate_incorrect_Medium': (list(), list()),

    'feedback_alternate_hit_Difficult': (list(), list()),
    'feedback_alternate_missed_Difficult': (list(), list()),
    'feedback_alternate_incorrect_Difficult': (list(), list()),

    'choices_Easy': (list(), list()),
    'choices_selected_l': (list(), list()),
    'choices_selected_m': (list(), list()),
    'choices_selected_r': (list(), list()),
    'choices_Medium': (list(), list()),
    'choices_Difficult': (list(), list()),
    'feedback_errorcorrect_Easy': (list(), list()),
    'feedback_errorcorrect_Medium': (list(), list()),
    'feedback_errorcorrect_Difficult': (list(), list()),
    'isi_1': (list(), list()),
    'isi_2': (list(), list()),
    'tlx_1': (list(), list()),
    'tlx_1_selected_1': (list(), list()),
    'tlx_1_selected_2': (list(), list()),
    'tlx_1_selected_3': (list(), list()),
    'tlx_1_selected_4': (list(), list()),
    'tlx_1_selected_5': (list(), list()),
    'tlx_2': (list(), list()),
    'tlx_2_selected_1': (list(), list()),
    'tlx_2_selected_2': (list(), list()),
    'tlx_2_selected_3': (list(), list()),
    'tlx_2_selected_4': (list(), list()),
    'tlx_2_selected_5': (list(), list()),
    'tlx_3': (list(), list()),
    'tlx_3_selected_1': (list(), list()),
    'tlx_3_selected_2': (list(), list()),
    'tlx_3_selected_3': (list(), list()),
    'tlx_3_selected_4': (list(), list()),
    'tlx_3_selected_5': (list(), list()),
    'tlx_4': (list(), list()),
    'tlx_4_selected_1': (list(), list()),
    'tlx_4_selected_2': (list(), list()),
    'tlx_4_selected_3': (list(), list()),
    'tlx_4_selected_4': (list(), list()),
    'tlx_4_selected_5': (list(), list()),
    'tlx_5': (list(), list()),
    'tlx_5_selected_1': (list(), list()),
    'tlx_5_selected_2': (list(), list()),
    'tlx_5_selected_3': (list(), list()),
    'tlx_5_selected_4': (list(), list()),
    'tlx_5_selected_5': (list(), list())
}


def get_difficulty(ele):
    try:
        number = int(ele.split('_')[-1])
    except ValueError:
        print(ele)
        return
    if number <= 48:
        return 'Easy'
    elif 49 <= number <= 96:
        return 'Medium'
    else:
        return 'Difficult'


input_path = "/Users/kondla/Dropbox/MA_NeuroIS/Versuch/MA_NeuroIS_Contrast/Logs"
os.chdir(input_path)

with open(input_log_file, 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    data = list(reader)
    data = data[5:]

offset = int(data[0][4])
element = None
previous_error_in_block = 0
time = None
onset = None
duration = None

for d in data[1:]:
    if d[3][:9] == 'questions' and len(d[3]) <= 14:
        element = 'questions_' + get_difficulty(d[3])
    elif d[3][:7] == 'choices' and len(d[3]) <= 12:
        element = 'choices_' + get_difficulty(d[3])
    elif d[3][:12] == 'feedback_hit':
        element = 'feedback_hit_' + get_difficulty(d[3])
    elif d[3][:13] == 'feedback_miss':
        element = 'feedback_miss_' + get_difficulty(d[3])
    elif d[3][:18] == 'feedback_incorrect':
        element = 'feedback_incorrect_' + get_difficulty(d[3])
    elif d[3][:20] == 'questions_errorImage':
        element = 'questions_errorImage'
    elif d[3][:22] == 'feedback_alternate_hit':
        element = 'feedback_alternate_hit_' + get_difficulty(d[3])
    elif d[3][:25] == 'feedback_alternate_missed':
        element = 'feedback_alternate_missed_' + get_difficulty(d[3])
    elif d[3][:28] == 'feedback_alternate_incorrect':
        element = 'feedback_alternate_incorrect_' + get_difficulty(d[3])
    # that is just a recoding for the participant by chance selecting the right answer after an errorImage
    elif d[3][:21] == 'feedback_errorcorrect':
        element = 'feedback_incorrect_' + get_difficulty(d[3])

    elif d[3] in ignore:
        element = None
    elif d[3] not in ignore:
        element = d[3]

    if element:
        time = int(d[4])
        onset = (time - offset) / 10000
        trials[element][0].append(onset)
        duration = int(d[7]) / 10000
        trials[element][1].append(duration)


names_list = 'names={'
onset_list = 'onsets={'
duration_list = 'durations={'

for k in trials.keys():
    onsets = trials[k][0]
    if len(onsets) > 0:
        durations = trials[k][1]
        names_list += '\''
        names_list += k
        names_list += '\','
        onset_list += str(onsets)
        onset_list += '\','
        duration_list += str(durations)
        duration_list += '\','

names_list = names_list[:-1]
names_list += '}'
duration_list = duration_list[:-1]
duration_list += '}'
onset_list = onset_list[:-1]
onset_list += '}'

output_path = "/Users/kondla/Dropbox/MA_NeuroIS/Versuch/MA_NeuroIS_Contrast/Original/Design_Matrices"
os.chdir(output_path)

with open(output_Design_Matrix_file, 'wt') as f:
    f.write(names_list)
    f.write('\n')
    f.write(duration_list)
    f.write('\n')
    f.write(onset_list)
    f.write('\n')