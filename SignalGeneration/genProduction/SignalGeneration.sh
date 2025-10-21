#!/bin/bash

# Configuration
#RUNHOME=/path/to/MG5_aMC/  # <-- change to your MG5/gridpack run directory
QUEUE=local                  # batch queue (e.g., 8nh, 1nd, or local)
JOBSTEP=ALL                  # number of job steps (default: ALL)
SCRAM_ARCH=el8_amd64_gcc10
CMSSW_VERSION=CMSSW_12_4_14_patch3  # Run3 baseline CMSSW version

MASSES=$(seq 10 5 65)
HTBINS=("100to400" "400toInf")

for M in $MASSES; do
  for HT in "${HTBINS[@]}"; do
    
    # Unique name for the gridpack
    NAME="TCP_m${M}_ht_${HT}"
    
    # Path to the card directory you generated earlier
    CARDDIR="cards/ALP_cards/TCP_m${M}/${NAME}"
    RUNHOME="Run3Summer22EE/TCP_m${M}/"
    
    # Make sure the directory exists
    if [ ! -d "${CARDDIR}" ]; then
      echo "Card directory ${CARDDIR} not found, skipping..."
      continue
    fi
    
    echo ">>> Starting gridpack for ${NAME}"
    
    ./gridpack_generation.sh ${NAME} ${CARDDIR} ${RUNHOME} ${QUEUE} ${JOBSTEP} ${SCRAM_ARCH} ${CMSSW_VERSION}
    
    echo ">>> Finished gridpack for ${NAME}"
    echo
  done
done

