import ciw
import parsefiles
import sys
import numpy
import math
from scipy import stats
import random

global min_wait_time
min_wait_time = float("inf")
global min_wait_time_threshold
min_wait_time_threshold = -1

global max_util
max_util = float("-inf")
global max_util_threshold
max_util_threshold = -1

class RoutingDecision0(ciw.Node):
    def next_node(self, ind):
        nodes = self.simulation.nodes
        
        min_node = nodes[2]
        for i in range (3, 10):
            if nodes[i].number_of_individuals < min_node.number_of_individuals: min_node = nodes[i]

        return min_node

class RoutingDecision1(ciw.Node):
    def next_node(self, ind):
        busyness = {nodeID: self.simulation.nodes[nodeID].number_of_individuals for nodeID in range(2, 10)}
        chosen_nodeID = sorted(busyness.keys(), key = lambda id: busyness[id])[0]

        return self.simulation.nodes[chosen_nodeID]

class RoutingDecision2(ciw.Node):
    def next_node(self, ind):
        nodes = self.simulation.nodes
        #print("----")
        busyness = {nodeID: self.simulation.nodes[nodeID].number_of_individuals for nodeID in range(2, 10)}
        #print(busyness)
        #for nodeID in busyness.keys():
        #    if nodes[nodeID].number_of_individuals > 1: print('Node ' + str(nodeID) + ' has more than 1 customers: ' + str(nodes[nodeID].number_of_individuals))
        sorted_nodeIDs_by_busyness = sorted(busyness.keys(), key = lambda id: busyness[id])   
        #print(sorted_nodeIDs_by_busyness)

        #random.shuffle(sorted_nodeIDs_by_busyness)

        if sorted_nodeIDs_by_busyness[0] > 6: # fast node
            #print('fast node selected')
            return nodes[sorted_nodeIDs_by_busyness[0]]
        else:
            #print('didnt find fast node - trying again until one is found')
            for i in range (1, 8):
                #print("Node:", sorted_nodeIDs_by_busyness[i])
                if sorted_nodeIDs_by_busyness[i] > 6:
                    #if nodes[sorted_nodeIDs_by_busyness[i]].number_of_individuals > 1: print('Node ' + str(sorted_nodeIDs_by_busyness[i]) + ' has ' + str(nodes[sorted_nodeIDs_by_busyness[i]].number_of_individuals) + ' customers')
                    if nodes[sorted_nodeIDs_by_busyness[i]].number_of_individuals - threshold > nodes[sorted_nodeIDs_by_busyness[0]].number_of_individuals:
                        return nodes[sorted_nodeIDs_by_busyness[i]]
                    else:
                        break
            
            return nodes[sorted_nodeIDs_by_busyness[0]]

def getClass(classname):
    return getattr(sys.modules[__name__], classname)

def calculate_standard_deviation(elapsedTrials, avg_waits, avg_wait_time):
    sum_of_squares_waits = 0

    for trial in range(elapsedTrials):
        sum_of_squares_waits += (avg_waits[trial] - avg_wait_time) ** 2

    variance_waits = sum_of_squares_waits / elapsedTrials

    sd_wait = math.sqrt(variance_waits)

    return sd_wait

def calculate_conf_interval(ci, elapsedTrials, sd_wait, avg_wait_time):

    # for small samples (<50) we use t-statistics
    # trials, degrees of freedom = trials - 1
    # for 99% confidence interval, alpha = 1% = 0.01 and alpha/2 = 0.005
    # for 95% confidence interval, alpha = 5% = 0.05 and alpha/2 = 0.025
    # for 90% confidence interval, alpha = 10% = 0.1 and alpha/2 = 0.5
    global alpha
    if ci == 99: alpha = 0.05
    if ci == 95: alpha = 0.05
    if ci == 90: alpha = 0.1

    df = elapsedTrials - 1 # degrees of freedom - step1
    
    # ci % confidence level - step2

    tDistr_res = stats.t.ppf(1- ((100-ci)/2/100), df) # step3

    step4 = sd_wait / math.sqrt(elapsedTrials)

    step5 = tDistr_res * step4

    conf95_wait_upper = avg_wait_time + step5 # Upper tail probability
    
    conf95_wait_lower = avg_wait_time - step5 # Lower tail probability

    #print(conf95_wait_upper, conf95_wait_lower)

    return conf95_wait_upper, conf95_wait_lower

def simulation():
    global moreRunsNeeded
    moreRunsNeeded = True

    avg_waits = []
    avg_services = []
    avg_total_utils = []
    avg_node_utils = []

    #print('\n////////////////////')
    #print('Threshold value: %i - Max trials: %i' % (threshold, max_trials))

    for trial in range(max_trials):
        ciw.seed(trial)

        #print('\nTrial %i' % trial)

        if not moreRunsNeeded == True: break

        global Q
        Q = ciw.Simulation(
            ciw.create_network_from_yml('network_params.yml'), tracker = ciw.trackers.NodePopulation(),
            node_class = [getClass(algo), ciw.Node, ciw.Node, ciw.Node, ciw.Node, ciw.Node, ciw.Node, ciw.Node, ciw.Node])
        Q.simulate_until_max_time(sim_time) # 1hr warmup, sim_time hr data capture, 1hr cooldown
        
        records = Q.get_all_records()

        waits = [r.waiting_time for r in records if r.arrival_date > 3600 and r.arrival_date < (sim_time - 3600)]
        mean_wait = sum(waits) / len(waits)
        avg_waits.append(mean_wait)

        services = [r.service_time for r in records if r.arrival_date > 3600 and r.arrival_date < (sim_time - 3600)]
        mean_service = sum(services) / len(services)
        avg_services.append(mean_service)

        utils = [node.server_utilisation for node in Q.transitive_nodes]
        mean_util = sum(utils) / len(utils)
        avg_total_utils.append(mean_util)

        utils = [node.server_utilisation for node in Q.transitive_nodes]
        avg_node_utils.append(utils)

        if trial > 1:

            # Check if more runs are needed
            # if conf_interval / avg_of_chosen_metric < error: moreRunsNeeded = False

            avg_wait_time = sum(avg_waits) / len(avg_waits)

            sd_wait = calculate_standard_deviation(trial, avg_waits, avg_wait_time)
            #print('\nStandard deviation across %i trials:' % trial)
            #print('Avg wait standard deviation: %f' % sd_wait)

            ci = 90 # confidence interval
            conf_wait_upper, conf_wait_lower = calculate_conf_interval(ci, trial, sd_wait, avg_wait_time)
            conf_wait = conf_wait_upper
            #print('\n%.1f-percent confidence interval across %i trials:' % (ci ,trial))
            #print('Avg wait %.1f-percent confidence interval: %f' % (ci , conf_wait))

            # Check if more runs are needed
            #print('\nconf_interval_wait / avg_wait_time = %f' % (conf_wait / avg_wait_time))
            if conf_wait / avg_wait_time < alpha: moreRunsNeeded = False
           
    print('\n////////////////////')
    print('Algo:', algo)
    if 'threshold' in globals(): print('Threshold value:', threshold)

    #print('Average waits per trial:', avg_waits)
    avg_wait_time = sum(avg_waits) / len(avg_waits)
    print('Avg wait time(ms):', "{:.3f}".format(avg_wait_time * 1000))

    #print('Average services per run:', avg_services)
    avg_service_time = sum(avg_services) / len(avg_services)
    #print('Avg service time(ms):', "{:.3f}".format(avg_service_time * 1000))
    avg_service_rate = 1 / avg_service_time
    print('Avg service rate(services/second):', "{:.3f}".format(avg_service_rate * 100))

    #print('Average total utils per trial:', avg_total_utils)
    avg_total_util = sum(avg_total_utils) / len(avg_total_utils)
    print('Avg total node util(percentage):', "{:.3f}".format(avg_total_util * 100))

    #print(avg_node_utils)
    sums = numpy.sum(avg_node_utils, 0)
    avg_node_util = [(sum / max_trials) for sum in sums]
    avg_node_util_percent = ["{:.3f}".format(util * 100) for util in avg_node_util]
    #print('Avg node util(percentage):', avg_node_util_percent)
    avg_node_util_percent_map = dict(zip(Q.transitive_nodes, avg_node_util_percent))
    print('Avg node util(percentage):', avg_node_util_percent_map)

    print('////////////////////')

    if 'threshold' in globals():
        global min_wait_time
        global min_wait_time_threshold
        if (avg_wait_time < min_wait_time):
            min_wait_time = avg_wait_time
            min_wait_time_threshold = threshold
        
        global max_util
        global max_util_threshold
        if (avg_total_util > max_util):
            max_util = avg_total_util
            max_util_threshold = threshold

def finalizeSimulationResults():
    try:
        with open('simulation_results.txt', 'r+') as file:
            lines = file.readlines()
            file.seek(0)

            file.write('System Description:\n')
            file.write('Node network: ' + str(Q.nodes) + '\n')
            file.write('Transitive node network: ' + str(Q.transitive_nodes) + '\n')
            file.write('Arrival distributions and rates for each transitive node and customer class: ' + str(Q.inter_arrival_times) + '\n')
            file.write('Service distributions and rates for each transitive node and customer class: ' + str(Q.service_times) + '\n')
            file.write('Number of servers per transitive node: ')
            for node in Q.transitive_nodes: file.write('[Node '+ str(node.id_number) + ': ' + str(node.c) + '] ')
            file.write('\n')
            file.write('Queueing capacity per transitive node: ')
            for node in Q.transitive_nodes: file.write('[Node '+ str(node.id_number) + ': ' + str(node.node_capacity) + '] ')
            file.write('\n')
            file.write('Routing table:\n')
            for node in Q.transitive_nodes: file.write(str(node.transition_row) + '\n')

            #file.write('\n')
            file.writelines(lines)
    except FileNotFoundError as e:
        print('Cannot create simulation_results.txt. Quitting...')
        sys.exit()

print('Simulation started...')

try:
    original_stdout = sys.stdout # Save a reference to the original standard output
    sys.stdout = open('simulation_results.txt', 'w')
except FileNotFoundError as e:
    print('Cannot create simulation_results.txt. Quitting...')
    sys.exit()

sim_time, algo, thresholds, max_trials = parsefiles.parseSimulationParameters('simulation_params.txt')
#print(sim_time, algo, thresholds, max_trials)
print('\nSimulation Parameters:')
print('Simulation time incl. 1hr warmup and  1hr cooldown (seconds):', sim_time)
print('Load balance algo:', algo)
print('Threshold values:', thresholds)
print('Maximum number of trials:', max_trials)

print('\nSimulation results:')
if algo == 'RoutingDecision1': simulation()

if algo == 'RoutingDecision2':
    for d in thresholds:
        global threshold
        threshold = d
        #ciw.seed(threshold) # this is wrong here

        simulation()

    print('\nMin wait time (ms):', "{:.3f}".format(min_wait_time * 1000))
    print('Threshold with min wait time: d =', min_wait_time_threshold)

    print('\nMax util (percentage):', "{:.3f}".format(max_util * 100))
    print('Threshold with max util: d =', max_util_threshold)

sys.stdout = original_stdout # Reset the standard output to its original value
finalizeSimulationResults()
print('Simulation completed successfully.')