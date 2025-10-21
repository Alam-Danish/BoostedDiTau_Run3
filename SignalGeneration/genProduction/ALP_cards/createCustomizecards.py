import os

HTBIN = ["100to400","400toInf"]

for i in range(10,70,5):
    for htbin in HTBIN:
        path = "TCP_m"+str(i)+"/TCP_m"+str(i)+"_ht_"+htbin
        if not os.path.exists(path) : os.makedirs(path)
        f = open(path+"/TCP_m"+str(i)+"_ht_"+htbin+"_customizecards.dat", "w")
        f.write("set param_card mass 9999 "+str(i))
        f.close()
        print(path+"/TCP_m"+str(i)+"_ht_"+htbin+"_customizecards.dat created")
