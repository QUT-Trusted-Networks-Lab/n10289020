import pandas as pd
import numpy as np
import random
import sys
sys.path.append('../')
from DiseasePropagation.TransmissionProbability import calculateTransProbability
from DiseasePropagation.Exposure import calculateExposure


def runSimulation_Reactive(inputNetworksPrefix,
                           inputStatusFile,
                           seedIndex,
                           METHOD = 'RV',
                           PERCENT = 0.002,
                           START_DAY = 7,
                           END_DAY = 32, # Change to simulate at a bigger scale,
                           SIMULATION_ID = 0
                           ):
    # print(f'Simulation {SIMULATION_ID} begin.')
    StatusDf = pd.read_csv(inputStatusFile)
    Status_UsID = StatusDf['UsID'].tolist()
    Status = StatusDf['Status'].tolist()
    Status_InfectiousAt = StatusDf['InfectiousAt'].tolist()
    Status_RecoverAt = StatusDf['RecoverAt'].tolist()
    InfectedUsID = []
    for r in seedIndex:
        Status[r] = 'Infectious'
        InfectedUsID.append(Status_UsID[r])
        Status_RecoverAt[r] = END_DAY
    nOfInfection = len(seedIndex)
    node = 0

    # Gather information from Day 0 to START_DAY
    NbNodes = []
    indexToVacc = []
    ## Get all neighboring nodes
    for iday in range(START_DAY):
        for infectiosID in InfectedUsID:
            LinkDf = pd.read_csv(inputNetworksPrefix + str(iday) + '.csv',
                                 names=['HostID', 'NbID', 'HSt', 'HEnd', 'NbSt', 'NbEnd'])
            neighbors_host = LinkDf.loc[LinkDf['HostID'] == infectiosID]['NbID'].tolist()
            neighbors_nb = LinkDf.loc[LinkDf['HostID'] == infectiosID]['HostID'].tolist()
            NbNodes += neighbors_host + neighbors_nb
            NbNodes = list(dict.fromkeys(NbNodes))
        pass

    ## Vaccinate based on strategy

    nOfVacc = int(PERCENT/100 * len(NbNodes))
    if(nOfVacc == 0):
        nOfVacc = 1

    if(METHOD == 'RV'):
        indexToVacc = np.random.choice(len(NbNodes), nOfVacc) #Randomly choose


    elif(METHOD == 'DV'):
        DVRank = pd.read_csv('../StatusGeneration/ContactCount.csv')
        RankUs = DVRank['UsID'].tolist()
        NbNodes = sorted(NbNodes, key=lambda x: RankUs.index(x))
        toVaccID = NbNodes[0:nOfVacc]
        for toVacc in toVaccID:
            index = Status_UsID.index(toVacc)
            indexToVacc.append(index)


    elif (METHOD == 'AV'):
        AVRank = pd.read_csv('../StatusGeneration/DDT-AVranking.csv',
                              names=['UsID', 'AVrank'])
        AVRank = AVRank.sort_values(['AVrank'], ascending=False)
        RankUs = AVRank['UsID'].tolist()

        def AV_sorting(id):
            if (id in RankUs):
                return RankUs.index(id)
            else:
                return 1000000

        NbNodes = sorted(NbNodes, key=AV_sorting)
        toVaccID = NbNodes[0:nOfVacc]
        for toVacc in toVaccID:
            index = Status_UsID.index(toVacc)
            indexToVacc.append(index)

    elif(METHOD == 'IMV'):
        IMVRank = pd.read_csv('../StatusGeneration/DDT-IMVranking.csv', names=['UsID', 'IMVrank', 'IMEVrank', 'IMTVrank', 'Degree'])
        IMVRank = IMVRank.sort_values(['IMVrank'], ascending=False)
        RankUs = IMVRank['UsID'].tolist()

        def IMV_sorting(id):
            if(id in RankUs):
                return RankUs.index(id)
            else:
                return 1000000

        NbNodes = sorted(NbNodes, key=IMV_sorting)
        toVaccID = NbNodes[0:nOfVacc]
        for toVacc in toVaccID:
            index = Status_UsID.index(toVacc)
            indexToVacc.append(index)
    indexToVacc = indexToVacc + seedIndex
    print(len(NbNodes))
    print(len(indexToVacc))

    #----- Run simulation day by day -----#
    for day in range(0, END_DAY):
        if(day == START_DAY): ## Vaccination start at day 7
            for index in indexToVacc:
                Status[index] = 'Recovered'

        exposure_dict = dict()
        # print('Day '+ str(day) + ": Begin")
        # Check and Update the Status everyday
        infectiousUs = []
        for i in range(len(Status)):
            if((Status[i] == 'Infected') & (day == Status_InfectiousAt[i])):
                Status[i] = 'Infectious'
            elif((Status[i] == 'Infectious')):
                if(day == Status_InfectiousAt[i]):
                    Status[i] = 'Recovered'
                else:
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
                prob = calculateTransProbability(exposure_dict[susceptibleId])
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
    # print(f'Simulation {SIMULATION_ID} finished')
    return [nOfInfection, node]

def run_DDT(seedIndex, method, percent):
    result = runSimulation_Reactive(
        inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
        inputStatusFile='./Reactive/DDT/initialStatus.csv',
        METHOD=method,
        START_DAY=7,
        END_DAY=32,
        seedIndex=seedIndex,
        PERCENT=percent
    )

    log = dict()
    log['result'] = result
    log['method'] = method
    log['percent'] = percent
    return log
    pass

import concurrent.futures
import time
import multiprocessing as mp

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
                f'Node: {self.result_list[1]}. ')

    def schedule(self, function, args):
        self.pool.apply_async(function, args=args, callback=self.prompt)

    def wait(self):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

if __name__ == '__main__':
    # Test
    start = time.perf_counter()
    # print(runSimulation_Reactive(
    #     inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
    #     inputStatusFile='./Reactive/DDT/initialStatus.csv',
    #     METHOD='DV',
    #     START_DAY=7,
    #     END_DAY=32,
    #     seedIndex=[0,1,31499],
    #     PERCENT=1
    # ))
    NUMBER_OF_SIMULATIONS = 1000

    methods = ['DV']
    percentages = [2, 1.8, 1.6, 1.4, 1.2, 1, 0.8, 0.6, 0.4, 0.2]
    percentages = [20, 15, 10]
    # percentages = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]
    num_workers = mp.cpu_count() - 3
    index = [ind for ind in range(364544)]
    for method in methods:
        for percent in percentages:
            executor = Executor(num_workers)
            for i in range(NUMBER_OF_SIMULATIONS):
                seedIndex = random.sample(index, 100)
                executor.schedule(run_DDT, (seedIndex, method, percent))
            executor.wait()
            print(
                f'Reactive (DDT - {method} {percent}%): '
                f'Average outbreak size: {executor.result_list[0] / NUMBER_OF_SIMULATIONS} '
                f'Number of nodes: {executor.result_list[1]}\n')

    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    # NUMBER_OF_SIMULATIONS = 100
    # methods = ['AV']
    # percentages = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]
    # seedIndex = 31499
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     for method in methods:
    #         for percent in percentages:
    #             results = []
    #             for i in range(NUMBER_OF_SIMULATIONS):
    #                 results.append(executor.submit(runSimulation_Reactive,
    #                                                '../Data/SPDTNetwork/DDT/bclink_', #Input file prefix
    #                                                './Reactive/DDT/initialStatus.csv', #Input status file
    #                                                method,
    #                                                7,32, # Start and end day
    #                                                seedIndex,
    #                                                percent
    #                                                ))
    #
    #             for f in concurrent.futures.as_completed(results):
    #                 num_sim += 1
    #                 sum += f.result()['size']
    #                 node += f.result()['nodes']
    #
    #             print(
    #                 f'Pre-emptive (DDT - {method} {percent}%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')

    finish = time.perf_counter()



    print(f'Finished in {round(finish - start, 2)} second(s).')
