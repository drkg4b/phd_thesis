#!/bin/python
'''
Script to generate the trigger efficiency curve.
'''

import time
import os
from os import walk

from ROOT import *

gROOT.LoadMacro('AtlasStyle.C')
SetAtlasStyle()


# Turn off graphics on screen
gROOT.SetBatch(True)

RED = '\033[0;91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BLINK = '\033[5m'


def get_sample_list(path):
    '''
    Gets the sample list from a version directory.
    '''
    samples = [os.path.join(r, f) for r, subdir, files in walk(path) if
               "minitrees.root" in r for f in files]

    return samples


def get_tchain(top_dir):
    '''
    Function to create a chain of root files from a directory.
    '''
    file_list = get_sample_list(top_dir)

    chain_file = TFile.Open(file_list[0])

    tree_name = chain_file.GetListOfKeys().At(0).GetName()

    chain = TChain(tree_name)

    print BOLD + BLINK + 'Constructing TChain...' + ENDC

    for _file in file_list:

        chain.Add(_file)

        # print chain.GetEntries()

    print BOLD + 'Done!' + ENDC

    return chain


def do_efficiency_curve(chain):
    '''
    Gets a chain as argument and constructs the efficiency curve.
    '''
    entries = chain.GetEntries()

    output_file = TFile('trigger_efficiency.root', 'recreate')

    h_after_selection_p1 = TH1F('h_after_selection_p1', '', 50, 0, 1000)
    h_after_selection_p2 = TH1F('h_after_selection_p2', '', 50, 0, 1000)
    h_after_selection_p3 = TH1F('h_after_selection_p3', '', 50, 0, 1000)
    h_after_selection_p4 = TH1F('h_after_selection_p4', '', 50, 0, 1000)

    h_before_selection_p1 = TH1F('h_before_selection_p1', '', 50, 0, 1000)
    h_before_selection_p2 = TH1F('h_before_selection_p2', '', 50, 0, 1000)
    h_before_selection_p3 = TH1F('h_before_selection_p3', '', 50, 0, 1000)
    h_before_selection_p4 = TH1F('h_before_selection_p4', '', 50, 0, 1000)

    g_efficiency_p1 = TGraphAsymmErrors(50)
    g_efficiency_p2 = TGraphAsymmErrors(50)
    g_efficiency_p3 = TGraphAsymmErrors(50)
    g_efficiency_p4 = TGraphAsymmErrors(50)

    g_efficiency_p1.SetName('g_efficiency_p1')
    g_efficiency_p2.SetName('g_efficiency_p2')
    g_efficiency_p3.SetName('g_efficiency_p3')
    g_efficiency_p4.SetName('g_efficiency_p4')

    h_after_selection_p1.Sumw2()
    h_after_selection_p2.Sumw2()
    h_after_selection_p3.Sumw2()
    h_after_selection_p4.Sumw2()

    h_before_selection_p1.Sumw2()
    h_before_selection_p2.Sumw2()
    h_before_selection_p3.Sumw2()
    h_before_selection_p4.Sumw2()

    h_after_selection_p1.SetDirectory(output_file)
    h_after_selection_p2.SetDirectory(output_file)
    h_after_selection_p3.SetDirectory(output_file)
    h_after_selection_p4.SetDirectory(output_file)

    h_before_selection_p1.SetDirectory(output_file)
    h_before_selection_p2.SetDirectory(output_file)
    h_before_selection_p3.SetDirectory(output_file)
    h_before_selection_p4.SetDirectory(output_file)

    print BOLD + BLINK + 'Filling the histograms...' + ENDC

    # entries = 100000

    for entry in range(entries):

        if (entry % 500000 == 0 and entry > 0):

            print entry

        chain.GetEntry(entry)

        mu_pt_eta = [i for i in zip(chain.mu_pt, chain.mu_eta) if i[0] > 10000
                     and abs(i[1]) < 2.5]

        pass_muon_cut = len(mu_pt_eta) == 1

        # Require exactly one muon:
        if not pass_muon_cut:

            continue

        el_pt_eta = [i for i in zip(chain.el_pt, chain.el_eta) if i[0] > 20000
                     and abs(i[1]) < 2.47]

        pass_el_cut = len(el_pt_eta) == 0

        # Veto electrons:
        if not pass_el_cut:

            continue

        n_jets = len(chain.jet_pt)

        jet_pt_eta = [i for i in zip(chain.jet_pt, chain.jet_eta) if i[0] >
                      30000 and abs(i[1]) < 2.8]

        jet_met_nomuon_dphi = [i for i in chain.jet_met_nomuon_dphi if i > 0.4]

        pass_jet_cuts = len(jet_pt_eta) < 5 and \
                        len(jet_met_nomuon_dphi) == n_jets

        # Require at most 4 jets with delta_phi > 0.4
        if not pass_jet_cuts:

            continue

        is_first_period = (chain.run >= 296939 and chain.run <= 302393)
        is_second_period = (chain.run >= 302737  and chain.run <= 302872)
        is_third_period = (chain.run >= 302919 and chain.run <= 304008)
        is_fourth_period = (chain.run >= 304128 and chain.run <= 310216)

        pass_muon_trigger = (chain.trigger_HLT_mu24_ivarmedium or
                             chain.trigger_HLT_mu26_ivarmedium)

        # pass_muon_trigger = chain.trigger_HLT_mu26_ivarmedium

        if is_first_period:

            if pass_muon_trigger:

                h_before_selection_p1.Fill(chain.met_nomuon_tst_et * .001)

                if chain.trigger_HLT_xe80_tc_lcw_L1XE50 or \
                   chain.trigger_HLT_xe90_mht_L1XE50:

                    h_after_selection_p1.Fill(chain.met_nomuon_tst_et * .001)

        if is_second_period:

            if pass_muon_trigger:

                h_before_selection_p2.Fill(chain.met_nomuon_tst_et * .001)

                if chain.trigger_HLT_xe90_mht_L1XE50:

                    h_after_selection_p2.Fill(chain.met_nomuon_tst_et * .001)

        if is_third_period:

            if pass_muon_trigger:

                h_before_selection_p3.Fill(chain.met_nomuon_tst_et * .001)

                if chain.trigger_HLT_xe100_mht_L1XE50 or \
                   chain.trigger_HLT_xe110_mht_L1XE50:

                    h_after_selection_p3.Fill(chain.met_nomuon_tst_et * .001)

        if is_fourth_period:

            if pass_muon_trigger:

                h_before_selection_p4.Fill(chain.met_nomuon_tst_et * .001)

                if chain.trigger_HLT_xe110_mht_L1XE50:

                    h_after_selection_p4.Fill(chain.met_nomuon_tst_et * .001)


    print BOLD + 'Done!' + ENDC

    h_after_selection_p1.Write()
    h_after_selection_p2.Write()
    h_after_selection_p3.Write()
    h_after_selection_p4.Write()

    h_before_selection_p1.Write()
    h_before_selection_p2.Write()
    h_before_selection_p3.Write()
    h_before_selection_p4.Write()

    g_efficiency_p1.Divide(h_after_selection_p1, h_before_selection_p1,
                           "cl=0.683 b(1,1) mode")
    g_efficiency_p2.Divide(h_after_selection_p2, h_before_selection_p2,
                           "cl=0.683 b(1,1) mode")
    g_efficiency_p3.Divide(h_after_selection_p3, h_before_selection_p3,
                           "cl=0.683 b(1,1) mode")
    g_efficiency_p4.Divide(h_after_selection_p4, h_before_selection_p4,
                           "cl=0.683 b(1,1) mode")

    g_efficiency_p1.Write()
    g_efficiency_p2.Write()
    g_efficiency_p3.Write()
    g_efficiency_p4.Write()

    output_file.Close()


def make_pretty_plot(period):
    '''
    Produce the decorated canvas.
    '''
    in_file = TFile('trigger_efficiency.root', 'read')

    canv = TCanvas()

    if period == 'all':

        graph_p1 = in_file.Get('g_efficiency_p1')
        graph_p2 = in_file.Get('g_efficiency_p2')
        graph_p3 = in_file.Get('g_efficiency_p3')
        graph_p4 = in_file.Get('g_efficiency_p4')

        canv.cd()

        graph_p1.GetXaxis().SetTitle('E_{T}^{miss} (no muons) [GeV]')
        graph_p1.GetYaxis().SetTitle('Efficiency')

        graph_p2.SetMarkerStyle(33)
        graph_p2.SetMarkerColor(38)

        graph_p3.SetMarkerStyle(23)
        graph_p3.SetMarkerColor(46)

        graph_p4.SetMarkerStyle(21)
        graph_p4.SetMarkerColor(9)

        graph_p1.Draw('ap')
        graph_p2.Draw('samep')
        graph_p3.Draw('samep')
        graph_p4.Draw('samep')

        latex = TLatex(1100, 1925, '#bf{#splitline{Data 2015 + 2016, #sqrt{s} = 13'\
                       'TeV, 36.1 fb^{-1}}{W #rightarrow #mu#nu selection}}')

        latex.SetNDC()
        latex.SetX(.35)
        latex.SetY(.47)
        latex.SetTextAlign(11)
        latex.SetTextSize(.03)
        # latex.SetTextColor(1)
        # latex.SetTextFont(42)

        latex.Draw('same')

        leg = TLegend(0.35, 0.21, 0.63, 0.43)

        leg.AddEntry(graph_p1, "Data period 1", 'p')
        leg.AddEntry(graph_p2, "Data period 2", 'p')
        leg.AddEntry(graph_p3, "Data period 3", 'p')
        leg.AddEntry(graph_p4, "Data period 4", 'p')

        leg.Draw('same')

        canv.Print('output/trigger_efficiency.png')
        canv.Print('output/trigger_efficiency.pdf')
        canv.Print('output/trigger_efficiency.root')

    else:

        graph_name = 'g_efficiency_' + period

        graph = in_file.Get(graph_name)

        canv.cd()

        graph.GetXaxis().SetTitle('E_{T}^{miss} [GeV]')
        graph.GetYaxis().SetTitle('Efficiency')

        graph.Draw('ap')

        canv.Print('output/trigger_efficiency_' + period + '.png')
        canv.Print('output/trigger_efficiency_' + period + '.pdf')


def main():
    '''
    Main function to run the script.
    '''
    path = 'data/'

    # chain = get_tchain(path)

    # do_efficiency_curve(chain)

    periods = ('all', 'p1', 'p2', 'p3', 'p4')

    for period in periods:

        make_pretty_plot(period)


if __name__ == '__main__':

    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
