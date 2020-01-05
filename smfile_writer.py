import math
import os
from os.path import isfile, join, isdir, dirname, realpath
from collections import defaultdict
import re
import time
import argparse

def format_file_name(f):
    name = "".join(f.split('.')[:-1]).lower()                               #lowercase; splits by period; keeps extension
    formatted = re.sub('[^a-z0-9-_ ]', '', name)                            #ignores special characters, except - and _
    return re.sub(' ', '_', formatted)

def output_file(file_name, x, output_dir):
    ofile = file_name + '.sm'
    index = 0

    with open(join(output_dir, ofile), "w") as f:
        f.write("#TITLE:" + str(x['title']) + ";\n")
        f.write("#ARTIST:jhaco vs cpuguy96;\n")
        f.write("#MUSIC:" + file_name + ".ogg;\n")
        f.write("#SELECTABLE:YES;\n")
        f.write("#BPMS:0.000=" + str(x['BPM']) + ";\n\n")
        f.write("//---------------dance-single - ----------------\n")
        f.write("#NOTES:\n")
        f.write("     dance-single:\n")
        f.write("     :\n")
        f.write("     Hard:\n")
        f.write("     8:\n")
        f.write("     1.000,1.000,1.000,1.000,1.000:\n")
        for n in x['notes']:
            if n == 0:
                f.write("0000\n")
            elif n == 1:
                f.write(str(x['types'][index]) + "\n")
                index+=1
            elif n == ',' or n == ';':
                f.write(n + "\n")

#=================================================================================================

#BPM = beats/minute -> BPS = beats/second = BPM/60
#measure = 4 beats = 4 1/4th notes = 1
#1/192 >  1 measure = 256 1/256nd notes
#after calculating and approximating each measure in 192 beats use trim() to reduce to 1/X and append and then append a comma at the end
#find notes that fit within the measure interval and calculate the trimmed measure off of that
#if last measure, instead of comma, append a semicolon
#4, 8, 16, 32, 64, 128, 256

#128 = every 2nd step; 64 = every 4th; 32 = 8th; 16 = 16th; 8 = 32th; 4 = 64th; 2 to power of 0, 1, 2, 3, 4, 5

def trim_measure(trim):
    position = [] 
    n = 0

    for i in range(len(trim)):
        if trim[i] == 1:
            position.append(i+1)

    for pow in range(6):
        flag = True
        for p in position:
            if int(p%(2**pow)) != 0:                             #if note does not fit, go next
                flag = False
        if flag:
            n = pow

    k = [0]*int(256/(2**n))
    for p in position:
        f = int(p/(2**n))-1
        k[f] = 1

    return k

def calculate_measure(measure, timing):
    trim    = []

    if not measure:
        trim = [0,0,0,0,',']
    else:
        trim = [0] * 256
        for note in measure:
            n   = 0
            min = 10.0
            for i in range(len(trim)):
                diff = abs(note - i*timing)
                if diff <= min:
                    n = i
                    min = diff
            trim[n] = 1
        trim = trim_measure(trim)
        trim.append(',')
    return trim

def calculate_notes(x):
    measure_sec     = round(4 * 60/x['BPM'], 10)                                                       #measure in seconds = 4 x seconds per beat
    measure_all     = math.ceil(x['timings'][-1]/measure_sec)                                          #number of measures that fits the whole song
    note_256        = round(measure_sec/256, 5)                                                     #time of notes in seconds

    for i in range(measure_all):
        measure = []
        for j in x['timings']:
            if((i * measure_sec) <= j < ((i+1) * measure_sec)):
                measure.append(round(j-(i*measure_sec), 5))
        x['notes'].extend(calculate_measure(measure, note_256))
    x['notes'][-1] = ';'

def parse_txt(txt_file):
    step_dict = defaultdict(list)

    with open(txt_file, 'r', encoding='ascii', errors='ignore') as f:                                      #ignores non-ASCII text (ex. Japanese)      
        for line in f:                                                                              #reads by line           
            if line.startswith('TITLE'):                                                            #title
                step_dict['title'] = line.rstrip('\n').lstrip('TITLE ')
            if line.startswith('BPM'):                                                             #BPM
                step_dict['BPM']   = float(line.rstrip('\n').lstrip('BPM '))
            if line[0].isdigit():
                num = line.rstrip('\n').split(' ')
                step_dict['types'].append(num[0])
                step_dict['timings'].append(float(num[1]))
    
    calculate_notes(step_dict)
    return step_dict

def parse(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        txt_files = [file for file in files if file.endswith('.txt')]
    
        for txt_file in txt_files:
            new_file = format_file_name(txt_file)
            try:
                txt_data = parse_txt(join(root, txt_file))
                # write text sm data to output dir
                output_file(new_file, txt_data, output_dir)
            except Exception as ex:
                print('Write failed for %s: %r' % (txt_file, ex))

#=================================================================================================

if __name__ == '__main__':
    start_time = time.time()

    dir = dirname(realpath(__file__))
    writer = argparse.ArgumentParser(description='Parser')
    writer.add_argument('--input', default='writeIn', help='Provide an input folder (default: parseIn)')
    writer.add_argument('--output', default='writeOut', help='Provide an output folder (default: parseOut)')

    args = writer.parse_args()
    input_dir  = join(dir, args.input)
    output_dir = join(dir, args.output)

    if not isdir(input_dir):
        print("Invalid input directory argument.")
    else:
        if not isdir(output_dir):
            print("Output directory missing: " + args.output + " \nGenerated specified output folder.")
            os.makedirs(output_dir)
        parse(input_dir, output_dir)

    end_time = time.time()

    print("Elapsed time was %g seconds" % (end_time - start_time))
