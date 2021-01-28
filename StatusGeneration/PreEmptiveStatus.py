import pandas as pd
import numpy as np

## This is to generate the initial status files for pre-emptive simulation,
## The file is stored in the "./output" folder. There are initial status files for
## different strategies with multiple vaccination rate. There are total of 4 statuses:
## Susceptible, Infected, Infectious, Recovered (Vaccinated also counted as Recovered)
class PreEmptiveStatus:
    def __init__(self,
                 dataFolder,
                 linkFilePrefix,
                 ):
        self.dataFolder = dataFolder
        self.linkFilePrefix = linkFilePrefix
        self.totalDays = 7 # Get the data of the first 7 days
        self.status = []
        self.population = []
        self.finalDf = pd.DataFrame()
        pass

    # Get all user ID in the populations
    def getPopulation(self):
        allHost = pd.Series()
        for i in range(0, self.totalDays):
            data = pd.read_csv(self.dataFolder + "/" + self.linkFilePrefix + str(i) + ".csv",
                               names=['UsID', 'NbID', 'Hst', 'Hend', 'NbSt', 'Nbend'])
            nb = pd.Series(data.NbID.unique())
            host = pd.Series(data.UsID.unique())
            allHost = allHost.append(nb)
            allHost = allHost.append(host)
            pass
        self.population = allHost.unique().tolist()
        pass

    #
    def generateInitialStatus(self, outputFile):
        self.getPopulation()
        self.status = ["Susceptible" for i in range(len(self.population))]
        data = {
            "UsID": self.population,
            "Status": self.status,
            "InfectiousAt" : [-1] * len(self.population),
            "RecoverAt":[-1] * len(self.population)
        }
        self.finalDf = pd.DataFrame(
            data, columns=["UsID", "Status", "InfectiousAt","RecoverAt"]
        )
        self.finalDf.to_csv(outputFile, index=False)
        pass

    def generateRVStatus(self, initialStatusFile, # The file to be overwritten. Currently all users are susceptible
                         outputFile,
                         proportion # Proportion of population to be vaccinated
                         ):
        df = pd.read_csv(initialStatusFile)
        UserId = df['UsID'].tolist()
        Status = df['Status'].tolist()
        nToVaccinate = int(proportion * len(UserId))
        pInfectionProtection = 0.038 # 3.8% effective in protecting against infection


        ##  Comment and uncomment each of these section below for different strategy

        # ---- This is for RV -------
        toVaccinateIndex = np.random.choice(len(UserId), nToVaccinate) #Randomly choose

        for i in toVaccinateIndex:
            temp_prob = np.random.binomial(1, pInfectionProtection)
            if(temp_prob > 0):
                Status[i] = 'Recovered'

        # ---- This if for AV -------
        # AVRanking = pd.read_csv('./DDT-AVranking.csv', names=['UsID', 'AVRank'])
        # AVRanking = AVRanking.sort_values(['AVRank'], ascending=False)
        # nOfVacc = int(proportion * len(Status))
        #
        # UsList = AVRanking['UsID'].tolist()
        #
        # toVaccList = UsList[0:nOfVacc]
        # for toVacc in toVaccList:
        #     temp_prob = np.random.binomial(1, pInfectionProtection)
        #     if (temp_prob > 0):
        #         index = UserId.index(toVacc)
        #         Status[index] = 'Recovered'

        #----- This is for DV -------
        # Read the contact count csv
        # contactCount = pd.read_csv('./ContactCount.csv')
        # nOfVacc = int(proportion * len(Status))
        # countList = contactCount['UsID'].tolist()
        #
        # toVaccList = countList[0:nOfVacc]
        #
        # for toVacc in toVaccList:
        #     temp_prob = np.random.binomial(1, pInfectionProtection)
        #     if (temp_prob > 0):
        #         index = UserId.index(toVacc)
        #         Status[index] = 'Recovered'

        #----- This is for IMV -----
        # Read the ranking file
        # IMVRanking = pd.read_csv('./DDT-IMVranking.csv', names=['UsID', 'IMVrank', 'IMEVrank', 'IMTVrank', 'Degree'])
        # IMVRanking = IMVRanking.sort_values(['IMVrank'], ascending=False)
        # nOfVacc = int(proportion * len(Status))
        #
        # UsList = IMVRanking['UsID'].tolist()
        #
        # toVaccList = UsList[0:nOfVacc]
        # for toVacc in toVaccList:
        #     temp_prob = np.random.binomial(1, pInfectionProtection)
        #     if (temp_prob > 0):
        #         index = UserId.index(toVacc)
        #         Status[index] = 'Recovered'
        # ------------------------------------------------


        #Output data to csv file
        data = {
            "UsID": UserId,
            "Status": Status,
            "InfectiousAt": [-1] * len(UserId),
            "RecoverAt": [-1] * len(UserId)
        }

        outputDf = pd.DataFrame(data,
                                columns=["UsID", "Status", "InfectiousAt","RecoverAt"])
        outputDf.to_csv(outputFile, index=False)
        pass


if __name__ == '__main__':
    ###################### FOR DDT NETWORK #############################
    DDTStatus = PreEmptiveStatus(dataFolder= "../Data/SPDTNetwork/DDT",
                                 linkFilePrefix="bclink_",
                                 )
    ################### Generating Initial Status file #################
    # DDTStatus.generateInitialStatus(outputFile="./output/Pre-emptive/DDT/initialStatus.csv")

    ################### Generating Initial Status with RV strategy file #################
    DDTStatus.generateRVStatus(initialStatusFile="./output/Pre-emptive/DDT/initialStatus.csv",
                               outputFile="./output/Pre-emptive/DDT/DV/initialStatus_10.csv",
                               proportion = 0.1
                               )
    
    pass