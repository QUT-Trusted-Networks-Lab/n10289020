import pandas as pd
import numpy as np
class PreEmptiveStatus:
    def __init__(self,
                 dataFolder,
                 linkFilePrefix,
                 ):
        self.dataFolder = dataFolder
        self.linkFilePrefix = linkFilePrefix
        self.totalDays = 7
        self.status = []
        self.population = []
        self.finalDf = pd.DataFrame()
        pass

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

    def generateRVStatus(self, initialStatusFile,
                         outputFile,
                         proportion
                         ):
        df = pd.read_csv(initialStatusFile)
        UserId = df['UsID'].tolist()
        Status = df['Status'].tolist()
        nToVaccinate = int(proportion * len(UserId))

        # ---- This is for RV -------
        # toVaccinateIndex = np.random.choice(len(UserId), nToVaccinate) #Randomly choose
        # for i in toVaccinateIndex:
        #     Status[i] = 'Recovered'

        # ---- This if for AV -------
        AVRanking = pd.read_csv('./DDT-AVranking.csv', names=['UsID', 'AVRank'])
        AVRanking = AVRanking.sort_values(['AVRank'], ascending=False)
        nOfVacc = int(proportion * len(Status))

        UsList = AVRanking['UsID'].tolist()

        toVaccList = UsList[0:nOfVacc]
        for toVacc in toVaccList:
            index = UserId.index(toVacc)
            Status[index] = 'Recovered'

        #----- This is for DV -------
        # Read the contact count csv
        # contactCount = pd.read_csv('./ContactCount.csv')
        # nOfVacc = int(proportion * len(Status))
        # countList = contactCount['UsID'].tolist()
        #
        # toVaccList = countList[0:nOfVacc]
        #
        # for toVacc in toVaccList:
        #     index = UserId.index(toVacc)
        #     Status[index] = 'Recovered'

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
        #     index = UserId.index(toVacc)
        #     Status[index] = 'Recovered'
        # ------------------------------------------------

        #Change Status to recover


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
                               outputFile="./output/Pre-emptive/DDT/AV/initialStatus_1.csv",
                               proportion = 0.01 # % of the population is vaccinated
                               )
    
    pass