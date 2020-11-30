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
                           PROPORTION = 0.002,
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
    r = seedIndex
    Status[r] = 'Infectious'
    Status_RecoverAt[r] = END_DAY
    nOfInfection = 1
    node = 0

    # Gather information from Day 0 to START_DAY
    InfectedUsID = Status_UsID[r]
    NbNodes = []

    ## Get all neighboring nodes
    for iday in range(START_DAY):
        LinkDf = pd.read_csv(inputNetworksPrefix + str(iday) + '.csv',
                             names=['HostID', 'NbID', 'HSt', 'HEnd', 'NbSt', 'NbEnd'])
        neighbors_host = LinkDf.loc[LinkDf['HostID'] == InfectedUsID]['NbID'].tolist()
        neighbors_nb = LinkDf.loc[LinkDf['HostID'] == InfectedUsID]['HostID'].tolist()
        NbNodes += neighbors_host + neighbors_nb
        NbNodes = list(dict.fromkeys(NbNodes))
        pass

    ## Vaccinate based on strategy
    nOfVacc = int(PROPORTION * len(NbNodes))
    if(METHOD == 'RV'):
        toVaccinateIndex = np.random.choice(len(NbNodes), nOfVacc) #Randomly choose
        for i in toVaccinateIndex:
            Status[i] = 'Recovered'

    elif(METHOD == 'DV'):
        DVRank = pd.read_csv('../StatusGeneration/ContactCount.csv')
        RankUs = DVRank['UsID'].tolist()
        NbNodes = sorted(NbNodes, key=lambda x: RankUs.index(x))
        toVaccID = NbNodes[0:nOfVacc]
        for toVacc in toVaccID:
            index = Status_UsID.index(toVacc)
            Status[index] = 'Recovered'

    elif(METHOD == 'IMV'):
        IMVRank = pd.read_csv('../StatusGeneration/IMVRank.csv', names=['UsID', 'Rank'])
        IMVRank = IMVRank.sort_values(['Rank'], ascending=False)
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
            Status[index] = 'Recovered'


    #----- Run simulation day by day -----#
    for day in range(0, END_DAY):
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
    if(nOfInfection > 100):
        node = 1
    # print(f'Simulation {SIMULATION_ID} finished')
    return [nOfInfection, node]




if __name__ == '__main__':
    # Test
    print(runSimulation_Reactive(
        inputNetworksPrefix='../Data/SPDTNetwork/DDT/bclink_',
        inputStatusFile='./Reactive/DDT/initialStatus.csv',
        METHOD='RV',
        START_DAY=7,
        END_DAY=32,
        seedIndex=0,
        PROPORTION=0.1
    ))
