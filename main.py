import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('EURUSD_Daily_Ask_2018.12.31_2019.10.05v2.csv')
df['Time (UTC)'] = pd.to_datetime(df['Time (UTC)'])
df.set_index('Time (UTC)', inplace=True)

sirIndex = df[pd.to_numeric(df['Volume'], errors='coerce').isnull()].index[0]  # detects the error
df = df.replace(df['Volume'][sirIndex], np.NaN)  # replaces error line with a NaN value

df['Volume'] = pd.to_numeric(df['Volume'])

dfB = pd.read_csv('EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv')
dfB['Time (UTC)'] = pd.to_datetime(dfB['Time (UTC)'])
dfB.set_index('Time (UTC)', inplace=True)

k = float(input("k value for standard deviation: "))
column = str(input("Column to look at. Options: Open, High, Low, Close, Volume  -->  "))

plt.plot(df[column])
plt.title("Before " + column)
plt.gcf().autofmt_xdate()
plt.show()

dfRemove = df.copy()
dfPrevious = df.copy()
dfInterpolate = df.copy()

meanAll = df[column].mean()
sdAll = df[column].std()


def isOutlier(dateIn, dataframe):
    if (meanAll - (k * sdAll)) < dataframe[column][pd.Timestamp(dateIn)] < (meanAll + (k * sdAll)):
        return False
    else:
        return True


def findAvalue(dateIn):
    value = df[column][pd.Timestamp(dateIn)]
    print("########################")
    print(dateIn, column)
    print(value)
    if isOutlier(dateIn, df):
        print("Is Outlier")
    else:
        print("Not an Outlier")
    return value


def removeOutlier(dateIn):
    if isOutlier(dateIn, dfRemove):
        # if an outlier it simply drops
        dfRemove.drop(pd.Timestamp(dateIn), inplace=True)
        print("removed outlier ")
        print(dateIn)
        print("\n")


def changeToPrevious(dateIn):
    dateInFormatted = pd.to_datetime(dateIn)  # to be compared with future i in the for
    if isOutlier(dateIn, dfPrevious):
        for i in dfPrevious[dateIn::-1].index.astype(str):  # reverse "for" starting in the date dateIn
            if len(dfPrevious[dateIn::-1]) == 1:
                dfPrevious.drop(pd.Timestamp(i), inplace=True)
            elif not isOutlier(i, dfPrevious):  # check if the previous is not an outlier
                if i != dateInFormatted:  # confirm it is not the same date
                    print("Row with index: ")
                    print(dateInFormatted)
                    print(" changed to " + i + "\n")
                    dfPrevious[column][pd.Timestamp(dateInFormatted)] = dfPrevious[column][
                        pd.Timestamp(i)]  # replace the value
                    break


def interpolation(dateIn):
    dateFormatted = pd.to_datetime(dateIn)
    listToDrop = []  # only used for the nextValues to prevent no Values not Outliers
    if isOutlier(dateIn, df):  # checks if it is an outlier
        if len(dfInterpolate[dateIn::-1]) > 1:  # checks if its not the first value of all
            previousDate = dfInterpolate[dateIn::-1].index[1]
            previousValue = dfInterpolate[column][pd.Timestamp(previousDate)]

            if isOutlier(previousDate, dfInterpolate):
                for i in dfInterpolate[dateIn::-1].index:
                    # goes on until it find a non-outlier value
                    if not isOutlier(i, dfInterpolate):
                        previousDate = dfInterpolate[i::-1].index.array[1]
                        previousValue = dfInterpolate[column][pd.Timestamp(previousDate)]
                        break
        else:
            # if it is the first value it drops the row
            dfInterpolate.drop(pd.Timestamp(dateFormatted), inplace=True)
            return

        if len(dfInterpolate[dateIn::1]) > 1:  # checks if it is the last value
            nextDate = dfInterpolate[dateIn::1].index[1]
            nextValue = dfInterpolate[column][pd.Timestamp(nextDate)]

            if isOutlier(nextDate, dfInterpolate):
                for i in dfInterpolate[dateIn::1].index:
                    # goes on until it finds a value or reaches the end
                    listToDrop.append(i)
                    if not isOutlier(i, dfInterpolate):
                        nextDate = dfInterpolate[i::1].index.array[1]
                        nextValue = dfInterpolate[column][pd.Timestamp(nextDate)]
                        break
                for j in listToDrop:  # if it doesnt find the value and reaches the end it drops all the rows from the
                    # starting point which are outliers
                    dfInterpolate.drop(pd.Timestamp(j), inplace=True)
                    return
        else:
            # if it is the last value it drops
            dfInterpolate.drop(pd.Timestamp(dateIn), inplace=True)
            return

        # calculates the interpolation result for each value
        final = interpolateFormula(dateFormatted, nextDate,
                                   previousDate, nextValue, previousValue)

        print("Value " + dfInterpolate[column][pd.Timestamp(dateIn)].astype(str) + " for column " + column + " and "
                                                                                                             "index"
                                                                                                             " ")
        print(dateIn)
        print("changed to " + final.astype(str) + "\n")
        dfInterpolate[column][pd.Timestamp(dateIn)] = final


def interpolateFormula(dateFormatted, nextDate, previousDate, nextValue, previousValue):
    result = previousValue + (nextValue - previousValue) * \
             ((dateFormatted - previousDate) / (nextDate - previousDate))

    return result


def variationClose():
    plt.style.use('ggplot')
    plt.hist(dfB['Close'].diff(), ec="black")
    plt.ylabel("Frequency")
    plt.title("Close Variation between a day and its previous day")
    plt.xlabel("Variation from the previous day")
    plt.show()


def highLow():
    plt.style.use('ggplot')
    plt.hist(dfB['High'] - dfB['Low'], ec="black")
    plt.ylabel("Frequency")
    plt.xlabel("Difference from High to Low")
    plt.title("High-Low Variation")
    plt.show()


def plotFunction(dfMix, title):
    plt.plot(dfMix[column])
    plt.title(title)
    plt.gcf().autofmt_xdate()
    plt.show()


if __name__ == '__main__':
    # Returns all values indicating which are outliers and those which are not
    for index in df.index:
        findAvalue(index)

    # Removes all outliers
    for index in dfRemove.index:
        removeOutlier(index)
    plotFunction(dfRemove, "After Removing Ouliers in column " + column + " with k=" + str(k))

    # Changes all outliers to the previous value. If no previous value "not outlier" it drops the row
    for index in dfPrevious.index:
        changeToPrevious(index)
    plotFunction(dfPrevious, "After Changing to Previous in column " + column + " with k=" + str(k))

    # Interpolates the results of the outliers with the previous and the next
    # If the next or previous values are outliers, it iterates until it finds a value which is not an outlier
    # If it reaches the end and hasn't found any value, it drops all the values starting from the former mentioned
    for index in dfInterpolate.index:
        interpolation(index)
    plotFunction(dfInterpolate, "After Interpolation in column " + column + " with k=" + str(k))

    variationClose()

    highLow()

    plt.plot(dfB['Open'])
    plt.title("Open EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv")
    plt.gcf().autofmt_xdate()
    plt.show()

    plt.plot(dfB['High'])
    plt.title("High EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv")
    plt.gcf().autofmt_xdate()
    plt.show()

    plt.plot(dfB['Low'])
    plt.title("Low EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv")
    plt.gcf().autofmt_xdate()
    plt.show()

    plt.plot(dfB['Close'])
    plt.title("Close EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv")
    plt.gcf().autofmt_xdate()
    plt.show()

    plt.plot(dfB['Volume'])
    plt.title("Volume EURUSD_Daily_Ask_2009.10.07_2019.10.07.csv")
    plt.gcf().autofmt_xdate()
    plt.show()
