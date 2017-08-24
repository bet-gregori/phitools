#!/usr/bin/env python

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from SDFhelper import *
from moleculeHelper import *
import argparse, sys

sep = '\t'

def compare(args):

    ###########################
    ### Store the compounds ###
    ###########################
    fpA = getFPdict (args.format, args.filea, molID= args.id, smilesI= args.col)
    namesA = list(fpA.keys())
    nA = len(namesA)

    if args.fileb is not None:
        fpB = getFPdict (args.format, args.fileb, molID= args.id, smilesI= args.col)
        namesB = list(fpB.keys())
        nB = len(namesB)
    
    #################################
    ### Get compound similarities ###
    #################################

    simD = {}
    if args.sim == 'max': startSim = 0
    else: startSim = 1

    # Work with only one input file
    if args.fileb is None:
        for name in namesA:
            simD[name] = ['', startSim]

        for i in range(nA):
            name1 = namesA[i]
            fp1 = fpA[name1]            
            for j in range(i+1, nA):
                name2 = namesA[j]
                fp2 = fpA[name2]

                sim = DataStructs.TanimotoSimilarity(fp1, fp2)
                if args.cutoff is not None and sim < args.cutoff:
                    continue

                if args.sim == 'all':
                    args.out.write('{}\t{}\t{}\n'.format(name1, name2, sim))
                    args.out.write('{}\t{}\t{}\n'.format(name2, name1, sim))
                else:
                    if args.sim == 'max':
                        if sim > simD[name1][1]: simD[name1] = [name2, sim]
                        if sim > simD[name2][1]: simD[name2] = [name1, sim]
                    else:
                        if sim < simD[name1][1]: simD[name1] = [name2, sim]
                        if sim < simD[name2][1]: simD[name2] = [name1, sim]

        if args.sim != 'all':
            for name in simD:
                args.out.write('{}\t{}\t{}\n'.format(name, simD[name][0], simD[name][1]))

    # Work with two input files
    else:
        for name in namesA:
            simD[name] = ['', startSim]
        for name in namesB:
            simD[name] = ['', startSim]

        for i in range(nA):
            name1 = namesA[i]
            fp1 = fpA[name1]            
            for j in range(nB):
                name2 = namesB[j]
                fp2 = fpB[name2]

                sim = DataStructs.TanimotoSimilarity(fp1, fp2)
                if args.cutoff is not None and sim < args.cutoff:
                    continue

                if args.sim == 'all':
                    args.out.write('{}\t{}\t{}\n'.format(name1, name2, sim))
                else:
                    if args.sim == 'max':
                        if sim > simD[name1][1]: simD[name1] = [name2, sim]
                    else:
                        if sim < simD[name1][1]: simD[name1] = [name2, sim]

        if args.sim != 'all':
            for name in simD:
                args.out.write('{}\t{}\t{}\n'.format(name, simD[name][0], simD[name][1]))
                        


def main ():
    parser = argparse.ArgumentParser(description='Get the smilarity between the compounds in the input file if only one is provided or between files if two are provided.')
    parser.add_argument('-a', '--filea', type=argparse.FileType('rb'), help='Input file.', required=True)
    parser.add_argument('-b', '--fileb', type=argparse.FileType('rb'), help='Optional input file. If it is provided he compounds in this file will be compared to the compounds in the first input file.')
    parser.add_argument('-f', '--format', action='store', dest='format', choices=['smi', 'sdf'], default='smi', help='Specify the input format (smiles strings (default) or SD file).')
    parser.add_argument('-s', '--sim', action='store', choices=['min', 'max', 'all'], default='max', help='Get only the closest compounds (\'max\', default), the most dissimilar (\'min\'), or all v all similarties (\'all\')')
    parser.add_argument('-c', '--cutoff', type=float, help='If wanted, set a minimum similarity cutoff.')
    parser.add_argument('-i', '--id', type=str, help='Field containing the molecule ID. If it is not provided for the SD file format, the SD file compound name will be used.')
    parser.add_argument('-x', '--col', type=int, default=1, help='If the input file has smiles, indicate which column contains the smiles strings.')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Smiles input data file doesn\'t have a header line.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w+'), default='output.txt', help='Output file name (default: output.txt)')
    args = parser.parse_args()

    if args.col is not None:
        args.col -= 1
    args.id = int(args.id)-1

    #if args.format == 'smi' and args.id is not None:
        #try:
        #    args.id = int(args.id)-1
        #except:
        #    sys.stderr('The ID argument must be a column index if the input file is of smiles format.\n')
        #    sys.exit()

    compare(args)    

if __name__ == '__main__':    
    main()