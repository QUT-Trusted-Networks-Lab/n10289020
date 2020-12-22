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


    return [nOfInfection, node]


import concurrent.futures
import time
import threading
import multiprocessing as mp

# def singleProcess_10Sim(procnum, return_dict):
#     NUMBER_OF_SIMULATIONS = 20
#     sum = 0
#     seedIndex = random.randint(364544)
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         results = [executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
#                                    './Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
#                                    seedIndex,
#                                    7,
#                                    32,
#                                    i
#                                    ) for i in range(NUMBER_OF_SIMULATIONS)]
#         for f in concurrent.futures.as_completed(results):
#             sum += f.result()

    # return_dict[procnum]=(sum / NUMBER_OF_SIMULATIONS)

def exclude_random(exclude, range):
    rand = random.randint(0,range)
    return exclude_random(exclude,range) if rand in exclude else rand

result_list = [0,0,0]
num_sim = 0
def log_result(result):
    result_list[2] += 1
    result_list[0] += result[0]
    result_list[1] += result[1]

def log_result_2(result):
    print(f"DDT - {result['method']} {result['percent']}: Outbreak size: {result['size']}. Seed Index: {result[seedIndex]}")

def runSim_DDT(seedIndex, method, percent, sim, return_dict):
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
                                      seedIndex=seedIndex,
                                       START_DAY = 7,
                                       END_DAY =32)
    result_list[2] += 1
    result_list[0] += result[0]
    result_list[1] += result[1]
    print(f'Sim {sim}. DDT - {method} {percent}%: Outbreak size: {result[0]}. Seed node index: {seedIndex}')
    return_dict[sim] = result
    # return_dict = {}
    # return_dict['method'] = method
    # return_dict['percent'] = percent
    # return_dict['size'] = result[0]
    # return_dict['nodes'] = result[1]
    # return_dict['seedIndex'] = seedIndex
    # return return_dict

    pass

if __name__ == '__main__':
    start = time.perf_counter()
    NUMBER_OF_SIMULATIONS = 2
    #---------- Simulation 1: Pre-emptive no Vaccine, 7 days ------------
    # result = runSimulation_PreEmptive(inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
    #                                    inputStatusFile='./Pre-emptive/RV/initialStatus_noVacc.csv',
    #                                    START_DAY = 7,
    #                                    END_DAY =32
    #                                    )
    # print(f'DDT - No Vacc: {result}')

    methods = ['AV']
    percentages = [0.2, 0.4, 0.6]
    # percentages = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]
    num_workers = mp.cpu_count()

    for method in methods:
        for percent in percentages:
            pool = mp.Pool(num_workers)
            jobs = []
            sum = 0
            sim = 0
            node = 0
            results = []
            exclude = []
            result_list = [0, 0, 0]
            return_dict = mp.Manager().dict()
            for i in range(NUMBER_OF_SIMULATIONS):
                sim += 1
                seedIndex = exclude_random(exclude, 364544)
                exclude.append(seedIndex)
                pool.apply_async(runSim_DDT, args=(seedIndex, method, percent, sim, return_dict))

            pool.close()
            pool.join()
            for a in return_dict:
                sum += return_dict[a][0]
                node += return_dict[a][1]
            print(
                f'Pre-emptive (DDT - {method} {percent}%): Average outbreak size: {sum/NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')

    # ------------- Simulation for a particular node -------------
    # methods = ['AV']
    # percentages = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8 , 2]
    # # seedIndex = 31499
    #
    #
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     for method in methods:
    #         for percent in percentages:
    #             sum = 0
    #             node = 0
    #             num_sim = 0
    #             results = []
    #             exclude = []
    #             for i in range(NUMBER_OF_SIMULATIONS):
    #                 seedIndex = exclude_random(exclude, 364544)
    #                 exclude.append(seedIndex)
    #                 results.append(executor.submit(runSim_DDT,seedIndex, method, percent
    #                                                ))
    #
    #             for f in concurrent.futures.as_completed(results):
    #                 num_sim += 1
    #                 sum += f.result()['size']
    #                 node += f.result()['nodes']
    #
    #             print(
    #                 f'Pre-emptive (DDT - {method} {percent}%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
            # print(
            #     f'({seedIndex} - DV 0.2%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')

    # seedNd = 27160 # Seed node index
    # num_workers = mp.cpu_count() - 2
    # pool = mp.Pool(num_workers)
    # exclude = []
    # for method in methods:
    #     for percent in percents:
    #         seedIndex = seedNd
    #         pool.apply_async(runSim_DDT, args=(seedIndex,method,percent), callback=log_result_2)
    # pool.close()
    # pool.join()
    # print('Finished')



    
    # num_workers = mp.cpu_count() - 2
    # pool = mp.Pool(num_workers)
    # exclude = []
    # for i in range(NUMBER_OF_SIMULATIONS):
    #     seedIndex = exclude_random(exclude, 364544)
    #     exclude.append(seedIndex)
    #     pool.apply_async(runSimulation_PreEmptive, args=('../Data/SPDTNetwork/DDT/bclink_',
    #                                                      './Pre-emptive/RV/initialStatus_noVacc.csv',
    #                                                      27160,
    #                                                      ), callback=log_result)
    #
    #
    # pool.close()
    # pool.join()
    # print(f'Seed Index: 27160 (No Vacc):\nAverage outbreak size: {result_list[0] / NUMBER_OF_SIMULATIONS}\n')
    # print(f'Seed Index: 27160 (No Vacc):\nAverage outbreak size: {result_list[0] / NUMBER_OF_SIMULATIONS}\n'
    #       f'Number of nodes: {result_list[1]}')

    # sum = 0
    # node = 0
    # num_sim = 0
    # seedIndex = 31499
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/RV/initialStatus_point2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    # print(
    #     f'Pre-emptive ({seedIndex} - RV 0.2%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_point2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 0.2%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 0.2%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_point4.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 0.4%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 0.4%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_point6.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 0.6%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 0.6%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_point8.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 0.8%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 0.8%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_1.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 1.0%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 1.0%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_1point2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 1.2%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 1.2%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_1point4.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 1.4%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 1.4%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_1point6.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 1.6%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 1.6%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_1point8.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 1.8%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - DV 1.8%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/DV/initialStatus_2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - DV 2.0%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - D 2.0%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_point2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 0.2%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 0.2%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_point4.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 0.4%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 0.4%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_point6.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 0.6%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 0.6%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_point8.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 0.8%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 0.8%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_1.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 1.0%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 1.0%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_1point2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 1.2%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 1.2%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_1point4.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 1.4%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 1.4%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_1point6.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 1.6%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 1.6%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_1point8.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 1.8%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 1.8%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')
    #
    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/IMV/initialStatus_2.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         # print(
    #         #     f'({seedIndex} - IMV 2.0%) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive ({seedIndex} - IMV 2.0%): Average outbreak size: {sum / NUMBER_OF_SIMULATIONS} Number of nodes: {node}\n')



    # sum = 0
    # node = 0
    # num_sim = 0
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = []
    #     exclude = []
    #     for i in range(NUMBER_OF_SIMULATIONS):
    #         seedIndex = exclude_random(exclude, 364544)
    #         exclude.append(seedIndex)
    #         results.append(executor.submit(runSimulation_PreEmptive, '../Data/SPDTNetwork/DDT/bclink_',
    #                                        './Pre-emptive/RV/initialStatus_noVacc.csv',
    #                                        seedIndex,
    #                                        7,
    #                                        32,
    #                                        i
    #                                        ))
    #     for f in concurrent.futures.as_completed(results):
    #         num_sim += 1
    #         sum += f.result()[0]
    #         node += f.result()[1]
    #         print(
    #             f'(DDT - No Vaccination) Simulation {num_sim}. outbreak size: {sum / num_sim}. Number of nodes: {node}')
    # print(
    #     f'Pre-emptive (DDT - No Vaccination):\nAverage outbreak size: {sum / NUMBER_OF_SIMULATIONS}\nNumber of nodes: {node}')

    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s).')
    pass