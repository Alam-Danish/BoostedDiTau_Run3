HTBIN = ["100to400","400toInf"]

for i in range(10,70,5):
    for htbin in HTBIN:
        path = "TCP_m"+str(i)+"/TCP_m"+str(i)+"_ht_"+htbin
        f = open(path+"/TCP_m"+str(i)+"_ht_"+htbin+"_extramodels.dat", "w")
        f.write("SM_alp_UFO.tar.gz")
        f.close()
