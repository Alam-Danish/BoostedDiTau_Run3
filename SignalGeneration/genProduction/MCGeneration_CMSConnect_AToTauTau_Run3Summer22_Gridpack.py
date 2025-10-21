#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import getpass
import shutil
from pathlib import Path
import re

def main():
    # CMSSW versions
    CMSSW1 = "CMSSW_12_4_14_patch3"
    CMSSW2 = "CMSSW_13_0_13"
    
    # Command line argument parsing
    parser = argparse.ArgumentParser(description='MC Generation Using Pythia8 and MadGraph (GridPack) on CMSConnect')
    parser.add_argument('-j', '--jobs', type=int, required=True, help='Number of jobs to submit (Must be >= 1)')
    parser.add_argument('-n', '--events', type=int, required=True, help='Total number of events')
    parser.add_argument('--dec', dest='decay', required=True, help='Decay Mode')
    parser.add_argument('--frg', dest='fragment', required=True, help='The name of the fragment')
    parser.add_argument('--gp', dest='gridpack', required=True, help='The name of the pre-generated GridPack (Tarball)')
    parser.add_argument('--year', required=True, help='Year for the analysis (e.g., Run3Summer22, Run3Summer22EE)')
    
    args = parser.parse_args()
    
    NumberofJobs = args.jobs
    NumberofEvents = args.events
    DecayMode = args.decay
    Fragment = args.fragment
    GridPack = args.gridpack
    Year = args.year
    
    print(f"Number of Jobs: {NumberofJobs}")
    print(f"Total Number of Events: {NumberofEvents} Events")
    print(f"Decay Mode: {DecayMode}")
    print(f"Configuration Fragment: {Fragment}")
    print(f"GridPack: {GridPack}")
    print(f"Year: {Year}")
    print()
    
    # Calculate events per job
    NEpJ = NumberofEvents // NumberofJobs
    
    # Extract mass and HT bin from gridpack filename
    # Expected format: TCP_m{mass}_ht_{htbin}_...
    gridpack_pattern = r'TCP_m(\d+)_ht_(\d+to\d+|400toInf)'
    match = re.search(gridpack_pattern, GridPack)
    if match:
        mass = match.group(1)
        ht_bin = match.group(2)
        Name = f"ALP_M-{mass}_HT-{ht_bin}_{Year}"
    else:
        # Fallback to original naming if pattern doesn't match
        Name = f"M-{DecayMode}_{NumberofEvents}Events"
        print(f"Warning: Could not parse gridpack name '{GridPack}', using fallback naming")
    UserName = getpass.getuser()
    Top_Dir = os.getcwd()
    
    # Directory paths
    CMS_Dir1 = f"{Top_Dir}/{Name}/{CMSSW1}"
    CMS_Dir2 = f"{Top_Dir}/{Name}/{CMSSW2}"
    CGP = f"{CMS_Dir1}/src/Configuration/GenProduction/python"
    Log_Dir = f"{Top_Dir}/{Name}/LogFiles"
    Logs = f"{Log_Dir}/Logs"
    Errors = f"{Log_Dir}/Errors"
    Outs = f"{Log_Dir}/Outs"
    MyPublic = f"/ospool/cms-user/danish.alam/public/{Name}"
    
    # Create needed directories
    directories = [Name, CMS_Dir1, CMS_Dir2, CGP, Log_Dir, Logs, Errors, Outs, MyPublic]
    
    for directory in directories:
        if not os.path.exists(directory):
            if directory in [CMS_Dir1, CMS_Dir2]:  # Updated to only include CMS_Dir1 and CMS_Dir2
                # Create CMSSW projects
                create_cmssw_project(directory, Name, CMSSW1 if directory == CMS_Dir1 else CMSSW2)
            else:
                os.makedirs(directory, mode=0o755)
    
    # Check that needed subdirectories exist
    for directory in directories:
        if not os.path.exists(directory):
            raise SystemExit(f"Directory {directory} is missing")
    
    # Copy fragment and build
    subprocess.run(f"cp {Fragment} {CGP}", shell=True, check=True)
    subprocess.run(f"cd {CMS_Dir1}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && scram b", 
                   shell=True, check=True)
    subprocess.run(f"cp {Top_Dir}/GridPacks/{GridPack} {CMS_Dir1}/src/", shell=True, check=True)
    
    # Configuration file names
    ConfigFile1 = f"{Name}_Step1_cfg.py"
    ConfigFile2 = f"{Name}_Step2_cfg.py"
    ConfigFile3 = f"{Name}_Step3_cfg.py"
    ConfigFile4 = f"{Name}_Step4_cfg.py"
    ConfigFile5 = f"{Name}_Step5_cfg.py"
    
    PileUpInput = "PileupFiles"
    
    # Create cmsRun Configuration Files
    create_cms_configs(CMS_Dir1, CMS_Dir2, Fragment, ConfigFile1, ConfigFile2, 
                      ConfigFile3, ConfigFile4, ConfigFile5, NEpJ, PileUpInput)
    
    # Modify configuration files
    modify_config_file_step1(CMS_Dir1, ConfigFile1, GridPack)
    modify_config_file_step2(CMS_Dir1, ConfigFile2)
    
    # Create job scripts
    MyJob = f"{Name}.sh"
    MyHTCondor = f"{Name}.jdl"
    
    create_bash_script(Top_Dir, Name, MyJob, CMSSW1, CMSSW2, ConfigFile1, ConfigFile2, 
                      ConfigFile3, ConfigFile4, ConfigFile5, GridPack)
    create_htcondor_script(Top_Dir, Name, MyHTCondor, Log_Dir, CMS_Dir1, CMS_Dir2, 
                          ConfigFile1, ConfigFile2, ConfigFile3, ConfigFile4, ConfigFile5, 
                          GridPack, MyPublic, NumberofJobs)
    
    # Make executable
    os.chmod(f"{Top_Dir}/{Name}/{MyHTCondor}", 0o755)
    
    print(f"Job files created successfully!")
    print(f"To submit jobs, run: cd {CMS_Dir1}/src && condor_submit {MyHTCondor}")


def create_cmssw_project(cms_dir, name, cmssw_version):
    """Create CMSSW project directory"""
    arch = "el8_amd64_gcc10" if cmssw_version != "CMSSW_13_0_13" else "el8_amd64_gcc11"
    cmd = f"cd {name} && source /cvmfs/cms.cern.ch/cmsset_default.sh && export SCRAM_ARCH={arch} && scram project CMSSW {cmssw_version}"
    subprocess.run(cmd, shell=True, check=True)


def create_cms_configs(cms_dir1, cms_dir2, fragment, config1, config2, config3, config4, config5, nepj, pileup_input):
    """Create cmsDriver configuration files"""
    
    # Step 1
    cmd1 = f"""cd {cms_dir1}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && \
cmsDriver.py Configuration/GenProduction/python/{fragment} step1 --fileout file:Output1.root --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 124X_mcRun3_2022_realistic_v12 --beamspot Realistic25ns13p6TeVEarly2022Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Extended --era Run3 --python_filename {config1} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n {nepj}"""
    
    # Step 2
    cmd2 = f"""cd {cms_dir1}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && \
cmsDriver.py step2 --filein file:Output1.root --fileout file:Output2.root --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 124X_mcRun3_2022_realistic_v12 --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v12 --procModifiers premix_stage2,siPixelQualityRawToDigi --nThreads 4 --geometry DB:Extended --pileup_input {pileup_input} --datamix PreMix --era Run3 --python_filename {config2} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1"""
    
    # Step 3
    cmd3 = f"""cd {cms_dir1}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && \
cmsDriver.py step3 --filein file:Output2.root --fileout file:Output3.root --mc --eventcontent AODSIM --datatier AODSIM --conditions 124X_mcRun3_2022_realistic_v12 --step RAW2DIGI,L1Reco,RECO,RECOSIM --procModifiers siPixelQualityRawToDigi --nThreads 4 --geometry DB:Extended --era Run3 --python_filename {config3} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1"""
    
    # Step 4
    cmd4 = f"""cd {cms_dir2}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && \
cmsDriver.py step4 --filein file:Output3.root --fileout file:Output4.root --mc --eventcontent MINIAODSIM --datatier MINIAODSIM --conditions 130X_mcRun3_2022_realistic_v5 --step PAT --nThreads 2 --geometry DB:Extended --era Run3,run3_miniAOD_12X --python_filename {config4} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1"""
    
    # Step 5
    cmd5 = f"""cd {cms_dir2}/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && eval `scram runtime -sh` && \
cmsDriver.py step5 --filein file:Output4 --fileout file:Output5 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 130X_mcRun3_2022_realistic_v5 --step NANO --scenario pp --era Run3 --nThreads 4 --python_filename {config5} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1"""
    
    for cmd in [cmd1, cmd2, cmd3, cmd4, cmd5]:
        subprocess.run(cmd, shell=True, check=True)


def modify_config_file_step1(cms_dir1, config_file1, gridpack):
    """Modify the cmsRun configuration file for Step 1"""
    input_file = f"{cms_dir1}/src/{config_file1}"
    temp_file = f"/tmp/{config_file1}.tmp"
    
    with open(input_file, 'r') as infile, open(temp_file, 'w') as outfile:
        for line in infile:
            line = line.rstrip()
            if "# Output definition" in line:
                outfile.write("# This populates the random seeds differently each time\n")
                outfile.write("from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper\n")
                outfile.write("randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)\n")
                outfile.write("randSvc.populate()\n")
                outfile.write("\n")
                outfile.write("# Getting the path to the current directory in order to add it to the GridPack name later\n")
                outfile.write("import os\n")
                outfile.write("cwd = os.getcwd()\n")
                outfile.write(f"GPACK = cwd+'/{gridpack}'\n")
                outfile.write("\n")
            
            if "args = cms.vstring('GridPack')," in line:
                line = line.replace("'GridPack'", "GPACK")
            
            outfile.write(line + "\n")
    
    shutil.move(temp_file, input_file)


def modify_config_file_step2(cms_dir, config_file2):
    """Modify the cmsRun configuration file for Step 2 (Getting Pileup files)"""
    input_file = f"{cms_dir}/src/{config_file2}"
    temp_file = f"/tmp/{config_file2}.tmp"
    
    with open(input_file, 'r') as infile, open(temp_file, 'w') as outfile:
        for line in infile:
            line = line.rstrip()
            if "process.mixData.input.fileNames = cms.untracked.vstring(['PileupFiles'])" in line:
                outfile.write("import subprocess\n")
                outfile.write("PileupFiles = subprocess.check_output([\n")
                outfile.write("\t'dasgoclient',\n")
                outfile.write("\t'-query=file dataset=/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX site=T2_CH_CERN'\n")
                outfile.write("], universal_newlines=True).splitlines()\n")
                outfile.write("process.mixData.input.fileNames = cms.untracked.vstring(PileupFiles)\n")
                outfile.write("\n")
            else:
                outfile.write(line + "\n")
    
    shutil.move(temp_file, input_file)


def create_bash_script(top_dir, name, job_file, cmssw1, cmssw2, config1, config2, config3, config4, config5, gridpack):
    """Create the bash script for job execution"""
    script_path = f"{top_dir}/{name}/{job_file}"
    
    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("date\n")
        f.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
        f.write("export SCRAM_ARCH=el8_amd64_gcc10\n")
        f.write(f"scram project CMSSW {cmssw1}\n")
        f.write("export SCRAM_ARCH=el8_amd64_gcc11\n")
        f.write(f"scram project CMSSW {cmssw2}\n")
        f.write(f"cd {cmssw1}/src\n")
        f.write("export SCRAM_ARCH=el8_amd64_gcc10\n")
        f.write("eval `scram runtime -sh`\n")
        f.write(f"mv ../../{config1} ./\n")
        f.write(f"mv ../../{gridpack} ./\n")
        f.write(f"mv ../../{config2} ./\n")
        f.write(f"mv ../../{config3} ./\n")
        f.write(f"time cmsRun {config1}\n")
        f.write(f"time cmsRun {config2}\n")
        f.write("rm -rf Output1.root\n")
        f.write(f"time cmsRun {config3}\n")
        f.write("rm -rf Output2.root\n")
        f.write(f"mv Output3.root ../../{cmssw2}/src\n")
        f.write(f"cd ../../{cmssw2}/src\n")
        f.write("export SCRAM_ARCH=el8_amd64_gcc11\n")
        f.write("eval `scram runtime -sh`\n")
        f.write(f"mv ../../{config4} ./\n")
        f.write(f"mv ../../{config5} ./\n")
        f.write(f"time cmsRun {config4}\n")
        f.write("rm -rf Output3.root\n")
        f.write(f"time cmsRun {config5}\n")
        f.write("mv Output4.root ../../\n")
        f.write("mv Output5.root ../../\n")
        f.write("date\n")


def create_htcondor_script(top_dir, name, condor_file, log_dir, cms_dir1, cms_dir2, 
                          config1, config2, config3, config4, config5, gridpack, my_public, num_jobs):
    """Create HTCondor submission file"""
    script_path = f"{top_dir}/{name}/{condor_file}"
    
    with open(script_path, 'w') as f:
        f.write("Universe = vanilla\n")
        f.write(f"Executable = {name}.sh\n")
        f.write("use_x509userproxy = TRUE\n")
        f.write("x509userproxy = /tmp/x509up_u11467\n")
        f.write('+SingularityImage = "/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/el8:x86_64"\n')
        f.write("Requirements = HasSingularity\n")
        f.write(f"Log = {log_dir}/Logs/$(Cluster)_$(Process).log\n")
        f.write(f"Error = {log_dir}/Errors/$(Cluster)_$(Process).err\n")
        f.write(f"Output = {log_dir}/Outs/$(Cluster)_$(Process).out\n")
        f.write("should_transfer_files = YES\n")
        f.write("when_to_transfer_output = ON_EXIT_OR_EVICT\n")
        f.write(f"transfer_input_files = {cms_dir1}/src/{config1},{cms_dir1}/src/{config2},{cms_dir1}/src/{config3},{cms_dir2}/src/{config4},{cms_dir2}/src/{config5},{cms_dir1}/src/{gridpack}\n")
        f.write("transfer_output_files = Output4.root,Output5.root\n")
        f.write(f'transfer_output_remaps = "Output4.root = {my_public}/{name}_MiniAOD_$(Process).root; Output5.root = {my_public}/{name}_NanoAOD_$(Process).root"\n')
        f.write("request_cpus = 8\n")
        f.write(f"Queue {num_jobs}\n")


if __name__ == "__main__":
    main()

# MC Generation Using Pythia8 and MadGraph (GridPack) on CMSConnect
###########################################################################################################################################################
# How to run this code (Need to be run inside Singularity):
#
#  e.g.  python3 MCGeneration_CMSConnect_AToTauTau_Run3Summer22_Gridpack.py -j 10 -n 50000 --dec Ztollbb --frg Ztollbb_Hadronizer_GridPack.py --gp TCP_m10_ht_100to400_el8_amd64_gcc10_CMSSW_12_4_14_patch3_tarball.tar.xz --year postVFPUL16
#
#     -j, --jobs      Number of jobs (must be always >= 1)
#     -n, --events    Total number of events
#     --dec, --decay  Decay Mode
#     --frg, --fragment    Fragment
#     --gp, --gridpack     GridPack Tar Ball --> Note: GridPack must be stored in a sub-directory called "GridPacks" in the current directory.
#                                                      Use ONLY the name of the file not the path to the file.
#     --year               Year for the analysis (e.g., postVFPUL16, postVFPUL17, postVFPUL18)
#
#**********************************************************************************************************************************************************
# In order to check the status of the submitted jobs on the network use:
#   condor_q <UserName>
#     e.g.
#       condor_q danish.alam
# 
# In order to delete a submitted job on the network use:
#   condor_rm <job-ID>
#
# For all the submitted jobs:
#   condor_rm <UserName>
#     e.g.
#       condor_rm danish.alam 
#**********************************************************************************************************************************************************
