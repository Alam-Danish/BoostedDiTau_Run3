HTBIN = ["100to400","400toInf"]

for i in range(10,70,5):
    for htbin in HTBIN:
        path = "TCP_m"+str(i)+"/TCP_m"+str(i)+"_ht_"+htbin
        toWrite = """
import model SM_alp_UFO

generate p p > alp j , alp > ta+ ta-
add process p p > alp j j , alp > ta+ ta-

output TCP_m"""+str(i)+"""_ht_"""+htbin+""" -nojpeg
"""
        with open(path+"/TCP_m"+str(i)+"_ht_"+htbin+"_proc_card.dat", "w") as f:
            f.writelines(toWrite)

        print(path+"/TCP_m"+str(i)+"_ht_"+htbin+"_proc_card.dat created")
