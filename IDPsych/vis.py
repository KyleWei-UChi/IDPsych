import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import sem


def IDscat(data):
    background_color = "#fbfbfb"
    IDscat = plt.figure(figsize=(6,6))
    IDscat.patch.set_facecolor(background_color)
    sjID = list(set(data))
    sjID.sort()
    threshInc = []
    threshDec = []
    for sj in sjID:
        taskMode = data[sj]['taskMode']
        thresholdPC = data[sj]['thresholdPC']
        Inc = np.array([thresholdPC[se] for se in range(len(thresholdPC)) if taskMode[se] == 1])
        Dec = np.array([thresholdPC[se] for se in range(len(thresholdPC)) if taskMode[se] == 0])

        threshInc.extend(Inc)
        threshDec.extend(Dec)

        plt.scatter(np.mean(Inc), np.mean(Dec), c = '#002d1d' , s = 40, alpha = 0.8)
        plt.errorbar(x = np.mean(Inc), y = np.mean(Dec), xerr = sem(Inc)*2,
                     yerr = sem(Dec)*2, ecolor = '#002d1d', linewidth = 1)

    plt.xlim([0,50])
    plt.ylim([0,50])
    plt.plot([0, 50], [0, 50], 'k--', linewidth = 1)
    plt.xlabel('Increment (%)', fontsize = 14, fontfamily = 'serif')
    plt.ylabel('Decrement (%)', fontsize = 14, fontfamily = 'serif')
    sns.histplot(x = threshInc, bins = 10, color = '#0e4f66', alpha = 0.6, element = 'step', linewidth = 0, kde = True)
    sns.histplot(y = threshDec, bins = 10, color = 'gray', alpha = 0.6, element = 'step', linewidth = 0, kde = True)
    plt.text(0, 52, 'Inc/Dec Thresholds', fontweight = 'bold', fontsize = 14, fontfamily = 'serif')
    plt.show()
    IDscat.savefig('thresholds.pdf')

def hitRateHist(data):
    hitRateHist = plt.figure()
    background_color = "#fbfbfb"
    hitRateHist.patch.set_facecolor(background_color)
    hitInc = []
    hitDec = []
    sjID = list(set(data))
    sjID.sort()
    for sj in sjID:
        taskMode = data[sj]['taskMode']
        hitAll = data[sj]['hitRatePC']
        hitInc.extend([hitAll[se] for se in range(len(hitAll)) if taskMode[se] == 1])
        hitDec.extend([hitAll[se] for se in range(len(hitAll)) if taskMode[se] == 0])

    plt.hist(hitInc, 10, color = '#0e4f66', alpha = 0.6)
    plt.hist(hitDec, 10, color = 'gray', alpha = 0.6)
    plt.xlim([60, 90])
    plt.xlabel('Hit Rate (%)', fontsize = 14, fontfamily = 'serif')
    plt.ylabel('Count', fontsize = 14, fontfamily = 'serif')
    plt.text(60, 21, 'Hit Rate Distribution', fontweight = 'bold', fontsize = 14, fontfamily = 'serif')
    plt.show()
    hitRateHist.savefig('hitRate.pdf')

def rBias(data):
    rBias = plt.figure()
    background_color = "#fbfbfb"
    rBias.patch.set_facecolor(background_color)
    rBiasInc = []
    rBiasDec = []
    sjID = list(set(data))
    sjID.sort()
    for sj in sjID:
        taskMode = data[sj]['taskMode']
        rBiasAll = data[sj]['rightBiasPC']
        rBiasInc.extend([rBiasAll[se] for se in range(len(rBiasAll)) if taskMode[se] == 1])
        rBiasDec.extend([rBiasAll[se] for se in range(len(rBiasAll)) if taskMode[se] == 0])
    sns.violinplot(data = [np.array(rBiasInc), np.array(rBiasDec)], palette = {0: '#0e4f66', 1: 'gray'})
    plt.xticks([0, 1], ['Increment', 'Decrement'], fontsize = 14, fontfamily = 'serif')
    plt.ylabel('R Bias (%)', fontsize = 14, fontfamily = 'serif')
    plt.text(-0.5, 21, 'R Bias', fontweight = 'bold', fontsize = 14, fontfamily = 'serif')
    plt.show()
    rBias.savefig('rBias.pdf')