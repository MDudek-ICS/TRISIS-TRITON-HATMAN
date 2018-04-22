# Triton-Symbolic
## Symbolic Execution of Triton Malware in ANGR
Script for running imain.bin with ANGR symbolic execution engine

All credits to [@bl4ckic3](https://twitter.com/bl4ckic3)

![Triton in ANGR](./angr.png).

## Files Description
* *imain.py* - python script that runs imain.bin in ANGR
* *TritonCFG.dot* - Control-Flow Graph (obtained as a result of running the imain.py script)

## Requirements
<TODO>

## Manual
* Before running script unpack imain.7z in *original_samples* folder
* In case you need Control-Flow Graph you also need to change the graph output path in the *imain.py* file.

## Futher development
I will eventually link some I/O interfaces to the machine running ANGR and use the Triton to do various manipulation for demonstration of its capabilities. 
