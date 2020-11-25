import pandas as pd
import numpy as np
import random

def runSimulation_PreEmptive(inputNetworksPrefix,
                              inputStatusFile,
                              outputStatusFile,
                              TOTAL_DAYS = 2, # Change to simulate at a bigger scale
                              ):
    StatusDf = pd.read_csv(inputStatusFile)
    Status_UsID = StatusDf['UsID'].tolist()
    Status = StatusDf['Status'].tolist()
    Status_InfectiousAt = StatusDf['InfectiousAt'].tolist()
    Status_RecoverAt = StatusDf['RecoverAt'].tolist()
    r = random.randrange(len(Status))
    Status[r] = 'Infectious'
    Status_RecoverAt[r] = TOTAL_DAYS
    #----- Run simulation day by day -----#
    for day in range(0, TOTAL_DAYS):

        print('Day '+ str(day) + ": Begin")
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
        print("Status Checked.")
        # Simulate the network
        LinkDf = pd.read_csv(inputNetworksPrefix + str(day) + '.csv')
        # Check each Infectious User
        for infectiousID in infectiousUs:
            contactRows_Host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['NbID'].tolist()
            prob_host = LinkDf.loc[LinkDf['HostID'] == infectiousID]['Prob'].tolist()
            contactRows_Nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['HostID'].tolist()
            prob_nb = LinkDf.loc[LinkDf['NbID'] == infectiousID]['Prob'].tolist()

            #Check host
            for j in range(0, len(contactRows_Host)):
                currentNb = contactRows_Host[j]
                temp_prob = np.random.binomial(1,prob_host[j])
                if(temp_prob > 0): # Infection occurred
                    nbIndex = Status_UsID.index(currentNb)
                    nbStatus = Status[nbIndex]
                    if(nbStatus == 'Susceptible'):
                        print('Infection occurred')
                        incubation = round(np.random.lognormal(mean=1.621,
                                                         sigma= 0.418
                                                         ))
                        while(incubation < 3):
                            incubation = round(np.random.lognormal(mean=1.621,
                                                             sigma= 0.418
                                                            ))
                        infectiousAt = day + incubation - 3
                        recoverAt = day + incubation + 11
                        Status[nbIndex] = 'Infected'
                        Status_InfectiousAt[nbIndex] = infectiousAt
                        Status_RecoverAt[nbIndex] = recoverAt

            #Check neighbors
            for k in range(0, len(contactRows_Nb)):
                currentNb = contactRows_Nb[k]
                temp_prob = np.random.binomial(1, prob_nb[k])
                if (temp_prob > 0):  # Infection occurred
                    nbIndex = Status_UsID.index(currentNb)
                    nbStatus = Status[nbIndex]
                    if (nbStatus == 'Susceptible'):
                        print('Infection occurred')
                        incubation = round(np.random.lognormal(mean=1.621,
                                                         sigma=0.418
                                                         ))
                        print(incubation)
                        while (incubation < 3):
                            incubation = round(np.random.lognormal(mean=1.621,
                                                             sigma=0.418
                                                             ))
                        infectiousAt = day + incubation - 3
                        recoverAt = day + incubation + 11
                        Status[nbIndex] = 'Infected'
                        Status_InfectiousAt[nbIndex] = infectiousAt
                        Status_RecoverAt[nbIndex] = recoverAt
            pass

        #------------OLD--------------#
    #     for linkIndex in range(0, len(LinkDf)):
    #         if(linkIndex % 1000000 == 0):
    #             print(str(linkIndex) + ' records checked. ' + str(len(LinkDf) - linkIndex) + ' remaining.')
    #         currentHost = LinkDf.at[linkIndex, 'HostID']
    #         currentNb = LinkDf.at[linkIndex, 'NbID']
    #         currentProb = LinkDf.at[linkIndex, 'Prob']
    #         #Random prob
    #         probRand = np.random.binomial(1, currentProb)
    #         if(probRand > 0): # Infection might occurred, update the status file
    #             print('Infection might occur')
    #             hostIndex = Status_UsID.index(currentHost)
    #             nbIndex = Status_UsID.index(currentNb)
    #             hostStatus = Status[hostIndex]
    #             nbStatus = Status[nbIndex]
    #             # Nothing happen
    #             # if((hostStatus == 'Susceptible') & (nbStatus == 'Susceptible')): break
    #             # if((hostStatus == 'Infected') & (nbStatus == 'Infected')): break
    #             # if((hostStatus == 'Infectious') & (nbStatus == 'Infectious')): break
    #             # if ((hostStatus == 'Recovered') & (nbStatus == 'Recovered')): break
    #
    #             # Infection occurred
    #             if((hostStatus == 'Infecious') & (nbStatus == 'Susceptible')):
    #                 print('Infection occurred')
    #                 incubation = np.random.lognormal(mean=1.621,
    #                                                  sigma= 0.418
    #                                                  )
    #                 while(incubation < 3):
    #                     incubation = np.random.lognormal(mean=1.621,
    #                                                      sigma= 0.418
    #                                                     )
    #                 infectiousAt = day + incubation - 3
    #                 recoverAt = day + incubation + 11
    #                 Status[nbIndex] = 'Infected'
    #                 Status_InfectiousAt[nbIndex] = infectiousAt
    #                 Status_RecoverAt[nbIndex] = recoverAt
    #
    #             elif((hostStatus == 'Susceptible') & (nbStatus == 'Infectious')):
    #                 incubation = np.random.lognormal(mean=1.621,
    #                                                  sigma=0.418
    #                                                  )
    #                 while (incubation < 3):
    #                     incubation = np.random.lognormal(mean=1.621,
    #                                                      sigma=0.418
    #                                                      )
    #                 infectiousAt = day + incubation - 3
    #                 recoverAt = day + incubation + 11
    #                 Status[hostIndex] = 'Infected'
    #                 Status_InfectiousAt[hostIndex] = infectiousAt
    #                 Status_RecoverAt[hostIndex] = recoverAt
        print('Day ' + str(day) + ': Finished')
        print()

    FinalStatusData = {
        'UsID': Status_UsID,
        'Status': Status,
        'InfectiousAt': Status_InfectiousAt,
        'RecoverAt': Status_RecoverAt
    }

    FinalStatusDf = pd.DataFrame(FinalStatusData, columns=['UsID', 'Status', 'InfectiousAt', 'RecoverAt'])
    FinalStatusDf.to_csv(outputStatusFile, header=True, index=False)

if __name__ == '__main__':
    # Simulation 1: Pre-emptive no Vaccine, 7 days
    runSimulation_PreEmptive(inputNetworksPrefix='../SimpleNetwork/DDT/ddtlink_simple_',
                             inputStatusFile='./Pre-emptive/RV/DDT_noVacc/initialStatus_noVacc.csv',
                             outputStatusFile='./Pre-emptive/RV/DDT_noVacc/result1.csv',
                             TOTAL_DAYS=7
                             )
    pass