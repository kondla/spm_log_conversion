import csv
import os

input_stimuli_files = ['S04_r1.txt', 'S04_r2.txt']
output_contrasts_files = 'Contrasts_S04'
contrast_input_file = 'Contrast_Definition_Original_short.csv'

os.chdir('/Users/kondla/Dropbox/MA_NeuroIS/Versuch/MA_NeuroIS_Contrast/Original/Design_Matrices')
stimuli_impressions = list()
for file in input_stimuli_files:
    with open(file, 'rt') as txtfile:
        reader = csv.reader(txtfile, delimiter='\n')
        just_names = list(reader)[0]
        reader_string_to_list = csv.reader(just_names, delimiter=',')
        stimuli = list(reader_string_to_list)[0]
        stimuli[0] = stimuli[0][7:]
        stimuli[-1] = stimuli[-1][:-1]
        stimuli = [items.strip("'") for items in stimuli]
        # Turns out, we have to consider additional contrasts that are added to the design matrix, like movement correction
        # Also, constants are a thing. But since the constants are at the end of the Design Matrix, we do not have
        # to include them in the contrasts.
        # These are the movement correction parameters. There are six. How do you find out if you're unsure?
        # Just read the SPM docume.... who am I kidding. Test it yourself by making a test SPM file with the respective
        # regressors (rp*.txt file - if you have not moved it, it is in the folder where you preprocessed the runs).
        for i in range(1, 7):
            stimuli.append(str('movement_correction_' + str(i)))
    stimuli_impressions.extend(stimuli)

os.chdir('/Users/kondla/Dropbox/MA_NeuroIS/Versuch/MA_NeuroIS_Contrast/Original')
with open(contrast_input_file, 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    contrasts_raw = list(reader)

keys = [contrast_names[1] for contrast_names in contrasts_raw[1:]]
left_c_val = [rows[2:11] for rows in contrasts_raw[1:]]
right_c_val = [rows[11:] for rows in contrasts_raw[1:]]

zipped_contrasts = list(zip(keys, left_c_val, right_c_val))
contrasts = {keys_and_contrasts[0]: list(keys_and_contrasts[1:]) for keys_and_contrasts in zip(keys, left_c_val, right_c_val)}

# It is important to only use the stimuli that have _actually_ been recorded. Therefore, we create a list of
# stimuli excluding the ones that did not have an onset.
# This is done in extract_stimuli_impressions_all_runs
# We need to do to contrast definitions separately, because the participants may not see the exact stimuli
# in BOTH runs. E.g. they may only make mistakes in the first run and ace the second run - so they only see the
# feedback_incorrect during the first run and not the second.

# We need to check the contrasts' definitions against the shown/occurred stimuli. From that we create a list.
# If there is a match on the position, there is a 1, if not, there is a 0
# Position is given by the order of the shown stimuli

# Get the all contrasts from the dictionary and split them in
# the left-hand, or positive and right-hand or negative contrasts
left_c_val = [lists[0] for lists in contrasts.values()]
right_c_val = [lists[1] for lists in contrasts.values()]

# Look into the stimuli and match them to the positive contrasts.
# So the contrast value is one (1) at the place in the design matrix where the stimulus coincides with the contrast
spm_contrasts_left = list()
for lists in left_c_val:
    stimulus_temp = list()
    for stimulus in stimuli_impressions:
        if stimulus in lists:
            stimulus_temp.append(1)
        else:
            stimulus_temp.append(0)
    spm_contrasts_left.append(stimulus_temp)

# Look into the stimuli and match them to the negative contrasts.
# So the contrast value is minues one (-1) at the place in the design matrix where the stimulus coincides with the contrast
spm_contrasts_right = list()
for lists in right_c_val:
    stimulus_temp = list()
    for stimulus in stimuli_impressions:
        if stimulus in lists:
            stimulus_temp.append(-1)
        else:
            stimulus_temp.append(0)
    spm_contrasts_right.append(stimulus_temp)

spm_contrasts_RAW = [[sum(pair) for pair in zip(*pairs)] for pairs in zip(spm_contrasts_left, spm_contrasts_right)]

# Now we have the contrasts with all 1s and 0s in the right place relative to the design matrix.
# However, we need the sum of all contrast values to be zero
# To balance the contrast (their sum equalling zero) we compare the number of positive to negative contrast values.
# We then divide by the Kehrwehrt to get a zero

# THIS WEIGHS THE CONTRASTS ACROSS ALL RUNS - not how something occurred over one run only
spm_contrasts = list()
for lists in spm_contrasts_RAW:

    positive_list = list()
    negative_list = list()
    for items in lists:
        if items == 1:
            positive_list.append(1)
        if items == -1:
            negative_list.append(-1)

    final_contrast = list()
    if len(negative_list) == len(positive_list) == 0:
        final_contrast = [items + 99 for items in lists]

    elif len(positive_list) == 0:
        final_contrast = [items + 42 for items in lists]
    elif len(negative_list) == 0:
        final_contrast = [items + 42 for items in lists]

    elif len(positive_list) == len(negative_list):
        final_contrast = lists
    # if there is no comparable contrast, i.e. if there are no stimuli for a certain condition, we kick the contrast
    # we keep the line, however, because in the SPM the contrasts have an index. If we want to compare results, it would
    # throw us off, if we deleted the line
    # Apparently using 0s to fill the line messes up Matlab. Therefore, we need something else. Probs just leave them as is
    # NEED TO BE AWARE OF THAT THOUGH!!!!

    # This is to make sure, that we do not have "empty" contrasts, i.e. no contrasts with only 0s.
    # So SPM does not throw an error.

    # Kehrwert
    elif len(positive_list) > len(negative_list):
        positive_list = [items * len(negative_list) / len(positive_list) for items in positive_list]
        final_contrast = [items * positive_list[0] if items == 1 else items for items in lists]
    elif len(positive_list) < len(negative_list):
        negative_list = [items * len(positive_list) / len(negative_list) for items in negative_list]
        final_contrast = [items * -1 * negative_list[0] if items == -1 else items for items in lists]
    # balanced contrast
    spm_contrasts.append(final_contrast)

# to have it easier, we need to write the contrasts as SPM statements.
# To do so, we take the names from the contrasts dictionary and the contrasts from the spm_contrasts.

matlabbatch_contrasts_keys = str()
matlabbatch_contrasts_session_rep = str()
matlabbatch_contrasts = str()
for counter, key in list(enumerate(contrasts.keys())):
    matlabbatch_contrasts_keys += 'matlabbatch{1}.spm.stats.con.consess{' + str(counter + 1) + '}.tcon.name = \'' + key + '\';' + '\n'
    matlabbatch_contrasts_session_rep += 'matlabbatch{1}.spm.stats.con.consess{' + str(counter + 1) + '}.tcon.sessrep = \'none\';' + '\n'
for counter, contrast, in list(enumerate(spm_contrasts)):
    matlabbatch_contrasts += 'matlabbatch{1}.spm.stats.con.consess{' + str(counter + 1) + '}.tcon.weights = ' + str(contrast) + ';' + '\n'

os.chdir('/Users/kondla/Dropbox/MA_NeuroIS/Versuch/MA_NeuroIS_Contrast/Original/Contrasts')
with open(output_contrasts_files, 'wt') as file:
        file.write(matlabbatch_contrasts_keys)
        file.write(matlabbatch_contrasts)
        file.write(matlabbatch_contrasts_session_rep)
        file.write('matlabbatch{1}.spm.stats.con.delete = 1;')
