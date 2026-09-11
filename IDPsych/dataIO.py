from pymatreader import read_mat
import numpy as np
import os
import json
from IDPsych import calc

def allSubjectDict(sjID):
    '''
    Creates a master dictionary containing all subjects' data
    (calls loadMatFilePyMat to load data files from individual subject)
    :param sjID: specifies which subjects are used for data analysis 
    '''
    allSubject = {}
    for sj in sjID:
        allSubject[sj] = loadMatFilePyMat(sj)
    return allSubject
    

def loadMatFilePyMat(sj, elim = 10, method = 0, last = 10, lastRev = 6):
    '''
    Loads the given matfile and assigns variables to access trial data.
    Returns a dictionary containing:
        1. Task settings
        2. Behavioral settings
        3. Dot settings
        4. Trials data 
    :param sj: specifies which subject's data files are loaded
    :param elim: specifies how many certified trials are eliminated at the 
                 beginning when calculating the hit rate (0 by default)
    :param method: use which method to calculate threshold (0, 1, or 2)
    :param last: specifies how many trials are used to average in method 1
    :param lastRev: specifies how many reversals are used to average in method 2
    '''
    
    os.chdir(os.getcwd() + '/' + sj)
    
    fileList = [name for name in os.listdir() if (name.endswith('.mat') and ('Info' not in name))]
    fileList.sort()
    # Get the unique dates
    fileListDate = list(set([fileList[d][:10] for d in range(len(fileList))]))
    fileListDate.sort()
    
    sjData = {'fileName': fileList,
              'nTrials': [],
              'taskMode': [],
              'stairType': [],
              'frameRateHz': [],
              'baseCohPC': [],
              'behavSettings': [],
              'dotSettings': [],
              'trials': [],
              'rightBiasPC': [],
              'thresholdPC': [],
              'hitRatePC': [],
              'dayOfExp': []}
    
    for fi in fileList:
        allTrials = read_mat(fi)
        allTrialsData = allTrials['trials']
        fileInfo = allTrials['file']
        
        nTrials = len(allTrialsData['trial'])
        sjData['nTrials'].append(nTrials)
        
        # Add task mode: 0 for Dec and 1 for Inc
        sjData['taskMode'].append(allTrialsData['trial'][0]['taskMode'])
        
        # Add staircase type: 0 for joint staircase
        sjData['stairType'].append(allTrialsData['trial'][0]['stairType'])
        sjData['frameRateHz'].append(fileInfo['frameRateHz']['data'])
        baseline = allTrialsData['trial'][0]['baseCohPC']
        sjData['baseCohPC'].append(allTrialsData['trial'][0]['baseCohPC'])
        
        # Add behavioral settings
        sjData['behavSettings'].append({'baseDurMS': allTrialsData['trial'][0]['baseDurMS'],
                                        'stepDurMS': allTrialsData['trial'][0]['stepDurMS'],
                                        'revBeforeChange': 6,
                                        'maxStepPC': abs(allTrialsData['trial'][0]['threshStepsPC']),
                                        'minStepPC': abs(allTrialsData['trial'][-1]['threshStepsPC']),
                                        'stepChangeFactor': 0.5})
        # Add random dot settings
        dots = allTrialsData['randomDots'][0]
        sjData['dotSettings'].append({'azimuthDeg': dots['azimuthDeg'],
                                      'elevationDeg': dots['elevationDeg'],
                                      'radiusDeg': dots['radiusDeg'],
                                      'densityDPD': dots['density'],
                                      'diameterDeg': dots['dotDiameterDeg'],
                                      'speedDPS': dots['speedDPS'],
                                      'lifeFrames': dots['lifeFrames']})
        
        # Add trial codes - 
        # :trialCertify: 0 if the trial is qualified
        # :eotCode: 0 for hits and 1 for misses
        # :stepDir: should stay the same if the staircase is unidirectional, 0 for Dec and 1 for Inc
        # :changeLoc: 0 for left and 1 for right
        sjData['trials'].append({'trialCertify': allTrialsData['trialCertify'],
                                 'eotCode': allTrialsData['eotCode'],
                                 'stepDir': [allTrialsData['trial'][tr]['stepDir'] for tr in range(nTrials)],
                                 'changeLoc': [allTrialsData['trial'][tr]['changeLoc'] for tr in range(nTrials)],
                                 'stepSizePC': [abs(allTrialsData['trial'][tr]['threshStepsPC']) for tr in range(nTrials)],
                                 'trialCohPC': [allTrialsData['trial'][tr]['stepCohPC'] for tr in range(nTrials)]})
       
        # A trial is "certified" only when trialCertify = 0 and eotCode = 0 or 1
        se = fileList.index(fi)
        cert = np.array(sjData['trials'][se]['trialCertify'])
        eot = np.array(sjData['trials'][se]['eotCode'])
        testCertify = np.logical_and(cert == 0, np.logical_or(eot == 1, eot == 0))
        # sjData['trials'][se]['testCertify'] = testCertify
        
        # Add right bias: use only the certified trials
        # right bias = right responses - right changes
        loc = sjData['trials'][se]['changeLoc']
        locFiltered = [loc[tr] for tr in range(nTrials) if testCertify[tr]]
        eotFiltered = [eot[tr] for tr in range(nTrials) if testCertify[tr]]
        rightChanges = sum(locFiltered)
        rightResponses = len([1 for tr in range(len(locFiltered)) if locFiltered[tr] + eotFiltered[tr] == 1])
        sjData['rightBiasPC'].append((rightResponses - rightChanges) / len(locFiltered) * 100)
        
        # Add threshold: by default, use the coherence of the last trial as threshold measurement
        coh = sjData['trials'][se]['trialCohPC']
        cohFiltered = [coh[tr] for tr in range(nTrials) if testCertify[tr]]
        sjData['thresholdPC'].append(calc.threshold(cohFiltered, eotFiltered, baseline, method, last, lastRev))
        
        
        # Add hit rate: use only the certified trials, by default, take all certified trials
        sjData['hitRatePC'].append(calc.hitRate(eotFiltered, elim))
        
        # Add the day of experiment session, separately labeled for Inc/Dec sessions
        sjData['dayOfExp'].append(fileListDate.index(fi[:10]) // 2 + 1)
        
    os.chdir(os.getcwd()[:-3])
    return sjData


def saveDict(data, fileName):
    """
    Exports the data dictionary to a .json file
    Make sure the working directory is switched to the data output folder
    :param data: the input dictionary
    :param fileName: the customized file name without extension
    """
    json.dump(data, open(fileName + '.json', 'w' ))