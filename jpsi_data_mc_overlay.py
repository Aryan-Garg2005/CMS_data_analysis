import ROOT


# Open ROOT files
f_data = ROOT.TFile.Open("plots/jpsi_data.root")
f_mc   = ROOT.TFile.Open("plots/jpsi_mc.root")

if not f_data or f_data.IsZombie():
    raise RuntimeError("Could not open plots/jpsi_data.root")

if not f_mc or f_mc.IsZombie():
    raise RuntimeError("Could not open plots/jpsi_mc.root")

h_data = f_data.Get("h_mumu")
h_mc   = f_mc.Get("h_mumu_mc")

if not h_data or not h_mc:
    raise RuntimeError("Histograms not found in ROOT files")


# Normalize BOTH histograms (shape comparison)
if h_data.Integral() > 0:
    h_data.Scale(1.0 / h_data.Integral())

if h_mc.Integral() > 0:
    h_mc.Scale(1.0 / h_mc.Integral())

# Styling
h_data.SetMarkerStyle(20)
h_data.SetMarkerSize(0.9)
h_data.SetLineColor(ROOT.kBlack)

h_mc.SetLineColor(ROOT.kRed)
h_mc.SetLineWidth(2)

h_data.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
h_data.GetYaxis().SetTitle("Normalized events")


# FORCE Y-AXIS RANGE  (CRITICAL FIX)
max_data = h_data.GetMaximum()
max_mc   = h_mc.GetMaximum()
max_val  = max(max_data, max_mc)

h_data.SetMaximum(1.3 * max_val)
h_data.SetMinimum(0.0)


# Draw
c = ROOT.TCanvas("c", "Data vs MC", 800, 600)
c.SetTicks(1, 1)

h_data.Draw("E")
h_mc.Draw("HIST SAME")


# Legend
leg = ROOT.TLegend(0.60, 0.72, 0.88, 0.88)
leg.SetBorderSize(0)
leg.SetFillStyle(0)

leg.AddEntry(h_data, "CMS Data", "lep")
leg.AddEntry(h_mc, "Simulation", "l")
leg.Draw()


# Save
c.SaveAs("plots/jpsi_data_vs_mc.png")

print("Data vs MC overlay saved to plots/jpsi_data_vs_mc.png")

