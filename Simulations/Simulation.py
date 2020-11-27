import pandas as pd
import numpy as np
import random
import sys
sys.path.append('../')
from DiseasePropagation.TransmissionProbability import calculateTransProbability

def runSimulation_PreEmptive(inputNetworksPrefix,
                              inputStatusFile,
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
    r = random.randrange(len(Status))
    Status[r] = 'Infectious'
    Status_RecoverAt[r] = END_DAY
    nOfInfection = 1
    #----- Run simulation day by day -----#
    for day in range(START_DAY, END_DAY):

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
        prob_dict = dict()
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
                prob_dict[contactRows_Host[j]] = 0
            for k in range(0, len(contactRows_Nb)):
                prob_dict[contactRows_Nb[k]] = 0
            #Check host
            for m in range(0, len(contactRows_Host)):
                prob = calculateTransProbability(HSt_Host[m],
                                                 HEnd_Host[m],
                                                 NbSt_Host[m],
                                                 NbEnd_Host[m]
                                                 )
                prob_dict[contactRows_Host[m]] += prob

            for n in range(0, len(contactRows_Nb)):
                prob = calculateTransProbability(HSt_Nb[n],
                                                 HEnd_Nb[n],
                                                 NbSt_Nb[n],
                                                 NbEnd_Nb[n]
                                                 )
                prob_dict[contactRows_Nb[n]] += prob
            for susceptibleId in prob_dict:
                temp_prob = np.random.binomial(1,prob_dict[susceptibleId])

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

if __name__ == '__main__':
    # Simulation 1: Pre-emptive no Vaccine, 7 days
    # runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
    #                          inputStatusFile='./Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
    #                          outputStatusFile='./Pre-emptive/RV/DDT_noVacc/result1.csv',
    #                          START_DAY = 7,
    #                          END_DAY =32
    #                          )
    start = time.perf_counter()
    NUMBER_OF_THREADS = 10
    NUMBER_OF_SIMULATIONS = 10
    l = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
                                                             './Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
                                                             7,
                                                             32,
                                                            i
                                                             ) for i in range(NUMBER_OF_SIMULATIONS)]
        for f in concurrent.futures.as_completed(results):
            l += f.result()
    print(l / NUMBER_OF_SIMULATIONS)
    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    pass