import math
from os import listdir, rename
from os.path import isfile, join

class Note():
    title   = "empty"
    BPM     = 0.0
    types   = []
    timings = []
    notes   = []

def get_file_names(mypath):                                                                         #lists all files in specified directory
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def format(src):
    dst = '_'.join(src.split()).split('.')[0].lower()
    return "".join(e for e in dst if e not in '()[]@!?#$%^&*\',')

#=================================================================================================

def parse_txt(n):
    x = Note()

    with open(n, 'r', encoding='ascii', errors='ignore') as f:                                      #ignores non-ASCII text (ex. Japanese)      
        for line in f:                                                                              #reads by line
           
            if line.startswith('TITLE'):                                                            #title
                x.title = line.rstrip('\n').lstrip('TITLE ')

            if line.startswith('BPM'):                                                             #BPM
                x.BPM   = float(line.rstrip('\n').lstrip('BPM '))

            if line[0].isdigit():
                nstr = line.rstrip('\n').split(' ')
                x.types.append(nstr[0])
                x.timings.append(float(nstr[1]))
    
    return x

#BPM = beats/minute -> BPS = beats/second = BPM/60
#measure = 4 beats = 4 1/4th notes = 1
#1/192 >  1 measure = 192 1/192nd notes
#after calculating and approximating each measure in 192 beats use trim() to reduce to 1/X and append and then append a comma at the end
#find notes that fit within the measure interval and calculate the trimmed measure off of that
#if last measure, instead of comma, append a semicolon
#4, 8, 16, 24, 32, 48, 64, 96, 192

def trim(p, base):
    trim    = []

    if not p:
        trim = [0,0,0,0,',']
    else:
        trim = [0] * 192
        for x in p:
            n   = 0
            min = 10.0
            for i in range(len(trim)):
                diff = abs(x - i*base)
                if diff <= min:
                    n = i
                    min = diff
            trim[n] = 1
        trim.append(',')
    return trim

def measure(x):
    measure_sec     = round(4 * 60/x.BPM, 10)                                                       #measure in seconds = 4 x seconds per beat
    measure_all     = math.ceil(x.timings[-1]/measure_sec)                                          #number of measures that fits the whole song
    note_192        = round(measure_sec/192, 5)                                                    #time of notes in seconds
    #print(measure_sec)
    #print(note_192)
    #c = 0

    for i in range(measure_all):
        p = []
        for j in x.timings:
            if((i * measure_sec) <= j < ((i+1) * measure_sec)):
                p.append(round(j-(i*measure_sec), 5))
                #c += 1
        #print(p)
        x.notes.extend(trim(p, note_192))
    del x.notes[-1]
    x.notes.append(';')
    #print(c)

#=================================================================================================

def output_file(n, x):
    d = format(n) + '.sm'
    c = 0

    with open(d, "w") as f:
        f.write("#TITLE:" + str(x.title) + ";\n")
        f.write("#ARTIST:jhaco vs cpuguy96;\n")
        f.write("#MUSIC:" + format(n) + ".ogg;\n")
        f.write("#SELECTABLE:YES;\n")
        f.write("#BPMS:0.000=" + str(x.BPM) + ";\n\n")
        f.write("//---------------dance-single - ----------------\n")
        f.write("#NOTES:\n")
        f.write("     dance-single:\n")
        f.write("     :\n")
        f.write("     Hard:\n")
        f.write("     8:\n")
        f.write("     1.000,1.000,1.000,1.000,1.000:\n")
        for n in x.notes:
            if n == 0:
                f.write("0000\n")
            if n == 1:
                f.write(str(x.types[c]) + "\n")
                c+=1
            if n == ',':
                f.write(n + "\n")
            if n == ';':
                f.write(n + "\n")


#=================================================================================================
#MAIN
for f in get_file_names("./"):
    if f.endswith(".txt"):
        #try:
        x = parse_txt(f)
        measure(x)
        output_file(f,x)
        #except Exception:
            #print("Conversion failed: " + f)
            #pass
        #print(x.notes)
        #print(len(x.types))
        #print(len(x.timings))
        x.notes.clear()
        x.types.clear()
        x.timings.clear()
