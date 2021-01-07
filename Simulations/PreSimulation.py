import pandas as pd
import numpy as np
import random
import sys
sys.path.append('../')
from DiseasePropagation.TransmissionProbability import calculateTransProbability
from DiseasePropagation.Exposure import calculateExposure


def runSimulation_PreEmptive(inputNetworksPrefix,
                              inputStatusFile,
                             seedIndex,
                             r_value = 1,
                              START_DAY = 7,
                              END_DAY = 32, # Change to simulate at a bigger scale,
                              SIMULATION_ID = 0
                              ):
    StatusDf = pd.read_csv(inputStatusFile)
    Status_UsID = StatusDf['UsID'].tolist()
    Status = StatusDf['Status'].tolist()
    Status_InfectiousAt = StatusDf['InfectiousAt'].tolist()
    Status_RecoverAt = StatusDf['RecoverAt'].tolist()
    r = seedIndex
    Status[r] = 'Infectious'
    Status_RecoverAt[r] = END_DAY
    nOfInfection = 1
    node = 0
    #----- Run simulation day by day -----#
    for day in range(START_DAY, END_DAY):
        exposure_dict = dict()
        # print('Day '+ str(day) + ": Begin")
        # Check and Update the Status everyday
        infectiousUs = []
        for i in range(len(Status)):
            if((Status[i] == 'Infected') & (day == Status_InfectiousAt[i])):
                Status[i] = 'Infectious'
            elif((Status[i] == 'Infectious')):
                if(day == Status_RecoverAt[i]):
                    Status[i] = 'Recovered'
                elif(day < Status_RecoverAt[i]):
                    infectiousUs.append(Status_UsID[i])
        # print("Status Checked.")
        # Simulate the network
        LinkDf = pd.read_csv(inputNetworksPrefix + str(day) + '.csv', names=['HostID','NbID','HSt','HEnd','NbSt','NbEnd'])
        # Check each Infectious User

        for infectiousID in infectiousUs:
            contactRows_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['NbID'].tolist()
            HSt_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['HSt'].tolist()
            HEnd_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['HEnd'].tolist()
            NbSt_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['NbSt'].tolist()
            NbEnd_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['NbEnd'].tolist()

            # prob_host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['Prob'].tolist()
            contactRows_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['HostID'].tolist()
            HSt_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['HSt'].tolist()
            HEnd_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['HEnd'].tolist()
            NbSt_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['NbSt'].tolist()
            NbEnd_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['NbEnd'].tolist()

            # prob_nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['Prob'].tolist()
            # Initialize the dictionary
            for j in range(0, len(contactRows_Host)):
                exposure_dict[contactRows_Host[j]] = 0

            for k in range(0, len(contactRows_Nb)):
                exposure_dict[contactRows_Nb[k]] = 0
            #Check host
            for m in range(0,len(contactRows_Host)):
                expo = calculateExposure(HSt_Host[m],
                                         HEnd_Host[m],
                                         NbSt_Host[m],
                                         NbEnd_Host[m]
                                         )
                exposure_dict[contactRows_Host[m]] += expo

            for n in range(0, len(contactRows_Nb)):
                expo = calculateExposure(HSt_Nb[n],
                                         HEnd_Nb[n],
                                         NbSt_Nb[n],
                                         NbEnd_Nb[n]
                                         )
                exposure_dict[contactRows_Nb[n]] += expo
            for susceptibleId in exposure_dict:
                prob = calculateTransProbability(exposure_dict[susceptibleId], r_value)
                # print(prob)
                temp_prob = np.random.binomial(1,prob)

                if(temp_prob > 0 ):
                    nbIndex = Status_UsID.index(susceptibleId)
                    nbStatus = Status[nbIndex]
                    if (nbStatus == 'Susceptible'):
                        nOfInfection += 1
                        # print('Infection occurred')
                        incubation = round(np.random.lognormal(mean=1.621,
                                                               sigma=0.418
                                                               ))
                        while (incubation < 3):
                            incubation = round(np.random.lognormal(mean=1.621,
                                                                   sigma=0.418
                                                                   ))
                        infectiousAt = day + incubation - 3
                        recoverAt = day + incubation + 8
                        Status[nbIndex] = 'Infected'
                        Status_InfectiousAt[nbIndex] = infectiousAt
                        Status_RecoverAt[nbIndex] = recoverAt

        # print('Day ' + str(day) + ': Finished')
        # print()

    #----- Output to a file -----#
    # FinalStatusData = {
    #     'UsID': Status_UsID,
    #     'Status': Status,
    #     'InfectiousAt': Status_InfectiousAt,
    #     'RecoverAt': Status_RecoverAt
    # }
    #
    # FinalStatusDf = pd.DataFrame(FinalStatusData, columns=['UsID', 'Status', 'InfectiousAt', 'RecoverAt'])
    # FinalStatusDf.to_csv(outputStatusFile, header=True, index=False)
    # print()
    # print(nOfInfection)
    if(nOfInfection > 100):
        node = 1


    return [nOfInfection, node]


import concurrent.futures
import time
import threading
import multiprocessing as mp


def exclude_random(exclude, range):
    rand = random.randint(0,range)
    return exclude_random(exclude,range) if rand in exclude else rand

result_list = [0,0,0]
num_sim = 0
def log_result(result):
    result_list[2] += 1
    result_list[0] += result[0]
    result_list[1] += result[1]


def runSim_DDT(seedIndex, method, percent, r_value):
    fileName = ''
    if(percent == 0):
        fileName = 'initialStatus_noVacc.csv'
    elif(percent == 0.2):
        fileName = 'initialStatus_point2.csv'
    elif(percent == 0.4):
        fileName = 'initialStatus_point4.csv'
    elif (percent == 0.6):
        fileName = 'initialStatus_point6.csv'
    elif (percent == 0.8):
        fileName = 'initialStatus_point8.csv'
    elif (percent == 1):
        fileName = 'initialStatus_1.csv'
    elif (percent == 1.2):
        fileName = 'initialStatus_1point2.csv'
    elif (percent == 1.4):
        fileName = 'initialStatus_1point4.csv'
    elif (percent == 1.6):
        fileName = 'initialStatus_1point6.csv'
    elif (percent == 1.8):
        fileName = 'initialStatus_1point8.csv'
    elif (percent == 2):
        fileName = 'initialStatus_2.csv'

    result = runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
                                       inputStatusFile=f'./Pre-emptive/{method}/{fileName}',
                                      r_value=r_value,
                                      seedIndex=seedIndex,
                                       START_DAY = 7,
                                       END_DAY =32)

    log = dict()
    log['result'] = result
    log['method'] = method
    log['percent'] = percent
    log['index'] = seedIndex
    log['r_value'] = r_value
    return log
    pass

class Executor:
    def __init__(self, process_num):
        self.pool = mp.Pool(process_num)
        self.result_list = [0,0,0]
    def prompt(self, log):
        if log:
            self.result_list[2] += 1
            self.result_list[0] += log['result'][0]
            self.result_list[1] += log['result'][1]
            print(
                f'Sim {self.result_list[2]}. '
                f'DDT - {log["method"]} {log["percent"]}%: '
                f'Outbreak size: {log["result"][0]}. '
                f'Average: {self.result_list[0] / self.result_list[2]}. '
                f'Node: {self.result_list[1]}. '
                f'R_value: {log["r_value"]}'
                f'Seed: {log["index"]}')

    def schedule(self, function, args):
        self.pool.apply_async(function, args=args, callback=self.prompt)

    def wait(self):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

if __name__ == '__main__':
    start = time.perf_counter()
    NUMBER_OF_SIMULATIONS = 100

    methods = ['DV', 'IMV', 'RV', 'AV']
    percentages = [1]
    r_list = [1, 0.8, 1.5]
    num_workers = mp.cpu_count() - 4

    for method in methods:
        for percent in percentages:
            for r_value in r_list:
                exclude = []
                executor = Executor(num_workers)
                for i in range(NUMBER_OF_SIMULATIONS):
                    seedIndex = exclude_random(exclude, 364544)
                    exclude.append(seedIndex)
                    executor.schedule(runSim_DDT, (seedIndex, method, percent, np.random.normal(1, 0.1)))
                executor.wait()
                print(
                    f'Pre-emptive (DDT - {method} {percent}%, R value: {r_value}): '
                    f'Average outbreak size: {executor.result_list[0]/NUMBER_OF_SIMULATIONS} '
                    f'Number of nodes: {executor.result_list[1]}\n')

    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    pass