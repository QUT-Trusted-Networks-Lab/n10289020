import pandas as pd

def getPopulation(inputFilePrefix,
                  DAYS = 7
                  ):
    population = []
    for day in range(DAYS):
        df = pd.read_csv(f'{inputFilePrefix}{day}.csv', names=['UsID', 'NbID', 'HSt', 'HEnd', 'NbSt', 'NbEnd'])
        current = df.UsID.unique()
        population = population + current
        population = list(dict.fromkeys(population))
    return population
    pass

def countContacts(inputFilePrefix,
                  outputFile,
                  DAYS = 7
                  ):
    contactCount = {}
    for day in range(DAYS):
        df = pd.read_csv(f'{inputFilePrefix}{day}.csv', names=['UsID', 'NbID', 'HSt', 'HEnd', 'NbSt', 'NbEnd'])
        for index, row in df.iterrows():
            currentHost = row['UsID']
            currentNb = row['NbID']
            if currentHost in contactCount.keys():
                contactCount[currentHost] += 1
            else:
                contactCount[currentHost] = 0

            if currentNb in contactCount.keys():
                contactCount[currentNb] += 1
            else:
                contactCount[currentNb] = 0

        # current = df.UsID.unique()
        #
        #
        # for i in range(len(current)):
        #     host = current[i]
        #     nOfContact = len(df.loc[(df['UsID'] == host) | (df['NbID'] == host)])
        #
        #     if host in contactCount.keys():
        #         contactCount[host] += nOfContact
        #     else:
        #         contactCount[host] = 0
    outDf = pd.DataFrame(data={
        'UsID': contactCount.keys(),
        'ContactCount': contactCount.values()
    }, columns=['UsID', 'ContactCount'])

    outDf = outDf.sort_values(by=['ContactCount'], ascending=False)
    outDf.to_csv(outputFile, index=False)
    pass

if __name__ == '__main__':
    print(countContacts(inputFilePrefix='../Data/SPDTNetwork/DDT/bclink_',
                        outputFile='./ContactCount.csv',
                        DAYS=7
                        ))
    pass