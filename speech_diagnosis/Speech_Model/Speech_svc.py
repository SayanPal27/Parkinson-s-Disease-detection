# -*- coding: utf-8 -*-
"""Parkinsons_SVC.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OGWnzOQT_giPQhSrErcLHeKYZx25GVqa
"""

!pip install lime

# Commented out IPython magic to ensure Python compatibility.
# %cd drive/My\ Drive/ML/Parkinsons

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import confusion_matrix,  precision_recall_curve, auc, accuracy_score, roc_curve, f1_score
from sklearn.metrics import matthews_corrcoef
from numpy import sqrt
from numpy import argmax 
import matplotlib.pyplot as plt

"""##Extracting required data"""

data = pd.read_csv('train_data.txt', sep=",", header=None)
data.columns = ["Subject id", "Jitter (local)" ,"Jitter (local, absolute)" ,"Jitter (rap)" ,"Jitter (ppq5)", "Jitter (ddp)", "Shimmer (local)", "Shimmer (local, dB)" ,"Shimmer (apq3)", "Shimmer (apq5)", "Shimmer (apq11)", "Shimmer (dda)", "AC" ,"NTH" ,"HTN", "Median pitch", "Mean pitch", "Standard deviation", "Minimum pitch", "Maximum pitch", "Number of pulses", "Number of periods", "Mean period", "Standard deviation of period", "Fraction of locally unvoiced frames", "Number of voice breaks", "Degree of voice breaks", "UPDRS", "class information"]
data.shape

y_updrs = data.UPDRS # for regression
y_class_info = data["class information"]#for classification
data_x = data.drop(labels=['UPDRS', "Subject id", "class information"], axis=1, inplace = False)
print(data_x.shape, y_updrs.shape, y_class_info.shape)

# min_max_scaler = preprocessing.MinMaxScaler()
# data_x = min_max_scaler.fit_transform(data_x)

"""## Selection of the best model using cross validation  """

from sklearn.svm import SVC
from sklearn.model_selection import KFold

total_folds = 10
kfold = KFold(n_splits= total_folds, shuffle=True, random_state=42)

acc_per_fold = []
fold=0

for train_index, test_index in kfold.split(data_x, y_class_info):
    fold+=1
    X_train, X_test, y_train, y_test =  data_x.iloc[train_index], data_x.iloc[test_index], y_class_info.iloc[train_index], y_class_info.iloc[test_index]

    svc_clf = SVC(kernel='rbf', gamma =0.001, probability=True)
    svc_clf.fit(X_train, y_train)

    y_pred = svc_clf.predict(X_test)

    print("\nFold : ",fold,"\n")

    
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    print("Average Accuracy : " ,(tp+tn)/(tp+tn+fp+fn))
    print("Sensitivity: ",(tp)/(tp+fn))
    print("Specificity: ",(tn)/(tn+fp))
    print("MCC: ",matthews_corrcoef(y_test, y_pred))
        
    print(svc_clf.score(X_test, y_test))

    acc_per_fold.append(svc_clf.score(X_test, y_test))

for i in range(total_folds):
    print("Fold ", i, "accuracy", acc_per_fold[i])

print("\nMean Accuracy = ",np.mean(acc_per_fold),'(+/-',np.std(acc_per_fold),')');

"""## Training the Best Model"""

X_train, X_test, y_train, y_test =train_test_split(data_x, y_class_info, test_size=0.20, random_state=42)

svc_clf = SVC(kernel='rbf', gamma =0.001, probability=True)
svc_clf.fit(X_train, y_train)

y_pred = svc_clf.predict(X_test)

tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

print("Average Accuracy : " ,(tp+tn)/(tp+tn+fp+fn))
print("Sensitivity: ",(tp)/(tp+fn))
print("Specificity: ",(tn)/(tn+fp))
print("MCC: ",matthews_corrcoef(y_test, y_pred))
print("F-measure", f1_score(y_test, y_pred))
print(svc_clf.score(X_test, y_test))

import seaborn as sn
array = confusion_matrix(y_test, y_pred)
df_cm = pd.DataFrame(array, index = [i for i in ["non - PD", "PD"]],
                columns = [i for i in ["non-PD","PD"]])
accuracy_thr = accuracy_score(y_test, y_pred)

plt.figure(figsize = (10,7))
sn.heatmap(df_cm, cmap="YlGnBu", annot=True, annot_kws={"fontsize":48})
sn.set(font_scale=1.4)
plt.savefig("SVM_Conf_orig_matrix.png", bbox_inches = "tight")

"""##ROC and PR"""

y_score = svc_clf.predict_proba(X_test)
print(len(y_test), len(y_score))

fpr, tpr, thresholds = roc_curve(y_test, y_score[:, 1])
roc_auc = auc(fpr, tpr)
gmeans = sqrt(tpr * (1-fpr))
arg_g = argmax(gmeans)
print('Best Threshold=%f, G-Mean=%.3f' % (thresholds[arg_g], gmeans[arg_g]))
best_threshold = thresholds[arg_g]
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
acc = accuracy_score(y_test, y_pred)
# tpr = tp/(tp+fn)
# fpr = fp/(fp+tn)
# tnr = tn/(fp+tn)
# fnr = fn/(tp+fn)

print("accuracy = ", acc, "\nroc_auc = ", roc_auc)

i=0
roc_table = pd.DataFrame(columns=["Threshold", "TPR (Sensitivity)",
                                  "FPR (Fall-out)", "Specificity",
                                  " (LR+)" ,"Youden index","Sensitivity + Specificity",
                                  "G-mean"], index=[_ for _ in range(len(thresholds))])

for fp_rate, tp_rate, thresh in zip(fpr, tpr, thresholds):
    spec = 1-fp_rate
    lrplus = tp_rate/fp_rate
    y_ind = tp_rate - fp_rate
    sen_sp = tp_rate + spec
    g_mean =  (tp_rate*spec)**(1/2)
    roc_table.iloc[i] = [thresh, tp_rate, fp_rate, spec, lrplus, y_ind, sen_sp, g_mean ]
    i+=1

# Commented out IPython magic to ensure Python compatibility.
# %cd ../../../..

pd.set_option("display.precision", 4)
roc_table.to_csv("SVM_ROC_Table.csv")
roc_table

plt.subplots(1, figsize=(7,7))
plt.title('Receiver Operating Characteristic')
plt.plot(fpr, tpr, marker = "." ,label = 'AUC = %0.2f' % roc_auc)
#plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'--', label = "No Skill")

plt.scatter(fpr[arg_g], tpr[arg_g], marker='o', color='black', label='Best')
# plt.xlim([0, 1])
# plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.legend(["ROC", "No Skill"], loc ="lower right")

plt.savefig("SVM_ROC.jpg", bbox_inches= "tight")
plt.show()

precision, recall, thresholds = precision_recall_curve(y_test, y_score[:,1])

fscore_ = (2 * precision * recall) / (precision + recall)
# locate the index of the largest f score
ix = argmax(fscore_)
print('Best Threshold=%f, F-Score=%.3f' % (thresholds[ix], fscore_[ix]))

pr_table = pd.DataFrame(columns=["Threshold", "Precision",
                                  "Recall", "F-Measure"], 
                                index=[_ for _ in range(len(thresholds))])

i=0
for pre, rec, thresh in zip(precision, recall, thresholds):
    fscore = (2 * pre * rec) / (pre + rec)
    pr_table.iloc[i] = [thresh, pre, rec, fscore]
    i+=1

roc_table.to_csv("SVM_PR_Table.csv")

pr_table

plt.subplots(1, figsize=(7,7))
plt.title('Precision-Recall Curve')
plt.plot(recall, precision)
plt.plot([0, 1], [0.725, 0.725], linestyle='--')
plt.legend(loc = 'lower right')
# plt.xlim([0, 1])
# plt.ylim([0, 1])
plt.scatter(recall[ix], precision[ix], marker='o', color='black', label='Best')
# axis labels
plt.ylabel('Precision')
plt.xlabel('Recall')
plt.legend(["PR","No Skill"], loc ="upper right")

plt.savefig("SVM_PR.jpg", bbox_inches="tight")
plt.show()

"""##After threshold tuning"""

y_pred_thr = [ 1 if _ >= best_threshold else 0 for _ in svc_clf.predict_proba(X_test)[:,1]]
print(best_threshold)
accuracy_thr = accuracy_score(y_test, y_pred_thr)
print("New accuracy ",accuracy_thr)
tn_thr, fp_thr, fn_thr, tp_thr = confusion_matrix(y_test, y_pred_thr).ravel()

print("Average Accuracy : " ,(tp_thr+tn_thr)/(tp_thr+tn_thr+fp_thr+fn_thr))
print("Sensitivity: ",(tp_thr)/(tp_thr+fn_thr))
print("Specificity: ",(tn_thr)/(tn_thr+fp_thr))
print("MCC: ",matthews_corrcoef(y_test, y_pred_thr))
print("F-measure : ",f1_score(y_test, y_pred))

import seaborn as sn
array = confusion_matrix(y_test, y_pred_thr)
df_cm = pd.DataFrame(array, index = [i for i in ["non - PD", "PD"]],
                columns = [i for i in ["non-PD","PD"]])
accuracy_thr = accuracy_score(y_test, y_pred_thr)

plt.figure(figsize = (10,7))
sn.heatmap(df_cm, cmap="YlGnBu", annot=True, annot_kws={"fontsize":48})
sn.set(font_scale=1.4)
plt.savefig("SVM_Conf_matrix.png", bbox_inches = "tight")

count=0
for i, j in zip(y_pred_thr, y_test):
    if i==0 and j==0:
        count+=1
print(count)

"""## Preparing data for LIME analysis"""

X_t = X_test.iloc[1]
X_t = X_t[np.newaxis,:]

print(svc_clf.predict_proba(X_t))

features = data_x.columns.to_list()
features

"""#LIME interpretation"""

import lime
import lime.lime_tabular
import lime.explanation
explainer = lime.lime_tabular.LimeTabularExplainer(X_train.values, feature_names=features, class_names=np.array(["non-PD", "PD"]), discretize_continuous=True)

exp = explainer.explain_instance(X_test.iloc[1].values, svc_clf.predict_proba, num_features=26, top_labels=26)

svc_clf.predict(X_test.iloc[i].values.reshape(1,-1))

"""#Analysing the Lime values by
###1. Checking if the predicted value is equal to the real value
###2. If **not equal** then proceed to the next iteration else if **equal** continue to to step 3
###3. call analyse_expl_map() to create a map of the explainer -> which would create a list of tuples i.e. [(weight, para).....] sort it in descending order and then pass the top five elements of the list to add_to_top_five()
###4. add_to_top_five would update the frequency of the aparameters in top_five_gen dictoionary.
"""

def add_to_top_five(res_):
    for weight, para in res_:
        top_five_gen[(para,weight)] = top_five_gen.get(para, 0)+1

def analyse_expl_map(t, ind):
    t = exp.as_map()
    res = []
    for ele in t[ind]:
        i,j = ele
        res.append((j,features[i]))

    res.sort(reverse = True)
    add_to_top_five(res[:])

top_five_gen = {}
for i in range(X_test.shape[0]):
    pr = svc_clf.predict(X_test.iloc[i].values.reshape(1,-1))
    real = y_test.iloc[i]
    if pr==real:
        expl_ = explainer.explain_instance(X_test.iloc[i].values, svc_clf.predict_proba, num_features=26, top_labels=26)
        analyse_expl_map(expl_, pr[0])

sort_top_five_gen = sorted(top_five_gen.items(), key=lambda x: x[1], reverse=True)
print(sort_top_five_gen)

##Testing
t = exp.as_list()
res = []
for i,j in t:
    res.append((j,i))
res.sort(reverse =True)
res

exp.show_in_notebook(show_table=True, show_all=True)