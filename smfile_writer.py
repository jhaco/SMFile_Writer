from collections import defaultdict, deque
from math import ceil
from os import makedirs, walk
from os.path import join, isdir, dirname, realpath
from re import sub, split
from shutil import copyfile
import argparse
import time

def format_file_name(f):    #formats file name to ASCII
    name = "".join(f.split('.')[:-1]).lower()   #lowercase; splits by period; removes extension
    formatted = sub('[^a-z0-9-_ ]', '', name)    #ignores special characters, except - and _
    return sub(' ', '_', formatted)  #replaces whitespace with _

def output_file(file_name, step_dict, output_dir):
    ofile = file_name + '.sm'

    with open(join(output_dir, ofile), 'w') as f:
        f.write('#TITLE:%s;\n' % step_dict['title'])
        f.write('#ARTIST:jhaco vs cpuguy96;\n')
        f.write('#MUSIC:%s.ogg;\n' % file_name)
        f.write('SELECTABLE:YES;\n')
        f.write('BPMS:0.000=%s;\n\n' % str(step_dict['bpm']))
        for difficulty in step_dict['notes'].keys():
            f.write('//---------------dance-single - ----------------\n')
            f.write('#NOTES:\n')
            f.write('     dance-single:\n')
            f.write('     :\n')
            f.write('     %s:\n' % difficulty)
            f.write('     8:\n')
            f.write('     1.000,1.000,1.000,1.000,1.000:\n')
            for note in step_dict['notes'][difficulty]:
                f.write(note + '\n')

#===================================================================================================

def compress_measure(measure, note_positions):
    nth_power = 0

    # tries to fit 128, 64, 32, 16, 8 or 4 note measures; skips 256, since that is already true
    for power in range(1, 7):
        can_compress = True
        for p in note_positions:
            if int(p%(2**power)) != 0:
                can_compress = False
                break
        if can_compress:
            nth_power = power
        else:
            break
    
    # if fitting fails, returns measure unchanged
    if nth_power == 0:
        return measure

    # place notes in compressed measure
    compressed_measure = ['0000']*int(256/(2**nth_power))
    for p in note_positions:
        new_p = int(p/(2**nth_power))-1
        compressed_measure[new_p] = measure[p-1]

    return compressed_measure

def generate_measure(notes, timings, note_256):
    if not notes or not timings: # no notes in current measure
        return ['0000','0000','0000','0000',',']
    
    measure = ['0000'] * 256
    note_positions = []
    for note, time in enumerate(timings):
        note_position = 0
        min_error = 5.0 # edge case: might need to adjust for really slow songs
        for i in range(len(measure)):
            error = abs(time - i*note_256)
            if error <= min_error: # narrows down note position based on timing difference
                note_position = i
                min_error = error
            else:
                break # stops finding note position once found
        measure[note_position] = notes[note]
        note_positions.append(note_position+1)
    measure = compress_measure(measure, note_positions)
    measure.append(',')

    return measure

def place_notes(notes_and_timings, bpm):
    placed_notes = []
    if not notes_and_timings:
        return placed_notes

    seconds  = round(4 * 60/bpm, 10) # length of measure in seconds
    total_time = float(notes_and_timings[-1].split()[1])
    total_measures = ceil(total_time/seconds)
    note_256 = round(seconds/256, 5)
    
    for measure in range(total_measures):
        notes = []   # contains notes that fit current measure
        timings = [] # contains timings that fit current measure
        while notes_and_timings: # while queue is not empty
            note_timing = notes_and_timings[0].split()
            note = note_timing[0]
            timing = float(note_timing[1])
            if((measure * seconds) <= timing < ((measure+1) * seconds)):
                notes.append(note)
                timings.append(round(timing - (measure * seconds), 5))
                notes_and_timings.popleft()
            else:
                break
        placed_notes.extend(generate_measure(notes, timings, note_256))

    placed_notes[-1] = ';'
    return placed_notes

def parse_txt(txt_file):
    step_dict = defaultdict(list)
    step_dict['notes'] = defaultdict(list)
    current_difficulty = ''
    notes_and_timings = deque()

    read_notes = False

    with open(txt_file, encoding='ascii', errors='ignore') as f:
        for line in f:
            line = line.rstrip()
            if not read_notes:
                if line.startswith('NOTES'):
                    read_notes = True
                else:
                    metadata = line.split() # splits name from values by whitespace
                    data_name = metadata[0]
                    data_value = ' '.join(metadata[1:])
                    if data_name == 'TITLE':
                        step_dict['title'] = data_value
                    elif data_name == 'BPM':
                        step_dict['bpm'] = float(data_value)
            else:
                if line.startswith('DIFFICULTY'):
                    if notes_and_timings:
                        notes = place_notes(notes_and_timings, step_dict['bpm'])
                        step_dict['notes'][current_difficulty].extend(notes)
                        notes_and_timings.clear()
                    current_difficulty = line.split()[1]
                else:
                    notes_and_timings.append(line)
        notes = place_notes(notes_and_timings, step_dict['bpm'])
        step_dict['notes'][current_difficulty].extend(notes)
    return step_dict

#===================================================================================================

def parse(input_dir, output_dir):
    for root, dirs, files in walk(input_dir):
        txt_files = [file for file in files if file.endswith('.txt')]
        ogg_files = [file for file in files if file.endswith('.ogg')]

        format_ogg_dict = dict(zip([format_file_name(ogg) for ogg in ogg_files], range(len(ogg_files))))

        for txt_file in txt_files:
            new_file = format_file_name(txt_file)
            try:
                txt_data = parse_txt(join(root, txt_file))
                # creates new folder for successfully parsed data
                output_folder = output_dir + '/' + new_file
                if not isdir(output_folder):
                    makedirs(output_folder)
                # write text sm data to output dir
                output_file(new_file, txt_data, output_folder)
            except Exception as ex:
                print('Write failed for %s: %r' % (txt_file, ex))
            try:
                # move and rename .ogg file to output dir
                copyfile(join(root, ogg_files[format_ogg_dict[new_file]]), join(output_folder, new_file + '.ogg'))
            except Exception as ex:
                print('Sound file not found for %s' % (new_file))

#=================================================================================================

if __name__ == '__main__':
    start_time = time.time()

    dir = dirname(realpath(__file__))
    writer = argparse.ArgumentParser(description='Writer')
    writer.add_argument('--input', default='writeIn', help='Provide an input folder (default: writeIn)')
    writer.add_argument('--output', default='writeOut', help='Provide an output folder (default: writeOut)')

    args = writer.parse_args()
    input_dir  = join(dir, args.input)
    output_dir = join(dir, args.output)

    if not isdir(input_dir):
        print("Invalid input directory argument.")
    else:
        if not isdir(output_dir):
            print("Output directory missing: " + args.output + " \nGenerated specified output folder.")
            makedirs(output_dir)
        parse(input_dir, output_dir)

    end_time = time.time()

    print("Elapsed time was %g seconds" % (end_time - start_time))
