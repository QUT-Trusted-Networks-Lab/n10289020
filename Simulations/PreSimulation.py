import pandas as pd
import numpy as np
import random
import sys
sys.path.append('../')
from DiseasePropagation.TransmissionProbability import calculateTransProbability
from DiseasePropagation.Exposure import calculateExposure


def runSimulation_PreEmptive(inputNetworksPrefix,
                             rankingFile,
                             vaccPercent,
                             missingPercent,
                             seedIndex,
                             r_value = 1,
                             START_DAY = 7,
                             END_DAY = 32, # Change to simulate at a bigger scale,
                            ):




    StatusDf = pd.read_csv('./initialStatus.csv')
    Status_UsID = StatusDf['UsID'].tolist()
    Status = StatusDf['Status'].tolist()
    Status_InfectiousAt = StatusDf['InfectiousAt'].tolist()
    Status_RecoverAt = StatusDf['RecoverAt'].tolist()
    Status[seedIndex] = 'Infectious'
    Status_RecoverAt[seedIndex] = END_DAY
    nOfInfection = 1
    node = 0

    # Vaccinate
    ranking = pd.read_csv(rankingFile)
    nOfVacc = int(vaccPercent/100 * len(Status_UsID))
    nOfMissing = int(missingPercent/100 * len(Status_UsID))
    countList = ranking['UsID'].tolist()

    recoveredList = countList[nOfMissing:nOfVacc + nOfMissing]

    # for r in recoveredList:
    #     recoverIndex = Status_UsID.index(r)
    #     Status[recoverIndex] = 'Recovered'


    # infectedList = []
    # infected_infectiousAt_list = []
    # infected_recoveredAt_list = []
    #
    # infectiousList = []
    # infectious_recoveredAt_list = []
    #
    # infectiousList.append(Status_UsID[seedIndex])
    # infectious_recoveredAt_list.append(END_DAY)

    #----- Run simulation day by day -----#
    for day in range(START_DAY, END_DAY):
        exposure_dict = dict()
        # print('Day '+ str(day) + ": Begin")
        # Check and Update the Status everyday


        infectiousUs = []

        # to_trans_infected_infectious = []
        # for i in  range(0, len(infectedList)):
        #     if(infected_infectiousAt_list[i] == day):
        #         to_trans_infected_infectious.append(i)
        # # print(infectedList)
        # # print(infectiousList)
        # # print(to_trans_infected_infectious)
        #
        # for transI in to_trans_infected_infectious:
        #     infectiousList.append(infectedList[transI])
        #     infectious_recoveredAt_list.append(infected_recoveredAt_list[transI])
        #
        # infectedList = [infectedList[i] for i in range(0,len(infectedList)) if i not in to_trans_infected_infectious]
        # infected_recoveredAt_list = [infected_recoveredAt_list[i] for i in range(0, len(infected_recoveredAt_list))
        #                              if i not in to_trans_infected_infectious]
        # infected_infectiousAt_list = [infected_infectiousAt_list[i] for i in range(0, len(infected_infectiousAt_list))
        #                              if i not in to_trans_infected_infectious]
        #
        # to_trans_infectious_recovered = []
        # for u in range(0, len(infectiousList)):
        #     if(infectious_recoveredAt_list[u] == day):
        #         to_trans_infected_infectious.append(u)
        #
        #     elif(day < infectious_recoveredAt_list[u]):
        #         infectiousUs.append(infectiousList[u])
        #
        # for transU in to_trans_infectious_recovered:
        #     recoveredList.append(infectiousList[transU])
        #
        # infectiousList = [infectiousList[i] for i in range(0, len(infectiousList)) if
        #                 i not in to_trans_infectious_recovered]
        # infectious_recoveredAt_list = [infectious_recoveredAt_list[i] for i in range(0, len(infectious_recoveredAt_list))
        #                              if i not in to_trans_infectious_recovered]

        for i in range(len(Status)):
            if((Status[i] == 'Infected') & (day == Status_InfectiousAt[i])): # Enter infectious period
                Status[i] = 'Infectious'
                infectiousUs.append(Status_UsID[i])
                # infectiousList.append(Status_UsID[i])
            elif((Status[i] == 'Infectious')):
                if(day == Status_RecoverAt[i]): # Enter Recovered period
                    recoveredList.append(Status_UsID[i])
                    Status[i] = 'Recovered'
                elif(day < Status_RecoverAt[i]): # Count as a infector
                    infectiousUs.append(Status_UsID[i])

        # Simulate the network
        LinkDf = pd.read_csv(inputNetworksPrefix + str(day) + '.csv', names=['HostID','NbID','HSt','HEnd','NbSt','NbEnd'])
        # Check each Infectious User

        ## Get all the node that contact with the infected
        for infectiousID in infectiousUs:
            # Get the link when the susceptible, as a neighbor, contact with the infected
            contactRows_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['NbID'].tolist()
            # contactRows_Host = [sus for sus in contactRows_Host if
            #                     (sus not in recoveredList) &
            #                     (sus not in infectedList) &
            #                     (sus not in infectiousList)
            #                     ]
            # HSt_Host = LinkDf.loc[(LinkDf['HostID'] == infectiousID)]['HSt'].tolist()
            HSt_Host = LinkDf[(LinkDf['HostID'] == infectiousID)]['HSt'].tolist()

            HEnd_Host = LinkDf[(LinkDf['HostID'] == infectiousID)]['HEnd'].tolist()
            NbSt_Host = LinkDf[(LinkDf['HostID'] == infectiousID)]['NbSt'].tolist()
            NbEnd_Host = LinkDf[(LinkDf['HostID'] == infectiousID)]['NbEnd'].tolist()

            # Get the link when the susceptible, as a host, contact with the infected
            contactRows_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['HostID'].tolist()
            # contactRows_Nb = [sus for sus in contactRows_Nb if
            #                     (sus not in recoveredList) &
            #                     (sus not in infectedList) &
            #                     (sus not in infectiousList)
            #                     ]
            HSt_Nb = LinkDf[(LinkDf['NbID'] == infectiousID)]['HSt'].tolist()
            HEnd_Nb = LinkDf[(LinkDf['NbID'] == infectiousID)]['HEnd'].tolist()
            NbSt_Nb = LinkDf[(LinkDf['NbID'] == infectiousID) ]['NbSt'].tolist()
            NbEnd_Nb = LinkDf[(LinkDf['NbID'] == infectiousID) ]['NbEnd'].tolist()

            # Initialize the exposure dictionary
            for j in range(0, len(contactRows_Host)):
                exposure_dict[contactRows_Host[j]] = 0

            for k in range(0, len(contactRows_Nb)):
                exposure_dict[contactRows_Nb[k]] = 0

            # Calculate the exposure
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
                # if (temp_prob > 0):
                #     nOfInfection += 1
                #     incubation = round(np.random.lognormal(mean=1.621,
                #                                            sigma=0.418
                #                                            ))
                #
                #     while (incubation < 3):
                #         incubation = round(np.random.lognormal(mean=1.621,
                #                                                sigma=0.418
                #                                                ))
                #     infectiousAt = day + incubation - 3  # The day Infected become Infectious
                #     recoverAt = day + incubation + 8  # The day Infectious become recovered
                #
                #     infectedList.append(susceptibleId)
                #     infected_infectiousAt_list.append(infectiousAt)
                #     infected_recoveredAt_list.append(recoverAt)


                if(temp_prob > 0 ):
                    nbIndex = Status_UsID.index(susceptibleId)
                    nbStatus = Status[nbIndex]
                    if ((nbStatus == 'Susceptible' ) & (susceptibleId not in recoveredList)):
                        nOfInfection += 1

                        # Incubation period
                        incubation = round(np.random.lognormal(mean=1.621,
                                                               sigma=0.418
                                                               ))

                        while (incubation < 3):
                            incubation = round(np.random.lognormal(mean=1.621,
                                                                   sigma=0.418
                                                                   ))
                        infectiousAt = day + incubation - 3 # The day Infected become Infectious
                        recoverAt = day + incubation + 8 # The day Infectious become recovered
                        Status[nbIndex] = 'Infected'
                        Status_InfectiousAt[nbIndex] = infectiousAt
                        Status_RecoverAt[nbIndex] = recoverAt

        # print('Day ' + str(day) + ': Finished')
        # print()
    if(nOfInfection > 100):
        node = 1 # If the node caused more than 100 infections


    return [nOfInfection, node]


import time
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

# This is for running the simulations
def runSim_DDT(seedIndex, method, percent, r_value, k):
    fileName = ''
    rankingFile = ''

    if (method == 'DV'):
        rankingFile = 'ContactCount.csv'
    elif(method =='IMV'):
        rankingFile = 'DDT-IMVranking.csv'

    # if(percent == 0):
    #     fileName = 'initialStatus_noVacc.csv'
    # elif(percent == 0.2):
    #     fileName = 'initialStatus_point2.csv'
    # elif(percent == 0.4):
    #     fileName = 'initialStatus_point4.csv'
    # elif (percent == 0.6):
    #     fileName = 'initialStatus_point6.csv'
    # elif (percent == 0.8):
    #     fileName = 'initialStatus_point8.csv'
    # elif (percent == 1):
    #     fileName = 'initialStatus_1.csv'
    # elif (percent == 1.2):
    #     fileName = 'initialStatus_1point2.csv'
    # elif (percent == 1.4):
    #     fileName = 'initialStatus_1point4.csv'
    # elif (percent == 1.6):
    #     fileName = 'initialStatus_1point6.csv'
    # elif (percent == 1.8):
    #     fileName = 'initialStatus_1point8.csv'
    # elif (percent == 2):
    #     fileName = 'initialStatus_2.csv'
    # elif(percent == 2.2):
    #     fileName = 'initialStatus_2point2.csv'
    # else:
    #     fileName = f'initialStatus_{percent}.csv'

    result = runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
                                      rankingFile= f'./Ranking/{rankingFile}',
                                      vaccPercent=percent,
                                      missingPercent= k,
                                      r_value=r_value,
                                      seedIndex=seedIndex,
                                      START_DAY=7,
                                      END_DAY=32)

    log = dict()
    log['result'] = result
    log['method'] = method
    log['percent'] = percent
    log['index'] = seedIndex
    log['r_value'] = r_value
    log['k'] = k
    return log
    pass

import csv

# This is multiprocessing class to run and log the result
class Executor:
    def __init__(self, process_num):
        self.pool = mp.Pool(process_num)
        self.result_list = [0,0,0, 0]
        self.size_list = []
    def prompt(self, log):
        if log:
            self.size_list.append(log['result'][0])
            self.result_list[3] = np.std(self.size_list)
            self.result_list[2] += 1
            self.result_list[0] += log['result'][0]
            self.result_list[1] += log['result'][1]
            # with open(r'./r-value.csv', 'a', newline='') as file:
            #     fieldNames = ['Strategy', 'Coverage', 'R_value', 'Size', 'Node']
            #     writer = csv.DictWriter(file, fieldnames = fieldNames)
            #     writer.writerow({'Strategy': log["method"],
            #                      'Coverage': log['percent'],
            #                      'R_value': log['r_value'],
            #                      'Size': log['result'][0],
            #                      })
            print(
                f'Sim {self.result_list[2]}. ' # Number of simulations
                f'DDT - {log["method"]} {log["percent"]}%: ' # Method, and vaccination rate
                f'Outbreak size: {log["result"][0]}. ' # Number of infections
                f'Average: {self.result_list[0] / self.result_list[2]}. ' # Average
                f'Missing K: {log["k"]}%. '
                # f'Sd: {self.result_list[3]}. ' # Standard deviation
                # f'R_value: {log["r_value"]}. ' # Infectiousness
                f'Seed: {log["index"]}') # Seed node index

    def schedule(self, function, args):
        self.pool.apply_async(function, args=args, callback=self.prompt)

    def wait(self):
        self.pool.close()
        self.pool.join()
        self.pool.terminate()

if __name__ == '__main__':
    start = time.perf_counter()
    # result = runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
    #                                   rankingFile=f'./Ranking/ContactCount.csv',
    #                                   vaccPercent=10,
    #                                   missingPercent=5,
    #                                   r_value=1,
    #                                   seedIndex=10,
    #                                   START_DAY=7,
    #                                   END_DAY=32)
    # print(result)


    NUMBER_OF_SIMULATIONS = 2

    methods = ['DV']
    missing_k = [5]
    percentages = [10]
    r_list = [1] #R value
    num_workers = mp.cpu_count() - 4

    for method in methods:
        for percent in percentages:
            for r_value in r_list:
                for k in missing_k:
                    exclude = []
                    executor = Executor(num_workers)
                    for i in range(NUMBER_OF_SIMULATIONS):
                        seedIndex = exclude_random(exclude, 364544) # 364544 is the number of users in the network
                        exclude.append(seedIndex) # we dont want to run the same seed node again
                        executor.schedule(runSim_DDT, (seedIndex, method, percent, r_value, k))
                    executor.wait()
                    print(
                        f'Pre-emptive (DDT - {method} {percent}%, R value: {r_value}): '
                        f'Average outbreak size: {executor.result_list[0]/NUMBER_OF_SIMULATIONS} '
                        f'Number of nodes: {executor.result_list[1]}. '
                        f'Missing k: {k}%\n'
                        )

    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    pass