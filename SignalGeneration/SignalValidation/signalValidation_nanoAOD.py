import ROOT,sys
import os
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

ROOT.gROOT.SetStyle('Plain')
ROOT.gROOT.SetBatch()

masses=[25]


def hasFlag(particle, bit):
    """Check if a given statusFlag bit is set for a GenPart"""
    return (particle.statusFlags & (1 << bit)) != 0


for mass in masses:
    if not os.path.exists(f"output/TCP_m{int(mass)}"):
        os.makedirs(f"output/TCP_m{int(mass)}")

    #fin = f"../../../CMSSW_12_4_14_patch3/src/ALP/TCP_m30_ht_100to400_nanoAOD_Run3Summer22nanoAODv12_modified.root"
    fin = f"../../../AToTauTau/M-AToTauTau_50000Events_NanoAOD_913736_merged.root"
    f = ROOT.TFile.Open(fin)
    tree = f.Get("Events")

    fout = ROOT.TFile(f"output/TCP_m{mass}/genReco_taus_TCP_m{mass}_nanoAOD_v4.root","RECREATE")

    # Create histograms and make y axis logarithmic
    hJet1Pt_nanoAOD = ROOT.TH1F ("hJet1Pt_nanoAOD", "leading jet Pt;P_{t};N_{events}", 100, 0, 500)
    hTcpPt_nanoAOD = ROOT.TH1F ("hTcpPt_nanoAOD", "TCP Pt;P_{t};N_{events}", 100, 0, 500)

    hGenTauPt_before_nanoAOD = ROOT.TH1F ("hGenTauPt_before_nanoAOD", "GenTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenTauEta_before_nanoAOD = ROOT.TH1F ("hGenTauEta_before_nanoAOD", "GenTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenTauPt_after_nanoAOD = ROOT.TH1F ("hGenTauPt_after_nanoAOD", "GenTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenTauEta_after_nanoAOD = ROOT.TH1F ("hGenTauEta_after_nanoAOD", "GenTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    hGenVisTauPt_before_nanoAOD = ROOT.TH1F ("hGenVisTauPt_before_nanoAOD", "GenVisTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenVisTauEta_before_nanoAOD = ROOT.TH1F ("hGenVisTauEta_before_nanoAOD", "GenVisTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenVisTauPt_after_nanoAOD = ROOT.TH1F ("hGenVisTauPt_after_nanoAOD", "GenVisTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenVisTauEta_after_nanoAOD = ROOT.TH1F ("hGenVisTauEta_after_nanoAOD", "GenVisTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    hGenHadVisTauPt_before_nanoAOD = ROOT.TH1F ("hGenHadVisTauPt_before_nanoAOD", "GenHadVisTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenHadVisTauEta_before_nanoAOD = ROOT.TH1F ("hGenHadVisTauEta_before_nanoAOD", "GenHadVisTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenHadVisTauPt_after_nanoAOD = ROOT.TH1F ("hGenHadVisTauPt_after_nanoAOD", "GenHadVisTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenHadVisTauEta_after_nanoAOD = ROOT.TH1F ("hGenHadVisTauEta_after_nanoAOD", "GenHadVisTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    hRecTauPt_before_nanoAOD = ROOT.TH1F ("hRecTauPt_before_nanoAOD", "RecoTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hRecTauEta_before_nanoAOD = ROOT.TH1F ("hRecTauEta_before_nanoAOD", "RecoTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hRecTauPt_after_nanoAOD = ROOT.TH1F ("hRecTauPt_after_nanoAOD", "RecoTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hRecTauEta_after_nanoAOD = ROOT.TH1F ("hRecTauEta_after_nanoAOD", "RecoTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    hBoostedRecTauPt_before_nanoAOD = ROOT.TH1F ("hBoostedRecTauPt_before_nanoAOD", "Boosted RecoTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hBoostedRecTauEta_before_nanoAOD = ROOT.TH1F ("hBoostedRecTauEta_before_nanoAOD", "Boosted RecoTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hBoostedRecTauPt_after_nanoAOD = ROOT.TH1F ("hBoostedRecTauPt_after_nanoAOD", "Boosted RecoTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hBoostedRecTauEta_after_nanoAOD = ROOT.TH1F ("hBoostedRecTauEta_after_nanoAOD", "Boosted RecoTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    #events=Events("../../../CMSSW_12_4_14_patch3/src/ALP/TCP_m"+str(int(mass))+"_ht_100to400_miniAOD_Run3Summer22miniAODv4.root")
    #events=Events("../../../AToTauTau/TCP_m25/M-AToTauTau_50000Events_MiniAOD_913736_merged.root")
    nevt=0
    for event in tree:
        nevt+=1

        if nevt%10000==0: print("Processing event: ",nevt)
        #if nevt>30: break
    
        genJet = Collection(event, "GenJet")
    
        jets=[]
        for jet in genJet:
            if jet.pt<20 or abs(jet.eta)>2.5: continue
            jets+=[jet]

        jets.sort(key=lambda x: x.pt, reverse=True)
        if len(jets)==0: continue
        hJet1Pt_nanoAOD.Fill(jets[0].pt)

        genPart = Collection(event, "GenPart")
        genVisTaus = Collection(event, "GenVisTau")
        recoTaus = Collection(event, "Tau")
        recoTausBoosted = Collection(event, "boostedTau")


        #print("event ",nevt)
        alp = []
        for p in genPart:
            if abs(p.pdgId)==9999 and hasFlag(p, 13):
                alp.append(p)
                #print("Found ALP with pt=",p.pt," eta=",p.eta," phi=",p.phi," mass=",p.mass, "mother pdgId=",genPart[p.genPartIdxMother].pdgId if p.genPartIdxMother>=0 else "none")

        #print("Number of ALPs found: ", len(alp))
        for a in alp:
            genTaus = []
            for p in genPart:
                if abs(p.pdgId)==15 and p.genPartIdxMother==a._index and genPart[p.genPartIdxMother].pdgId==9999:
                    genTaus.append(p)
                    #print("Found tau with pt=",p.pt," eta=",p.eta," phi=",p.phi," mass=",p.mass)
                    hGenTauPt_before_nanoAOD.Fill(p.pt)
                    hGenTauEta_before_nanoAOD.Fill(p.eta)
                    if p.pt>20 and abs(p.eta)<2.3:
                        hGenTauPt_after_nanoAOD.Fill(p.pt)
                        hGenTauEta_after_nanoAOD.Fill(p.eta)
            if len(genTaus)==2:
                hTcpPt_nanoAOD.Fill(genTaus[0].pt + genTaus[1].pt)

            for gt in genTaus:
                daughters = []
                for p in genPart:
                    if p.genPartIdxMother >= 0 and p.genPartIdxMother == gt._index and hasFlag(p, 5):  # isDirectPromptTauDecayProduct
                        daughters.append(p)
                    elif p.genPartIdxMother >= 0 and genPart[p.genPartIdxMother].genPartIdxMother == gt._index and genPart[genPart[p.genPartIdxMother].genPartIdxMother] == gt and hasFlag(p, 2):  # isTauDecayProduct
                        daughters.append(p)
                #print(f"daughters: {[p.pdgId for p in daughters]}")

                charged_hadrons = [p for p in daughters if abs(p.pdgId) in [211, 321]]
                neutral_hadrons = [p for p in daughters if abs(p.pdgId) in [111, 130, 310, 311]]
                tau_neutrinos = [p for p in daughters if abs(p.pdgId) == 16]
                electrons = [p for p in daughters if abs(p.pdgId) == 11]
                muons = [p for p in daughters if abs(p.pdgId) == 13]
                n_charged = len(charged_hadrons)
                n_neutral = len(neutral_hadrons)
                n_electrons = len(electrons)
                n_muons = len(muons)

                if any(abs(d.pdgId) in [111, 211, 311, 321, 130, 310] for d in daughters):
                    gt.decayMode = "had"
                    visTau = gt.p4() -  tau_neutrinos[0].p4() if tau_neutrinos else gt.p4()
                    hGenHadVisTauPt_before_nanoAOD.Fill(visTau.Pt())
                    hGenHadVisTauEta_before_nanoAOD.Fill(visTau.Eta())
                    if visTau.Pt()>20 and abs(visTau.Eta())<2.3:
                        hGenHadVisTauPt_after_nanoAOD.Fill(visTau.Pt())
                        hGenHadVisTauEta_after_nanoAOD.Fill(visTau.Eta())

        for visTau in genVisTaus:
            hGenVisTauPt_before_nanoAOD.Fill(visTau.pt)
            hGenVisTauEta_before_nanoAOD.Fill(visTau.eta)
            if visTau.pt>20 and abs(visTau.eta)<2.3:
                hGenVisTauPt_after_nanoAOD.Fill(visTau.pt)
                hGenVisTauEta_after_nanoAOD.Fill(visTau.eta)

        for recoTau in recoTaus:
            #print("Reco tau decay mode: ",recoTau.decayMode)
            hRecTauPt_before_nanoAOD.Fill(recoTau.pt)
            hRecTauEta_before_nanoAOD.Fill(recoTau.eta)
            if recoTau.pt>20 and abs(recoTau.eta)<2.3:
                hRecTauPt_after_nanoAOD.Fill(recoTau.pt)
                hRecTauEta_after_nanoAOD.Fill(recoTau.eta)

        for recoTau in recoTausBoosted:
            #print("Reco boosted tau decay mode: ",recoTau.decayMode)
            hBoostedRecTauPt_before_nanoAOD.Fill(recoTau.pt)
            hBoostedRecTauEta_before_nanoAOD.Fill(recoTau.eta)
            if recoTau.pt>20 and abs(recoTau.eta)<2.3:
                hBoostedRecTauPt_after_nanoAOD.Fill(recoTau.pt)
                hBoostedRecTauEta_after_nanoAOD.Fill(recoTau.eta)


        

    fout.cd()
    hJet1Pt_nanoAOD.Write()
    hTcpPt_nanoAOD.Write()
    hGenTauPt_before_nanoAOD.Write()
    hGenTauPt_after_nanoAOD.Write()
    hGenTauEta_before_nanoAOD.Write()
    hGenTauEta_after_nanoAOD.Write()
    hGenVisTauPt_before_nanoAOD.Write()
    hGenVisTauPt_after_nanoAOD.Write()
    hGenVisTauEta_before_nanoAOD.Write()
    hGenVisTauEta_after_nanoAOD.Write()
    hGenHadVisTauPt_before_nanoAOD.Write()
    hGenHadVisTauPt_after_nanoAOD.Write()
    hGenHadVisTauEta_before_nanoAOD.Write()
    hGenHadVisTauEta_after_nanoAOD.Write()
    hRecTauPt_before_nanoAOD.Write()
    hRecTauPt_after_nanoAOD.Write()
    hRecTauEta_before_nanoAOD.Write()
    hRecTauEta_after_nanoAOD.Write()
    hBoostedRecTauPt_before_nanoAOD.Write()
    hBoostedRecTauPt_after_nanoAOD.Write()
    hBoostedRecTauEta_before_nanoAOD.Write()
    hBoostedRecTauEta_after_nanoAOD.Write()
    fout.Close()
