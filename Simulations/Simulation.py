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
                              START_DAY = 7,
                              END_DAY = 32, # Change to simulate at a bigger scale,
                              SIMULATION_ID = 0
                              ):
    print(f'Simulation {SIMULATION_ID} begin.')
    StatusDf = pd.read_csv(inputStatusFile)
    Status_UsID = StatusDf['UsID'].tolist()
    Status = StatusDf['Status'].tolist()
    Status_InfectiousAt = StatusDf['InfectiousAt'].tolist()
    Status_RecoverAt = StatusDf['RecoverAt'].tolist()
    r = seedIndex
    Status[r] = 'Infectious'
    Status_RecoverAt[r] = END_DAY
    nOfInfection = 1
    
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
                        recoverAt = day + incubation + 11
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
    print(f'Simulation {SIMULATION_ID} finished')
    return nOfInfection


import concurrent.futures
import time
import threading
import multiprocessing

def singleProcess_10Sim(procnum, return_dict):
    NUMBER_OF_SIMULATIONS = 20
    sum = 0
    seedIndex = random.randint(364544)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
                                   './Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
                                   seedIndex,
                                   7,
                                   32,
                                   i
                                   ) for i in range(NUMBER_OF_SIMULATIONS)]
        for f in concurrent.futures.as_completed(results):
            sum += f.result()

    # return_dict[procnum]=(sum / NUMBER_OF_SIMULATIONS)

def exclude_random(exclude, range):
    rand = random.randint(0,range)
    return exclude_random(exclude,range) if rand in exclude else rand

if __name__ == '__main__':
    start = time.perf_counter()
    #---------- Simulation 1: Pre-emptive no Vaccine, 7 days ------------
    # print(runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
    #                          inputStatusFile='./Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
    #                          START_DAY = 7,
    #                          END_DAY =32
    #                          ))

    print(exclude_random([2,3], 10))
    # ---------- Test Threading ------------
    NUMBER_OF_SIMULATIONS = 1000
    sum = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = []
        exclude = []
        for i in range(NUMBER_OF_SIMULATIONS):
            seedIndex = exclude_random(exclude, 364544)
            exclude.append(seedIndex)
            results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
                                   './Pre-emptive/RV/initialStatus_point2.csv',
                                    seedIndex,
                                   7,
                                   32,
                                   i
                                   ))
        for f in concurrent.futures.as_completed(results):
            sum += f.result()
    print(f'Average outbreak size: {sum/NUMBER_OF_SIMULATIONS}')


    # NUMBER_OF_PROCESSORS = 4
    #
    # manager = multiprocessing.Manager()
    # return_dict = manager.dict()
    # jobs = []
    # for _ in range(10):
    #     for i in range(NUMBER_OF_PROCESSORS):
    #         p = multiprocessing.Process(target=singleProcess_10Sim,
    #                                     args=(i, return_dict))
    #
    #         jobs.append(p)
    #         p.start()
    #
    #     for proc in jobs:
    #         proc.join()
    #
    # sum = 0
    # for val in return_dict.values():
    #     sum += val
    #
    # print(f'Average outbreak size: {sum/10}')
    #
    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    pass