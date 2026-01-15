import ROOT
from ROOT import TFile, TH1F, TLorentzVector

# Open the NanoAOD file
file = TFile.Open("data/data.root")
if not file or file.IsZombie():
    raise RuntimeError("Could not open ROOT file")

# Get the Events tree
Events = file.Get("Events")
if not Events:
    raise RuntimeError("Events tree not found")

total_events = Events.GetEntries()
print("Total number of events:", total_events)

# Invariant mass histogram
h_mumu = TH1F(
    "h_mumu",
    "J/#psi #rightarrow #mu^{+}#mu^{-};m_{#mu#mu} [GeV];Events",
    120, 2.5, 3.5
)

mu1 = TLorentzVector()
mu2 = TLorentzVector()

# Progress counter
event_count = 0

# Event loop
for event in Events:

    event_count += 1
    if event_count % 100000 == 0:
        print(f"Processed {event_count}/{total_events} events")

    good_muons = []

    # Loop over muons in the event
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

    # Build opposite-sign muon pairs
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
            h_mumu.Fill(m_mumu)

print("Event loop completed")

fit_func = ROOT.TF1(
    "fit_func",
    "gaus(0) + pol0(3)",
    2.9, 3.3
)

# Initial parameter guesses
fit_func.SetParameters(
    h_mumu.GetMaximum(),  # amplitude
    3.1,                  # mean
    0.05,                 # sigma
    100                   # background
)

h_mumu.Fit("fit_func", "R")

# Extract fit parameters
mass  = fit_func.GetParameter(1)
sigma = fit_func.GetParameter(2)

print(f"Fitted J/psi mass      = {mass:.4f} GeV")
print(f"Detector resolution σ  = {sigma:.4f} GeV")
# Draw and save the plot
canvas = ROOT.TCanvas("c", "c", 800, 600)
h_mumu.Draw()
canvas.SaveAs("plots/jpsi_invariant_mass.png")

out = ROOT.TFile("plots/jpsi_data.root", "RECREATE")
h_mumu.Write()
out.Close()

print("Histogram saved to plots/jpsi_data.root")
print("Analysis complete. Plot saved to plots/jpsi_invariant_mass.png")

