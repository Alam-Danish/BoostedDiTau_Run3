import ROOT,sys
import os
from DataFormats.FWLite import Events, Handle
import numpy as np
import math

ROOT.gROOT.SetStyle('Plain')
ROOT.gROOT.SetBatch()

def delta_r(eta1, phi1, eta2, phi2):
    """Calculates Delta R between two particles."""
    dphi = ROOT.TVector2.Phi_mpi_pi(phi1 - phi2)
    deta = eta1 - eta2
    return math.sqrt(deta**2 + dphi**2)

masses=[25]

handleGenJet = Handle ('vector<reco::GenJet>')
labelGenJet = ('slimmedGenJets')

handleGenParticle = Handle ('vector<reco::GenParticle>')
labelGenParticle = ('prunedGenParticles')

handleTau = Handle('std::vector<pat::Tau>')
labelTau = ('slimmedTaus')

handleBoostedTau = Handle('std::vector<pat::Tau>')
labelBoostedTau = ('slimmedTausBoosted')

for mass in masses:
    # Create a directory for each mass point if it doesn't exist inside output directory
    if not os.path.exists(f"output/TCP_m{int(mass)}"):
        os.makedirs(f"output/TCP_m{int(mass)}")

    out=ROOT.TFile("output/TCP_m"+str(int(mass))+"/h_plotSignalGen_m"+str(int(mass))+"_miniAOD_v4.root",'recreate')

    hJet1Pt_miniAOD = ROOT.TH1F ("hJet1Pt_miniAOD", "leading jet Pt;P_{t};N_{events}", 100, 0, 500)
    hTcpPt_miniAOD = ROOT.TH1F ("hTcpPt_miniAOD", "TCP Pt;P_{t};N_{events}", 100, 0, 500)
    hTcpPt_mass_miniAOD = ROOT.TH1F("hTcpPt_mass_miniAOD", "TCP Mass;Mass;N_{events}", 20, 0, 100)

    h_dR_tautau_miniAOD = ROOT.TH1F("h_dR_tautau_miniAOD", "Delta R between the two taus from ALP decay;#Delta R;N_{events}", 50, 0, 5) 

    # GenTau histograms
    hGenTauPt_before_miniAOD = ROOT.TH1F ("hGenTauPt_before_miniAOD", "GenTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenTauEta_before_miniAOD = ROOT.TH1F ("hGenTauEta_before_miniAOD", "GenTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenTauPt_after_miniAOD = ROOT.TH1F ("hGenTauPt_after_miniAOD", "GenTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenTauEta_after_miniAOD = ROOT.TH1F ("hGenTauEta_after_miniAOD", "GenTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    # VisTau histograms
    hGenVisTauPt_before_miniAOD = ROOT.TH1F ("hGenVisTauPt_before_miniAOD", "GenVisTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenVisTauEta_before_miniAOD = ROOT.TH1F ("hGenVisTauEta_before_miniAOD", "GenVisTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenVisTauPt_after_miniAOD = ROOT.TH1F ("hGenVisTauPt_after_miniAOD", "GenVisTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenVisTauEta_after_miniAOD = ROOT.TH1F ("hGenVisTauEta_after_miniAOD", "GenVisTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    # hadronic visual tau histograms
    hGenHadVisTauPt_before_miniAOD = ROOT.TH1F ("hGenHadVisTauPt_before_miniAOD", "GenHadVisTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenHadVisTauEta_before_miniAOD = ROOT.TH1F ("hGenHadVisTauEta_before_miniAOD", "GenHadVisTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hGenHadVisTauPt_after_miniAOD = ROOT.TH1F ("hGenHadVisTauPt_after_miniAOD", "GenHadVisTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hGenHadVisTauEta_after_miniAOD = ROOT.TH1F ("hGenHadVisTauEta_after_miniAOD", "GenHadVisTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    # RecoTau histograms
    hRecTauPt_before_miniAOD = ROOT.TH1F ("hRecTauPt_before_miniAOD", "RecoTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hRecTauEta_before_miniAOD = ROOT.TH1F ("hRecTauEta_before_miniAOD", "RecoTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hRecTauPt_after_miniAOD = ROOT.TH1F ("hRecTauPt_after_miniAOD", "RecoTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hRecTauEta_after_miniAOD = ROOT.TH1F ("hRecTauEta_after_miniAOD", "RecoTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)

    # Boosted Tau histograms
    hBoostedRecTauPt_before_miniAOD = ROOT.TH1F ("hBoostedRecTauPt_before_miniAOD", "Boosted RecoTau Pt before preselection cut;P_{t};N_{events}", 100, 0, 500)
    hBoostedRecTauEta_before_miniAOD = ROOT.TH1F ("hBoostedRecTauEta_before_miniAOD", "Boosted RecoTau Eta before preselection cut;#eta;N_{events}", 100, -3, 3)
    hBoostedRecTauPt_after_miniAOD = ROOT.TH1F ("hBoostedRecTauPt_after_miniAOD", "Boosted RecoTau Pt after preselection cut;P_{t};N_{events}", 100, 0, 500)
    hBoostedRecTauEta_after_miniAOD = ROOT.TH1F ("hBoostedRecTauEta_after_miniAOD", "Boosted RecoTau Eta after preselection cut;#eta;N_{events}", 100, -3, 3)



    #events=Events("../../../CMSSW_12_4_14_patch3/src/ALP/TCP_m"+str(int(mass))+"_ht_100to400_miniAOD_Run3Summer22miniAODv4.root")
    events=Events("../../../AToTauTau/TCP_m25/M-AToTauTau_50000Events_MiniAOD_913736_merged.root")
    nevt=0
    for event in events:
        nevt+=1

        if nevt%1000==0: print("Processing event: ",nevt)
        #if nevt>10: break
    
        event.getByLabel(labelGenJet, handleGenJet)
    
        jets=[]
        for jet in handleGenJet.product():
            if jet.pt()<20 or abs(jet.eta())>2.5: continue
            jets+=[jet]
            
        jets.sort(key=lambda x: x.pt(), reverse=True)
        if len(jets)==0: continue
        jet1=ROOT.TLorentzVector(jets[0].px(), jets[0].py(), jets[0].pz(), jets[0].energy())
        hJet1Pt_miniAOD.Fill(jet1.Pt())

        #Particles handling
        event.getByLabel(labelGenParticle, handleGenParticle)
        particles=handleGenParticle.product()

        event.getByLabel(labelTau, handleTau)
        recoTaus=handleTau.product()

        event.getByLabel(labelBoostedTau, handleBoostedTau)
        recoTausBoosted=handleBoostedTau.product()

        # loop over gen particles to find pseudoscalar
        #print("event ",nevt)
        alp = []
        for p in particles:
            if abs(p.pdgId())==9999 and p.isLastCopy():
                alp_p4 = ROOT.TLorentzVector()
                alp_p4.SetPtEtaPhiM(p.pt(), p.eta(), p.phi(), p.mass())
                alp.append(alp_p4)
                hTcpPt_miniAOD.Fill(alp_p4.Pt())
                hTcpPt_mass_miniAOD.Fill(alp_p4.M())
                #print("Found ALP with pt=",p.pt()," eta=",p.eta()," phi=",p.phi()," mass=",p.mass(), "mother pdgId=",p.mother(0).pdgId(), p.mother(1).pdgId() if p.numberOfMothers()>1 else "")
                taus = []
                for d in p.daughterRefVector():
                    if abs(d.get().pdgId())==15:
                        taus.append(d.get())
                        d_vec=ROOT.TLorentzVector()
                        d_vec.SetPtEtaPhiM(d.get().pt(), d.get().eta(), d.get().phi(), d.get().mass())
                        hGenTauPt_before_miniAOD.Fill(d_vec.Pt())
                        hGenTauEta_before_miniAOD.Fill(d_vec.Eta())
                        if d_vec.Pt()>20 and abs(d_vec.Eta())<2.3:
                            hGenTauPt_after_miniAOD.Fill(d_vec.Pt())
                            hGenTauEta_after_miniAOD.Fill(d_vec.Eta())

                if len(taus)==2:
                    tau1=ROOT.TLorentzVector()
                    tau1.SetPtEtaPhiM(taus[0].pt(), taus[0].eta(), taus[0].phi(), taus[0].mass())
                    tau2=ROOT.TLorentzVector()
                    tau2.SetPtEtaPhiM(taus[1].pt(), taus[1].eta(), taus[1].phi(), taus[1].mass())
                    tcp = tau1+tau2
                    #hTcpPt_miniAOD.Fill(tcp.Pt())
                    #hTcpPt_mass_miniAOD.Fill(tcp.M())
                else:
                    print("Warning: ALP does not decay into 2 taus")
        tau_m = []
        tau_p = []
        nt1 = []
        nt2 = []
        leptons1 = []
        leptons2 = []
        for p in particles:
            if p.pdgId()==15 and p.mother().pdgId()==9999:
                tau_m.append(p)
            if p.pdgId()==16 and p.isDirectHardProcessTauDecayProductFinalState():
                nt1.append(p)
            if p.pdgId()==-15 and p.mother().pdgId()==9999:
                tau_p.append(p)
            if p.pdgId()==-16 and p.isDirectHardProcessTauDecayProductFinalState():
                nt2.append(p)
            if p.pdgId()==11 or p.pdgId()==13:
                if p.mother().pdgId()==15 and p.isDirectHardProcessTauDecayProductFinalState():
                    leptons1+=[p]
            if p.pdgId()==-11 or p.pdgId()==-13:
                if p.mother().pdgId()==-15 and p.isDirectHardProcessTauDecayProductFinalState():
                    leptons2+=[p]

                

        if len(tau_m)!=1 or len(tau_p)!=1:
            print("Warning: did not find both taus from ALP decay")

        if len(tau_m)==1 and len(tau_p)==1:
            # make TLorentz vectors
            tau1=ROOT.TLorentzVector()
            tau1.SetPtEtaPhiM(tau_m[0].pt(), tau_m[0].eta(), tau_m[0].phi(), tau_m[0].mass())
            tau2=ROOT.TLorentzVector()
            tau2.SetPtEtaPhiM(tau_p[0].pt(), tau_p[0].eta(), tau_p[0].phi(), tau_p[0].mass())
            nu1=ROOT.TLorentzVector()
            nu1.SetPtEtaPhiM(nt1[0].pt(), nt1[0].eta(), nt1[0].phi(), nt1[0].mass())
            nu2=ROOT.TLorentzVector()
            nu2.SetPtEtaPhiM(nt2[0].pt(), nt2[0].eta(), nt2[0].phi(), nt2[0].mass())
            vis_tau1 = tau1 - nu1
            vis_tau2 = tau2 - nu2
            dR_tautau = delta_r(tau1.Eta(), tau1.Phi(), tau2.Eta(), tau2.Phi())
            h_dR_tautau_miniAOD.Fill(dR_tautau)

            hGenVisTauPt_before_miniAOD.Fill(vis_tau1.Pt())
            hGenVisTauEta_before_miniAOD.Fill(vis_tau1.Eta())
            hGenVisTauPt_before_miniAOD.Fill(vis_tau2.Pt())
            hGenVisTauEta_before_miniAOD.Fill(vis_tau2.Eta())
            if vis_tau1.Pt()>20 and abs(vis_tau1.Eta())<2.3:
                hGenVisTauPt_after_miniAOD.Fill(vis_tau1.Pt())
                hGenVisTauEta_after_miniAOD.Fill(vis_tau1.Eta())
            if vis_tau2.Pt()>20 and abs(vis_tau2.Eta())<2.3:
                hGenVisTauPt_after_miniAOD.Fill(vis_tau2.Pt())
                hGenVisTauEta_after_miniAOD.Fill(vis_tau2.Eta())

        # get visible taus only for hadronic decays
            tau_m_d = [d.get().pdgId() for d in tau_m[0].daughterRefVector()]
            #print("daughter pdgId of tau-: ",tau_m_d)
            if any(abs(d) in [111, 211, 311, 321, 130, 310] for d in tau_m_d): # hadronic decay modes
                #print("hadronic decay mode found for tau-")
                tau_vis=ROOT.TLorentzVector()
                tau_vis.SetPtEtaPhiM(tau_m[0].pt(), tau_m[0].eta(), tau_m[0].phi(), tau_m[0].mass())
                nu1=ROOT.TLorentzVector()
                nu1.SetPtEtaPhiM(nt1[0].pt(), nt1[0].eta(), nt1[0].phi(), nt1[0].mass())
                tau_vis = tau_vis - nu1
                hGenHadVisTauPt_before_miniAOD.Fill(tau_vis.Pt())
                hGenHadVisTauEta_before_miniAOD.Fill(tau_vis.Eta())
                if tau_vis.Pt()>20 and abs(tau_vis.Eta())<2.3:
                    hGenHadVisTauPt_after_miniAOD.Fill(tau_vis.Pt())
                    hGenHadVisTauEta_after_miniAOD.Fill(tau_vis.Eta())
            tau_p_d = [d.get().pdgId() for d in tau_p[0].daughterRefVector()]
            #print("daughter pdgId of tau+: ",tau_p_d)
            if any(abs(d) in [111, 211, 311, 321, 130, 310] for d in tau_p_d): # hadronic decay modes
                #print("hadronic decay mode found for tau+")
                tau_vis=ROOT.TLorentzVector()
                tau_vis.SetPtEtaPhiM(tau_p[0].pt(), tau_p[0].eta(), tau_p[0].phi(), tau_p[0].mass())
                nu2=ROOT.TLorentzVector()
                nu2.SetPtEtaPhiM(nt2[0].pt(), nt2[0].eta(), nt2[0].phi(), nt2[0].mass())
                tau_vis = tau_vis - nu2
                hGenHadVisTauPt_before_miniAOD.Fill(tau_vis.Pt())
                hGenHadVisTauEta_before_miniAOD.Fill(tau_vis.Eta())
                if tau_vis.Pt()>20 and abs(tau_vis.Eta())<2.3:
                    hGenHadVisTauPt_after_miniAOD.Fill(tau_vis.Pt())
                    hGenHadVisTauEta_after_miniAOD.Fill(tau_vis.Eta())  

        for recoTau in recoTaus:
            #print("Reco tau decay mode: ",recoTau.decayMode())
            if recoTau.decayMode() in [5,6]: continue  # skip 3prong taus
            recoTau_vec=ROOT.TLorentzVector()
            recoTau_vec.SetPtEtaPhiM(recoTau.pt(), recoTau.eta(), recoTau.phi(), recoTau.mass())
            hRecTauPt_before_miniAOD.Fill(recoTau_vec.Pt())
            hRecTauEta_before_miniAOD.Fill(recoTau_vec.Eta())
            if recoTau_vec.Pt()>20 and abs(recoTau_vec.Eta())<2.3:
                hRecTauPt_after_miniAOD.Fill(recoTau_vec.Pt())
                hRecTauEta_after_miniAOD.Fill(recoTau_vec.Eta())

        for recoTau in recoTausBoosted:
            #print("Reco Boosted tau decay mode: ",recoTau.decayMode())
            if recoTau.decayMode() in [5,6]: continue  # skip 3prong taus
            recoTau_vec=ROOT.TLorentzVector()
            recoTau_vec.SetPtEtaPhiM(recoTau.pt(), recoTau.eta(), recoTau.phi(), recoTau.mass())
            hBoostedRecTauPt_before_miniAOD.Fill(recoTau_vec.Pt())
            hBoostedRecTauEta_before_miniAOD.Fill(recoTau_vec.Eta())
            if recoTau_vec.Pt()>40 and abs(recoTau_vec.Eta())<2.3:
                hBoostedRecTauPt_after_miniAOD.Fill(recoTau_vec.Pt())
                hBoostedRecTauEta_after_miniAOD.Fill(recoTau_vec.Eta())

    out.cd()
    hJet1Pt_miniAOD.Write()
    hTcpPt_miniAOD.Write()
    hTcpPt_mass_miniAOD.Write()
    h_dR_tautau_miniAOD.Write()
    hGenTauPt_before_miniAOD.Write()
    hGenTauPt_after_miniAOD.Write()
    hGenTauEta_before_miniAOD.Write()
    hGenTauEta_after_miniAOD.Write()
    hGenVisTauPt_before_miniAOD.Write()
    hGenVisTauPt_after_miniAOD.Write()
    hGenVisTauEta_before_miniAOD.Write()
    hGenVisTauEta_after_miniAOD.Write()
    hGenHadVisTauPt_before_miniAOD.Write()
    hGenHadVisTauPt_after_miniAOD.Write()
    hGenHadVisTauEta_before_miniAOD.Write()
    hGenHadVisTauEta_after_miniAOD.Write()
    hRecTauPt_before_miniAOD.Write()
    hRecTauPt_after_miniAOD.Write()
    hRecTauEta_before_miniAOD.Write()
    hRecTauEta_after_miniAOD.Write()
    hBoostedRecTauPt_before_miniAOD.Write()
    hBoostedRecTauPt_after_miniAOD.Write()
    hBoostedRecTauEta_before_miniAOD.Write()
    hBoostedRecTauEta_after_miniAOD.Write()
    out.Close()
