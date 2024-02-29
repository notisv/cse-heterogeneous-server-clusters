import sys

def parseSimulationParameters(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            #print(lines)
            sim_time = int(lines[5]) + 7200
            algo = lines[6].strip()
            thresholds = list(int(threshold) for threshold in lines[7].split(','))
            trials = int(lines[8])
            #print(sim_time)
            #print(algo)
            #print(thresholds)
            #print(trials)
            return sim_time, algo, thresholds, trials

    except FileNotFoundError as e:
        print('Cannot open ' + filename + '. Quitting...')
        sys.exit()