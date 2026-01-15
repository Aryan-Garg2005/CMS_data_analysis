import ROOT
from ROOT import TFile, TH1F, TLorentzVector

#Open the MC NanoAOD file
file = TFile.Open("data/mc_data.root")
if not file or file.IsZombie():
    raise RuntimeError("Could not open MC ROOT file")

Events = file.Get("Events")
if not Events:
    raise RuntimeError("Events tree not found")

total_events = Events.GetEntries()
print("Total number of MC events:", total_events)

# Histogram for dimuon invariant mass (MC)
h_mumu_mc = TH1F(
    "h_mumu_mc",
    "MC J/#psi #rightarrow #mu^{+}#mu^{-};m_{#mu#mu} [GeV];Normalized events",
    120, 2.5, 3.5
)

mu1 = TLorentzVector()
mu2 = TLorentzVector()


# Event loop (IDENTICAL selection to data)
event_count = 0

for event in Events:

    event_count += 1
    if event_count % 100000 == 0:
        print(f"Processed {event_count}/{total_events} MC events")

    good_muons = []

    for i in range(event.nMuon):

        if event.Muon_pt[i] < 4.0:
            continue
        if abs(event.Muon_eta[i]) > 2.4:
            continue
        if not event.Muon_looseId[i]:
            continue
        if not (event.Muon_isGlobal[i] or event.Muon_isTracker[i]):
            continue

        good_muons.append(i)

    for i in range(len(good_muons)):
        for j in range(i + 1, len(good_muons)):

            idx1 = good_muons[i]
            idx2 = good_muons[j]

            if event.Muon_charge[idx1] * event.Muon_charge[idx2] >= 0:
                continue

            mu1.SetPtEtaPhiM(
                event.Muon_pt[idx1],
                event.Muon_eta[idx1],
                event.Muon_phi[idx1],
                event.Muon_mass[idx1]
            )

            mu2.SetPtEtaPhiM(
                event.Muon_pt[idx2],
                event.Muon_eta[idx2],
                event.Muon_phi[idx2],
                event.Muon_mass[idx2]
            )

            m_mumu = (mu1 + mu2).M()
            h_mumu_mc.Fill(m_mumu)

print("MC event loop completed")


# Normalize MC histogram (shape comparison only)
if h_mumu_mc.Integral() > 0:
    h_mumu_mc.Scale(1.0 / h_mumu_mc.Integral())

out = ROOT.TFile("plots/jpsi_mc.root", "RECREATE")
h_mumu_mc.Write()
out.Close()

# Draw and save MC plot
canvas = ROOT.TCanvas("c_mc", "c_mc", 800, 600)
h_mumu_mc.Draw("HIST")

canvas.SaveAs("plots/jpsi_mc_invariant_mass.png")

print("MC plot saved to plots/jpsi_mc_invariant_mass.png")
print("MC analysis complete.")
