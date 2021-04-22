import csv
input_file = csv.DictReader(open("data.csv",encoding="utf-8-sig"))
for i in input_file:
  #VRF_Name=i["GW_ IP_Address"]
#facts =dict(i)
 #print (VRF_Name)
#print (i.values())
#print (i.keys())
 a=(i["PRI_Node_ IP"])
 print("A value is:{}".format(a))
#import pandas as pd
#df = pd.read_csv("data.csv")
#df.columns
#print (df.iloc[0,1])
#path = "C:\users\gmohan\python\data.csv"
#file = open(path)
#for line in file:

