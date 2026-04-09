import os # for listing event logs in the file system
import pandas # for collecting data
import pm4py # for importing event logs
import Constants
from modelcomplexity import ModelComplexityMeasures
from discovery import DiscoveryAlgorithms

def discover_and_collect_complexity_scores(miners: list, measures: list):
    header = [] # for collecting the name of each column, i.e., the names of complexity scores.
    collected_data = [] # for collecting the complexity scores that each selected measure returns.
    filenames = [] # for collecting the name of each row, i.e., the names of each file and miner.
    iteration = 1 # for printing how many iterations were successful so far.
    # process each file in the specified folder.
    for file in os.listdir(Constants.INPUT_PATH):
        # make sure that we only consider event log files in XES format.
        full_file_path = os.path.join(Constants.INPUT_PATH, file)
        if os.path.isfile(full_file_path) and file.endswith(".xes"):
            # tell the user which file is currently being processed.
            print("Parsing XES file " + str(iteration) + " (" + str(file) + "):")
            # import the XES file into the program.
            event_log = pm4py.read_xes(full_file_path)
            # go through all of the selected miners to discover Petri nets.
            for miner in miners:
                net, im, fm = miner.discover_for(event_log)
                filenames += ["(" + str(os.path.basename(file)) + "," + str(miner) + ")"]
                # prepare a list to callect all complexity scores and their names.
                header = []
                data = []
                # go through all chosen complexity measures.
                for measure in measures:
                    # add the name of the complexity measure to the header.
                    header += [str(measure)]
                    # if the current measure is depth or diameter, pass not only
                    # the net, but also the initial and final marking to the mehtod
                    # calculating the complexity score.
                    if measure in [ModelComplexityMeasures.Depth(), ModelComplexityMeasures.Diameter()]:
                        data += [measure.calculate_for(net, im, fm)]
                    # otherwise just pass the net for calculation.
                    else:
                        data += [measure.calculate_for(net)]
                # append the collected data to the full list of complexity scores.
                collected_data += [data]
            iteration += 1
    complexity = pandas.DataFrame(collected_data, index=filenames, columns=header)
    complexity.to_csv(Constants.OUTPUT_PATH + "complexity_scores.csv", mode='w', encoding='utf-8')
    return complexity, iteration-1
