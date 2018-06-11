from pyAudioAnalysis import audioTrainTest as aT

aT.featureAndTrain(["classifierData/music","classifierData/speech"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "svm", "svmSMtemp", False)
aT.fileClassification("data/teste_3570_4139.wav", "svmSMtemp","svm")