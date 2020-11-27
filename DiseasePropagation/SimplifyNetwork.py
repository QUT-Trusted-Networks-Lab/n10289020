import numpy as np
import pandas as pd
from TransmissionProbability import calculateTransProbability

def readOneDayFile(filePath):
    '''
    Read a single file
    :param filePath: CSV file path
    :return: All columns as lists
    '''
    df = pd.read_csv(filePath, names=['HostID', 'NbID', 'HostSt', 'HostEnd', 'NbSt', 'NbEnd'])
    HostID = df['HostID'].tolist()
    NbID = df['NbID'].tolist()
    HostSt = df['HostSt'].tolist()
    HostEnd = df['HostEnd'].tolist()
    NbSt = df['NbSt'].tolist()
    NbEnd = df['NbEnd'].tolist()

    return HostID, NbID, HostSt, HostEnd, NbSt, NbEnd

def writeOneDayFile(outputFilePath, df):
    df.to_csv(outputFilePath, index=False)
    pass

def simplifyNetwork(inputFilePathPrefix, outputFilePathPrefix):
    TOTAL_DAYS = 32
    for i in range(TOTAL_DAYS):
        print("Begin simplify day: " + str(i))
        HostID, NbID, HostSt, HostEnd, NbSt, NbEnd = readOneDayFile(inputFilePathPrefix + str(i) + '.csv')
        Probability = []
        # Calculate the transmission probability
        for j in range(len(HostSt)):
            prob = calculateTransProbability(HostSt[j],
                                             HostEnd[j],
                                             NbSt[j],
                                             NbEnd[j]
                                             )
            Probability.append(prob)
            if(j % 1000000 == 0):
                print(str(j) + " Links Simplified. " + str(len(HostSt) - j) + " records remaining.")
        data = {
            'HostID': HostID,
            'NbID': NbID,
            'Prob': Probability
        }
        df = pd.DataFrame(data, columns=['HostID', 'NbID', 'Prob'])
        writeOneDayFile(outputFilePath= outputFilePathPrefix + str(i) + '.csv',
                        df= df
                        )
        print("Finish Day: "+str(i))
        pass


if __name__ == '__main__':
    ##################### Simplify DDT Network #####################
    simplifyNetwork(inputFilePathPrefix='../Data/SPDTNetwork/DDT/bclink_',
                    outputFilePathPrefix='../Data/SimpleNetwork/DDT/ddtlink_simple_'
                    )
    pass
