#! /usr/bin/perl -w
use File::Path;
use strict;
use Getopt::Long;
use Cwd;

my $CMSSW1 = "CMSSW_12_4_14_patch2";
my $CMSSW2 = "CMSSW_12_4_14_patch3";
my $CMSSW3 = "CMSSW_13_0_13";

my $NumberofJobs;       # -j --> Number of jobs to submit (Must be >= 1)
my $NumberofEvents;     # -n --> Total number of events
my $DecayMode;          # --dec --> Decay Mode
my $mass;		# --m --> TCP mass
my $htbin;		# --ht --> ht bin
my $Fragment;           # --frg --> The name of the fragment
my $GridPack;           # --gp -->  The name of the pre-generated GridPack (Tarball)

GetOptions('j=i'=>\$NumberofJobs, 'n=i'=>\$NumberofEvents, 'dec=s'=>\$DecayMode, 'm=i'=>\$mass, 'ht=s'=>\$htbin, 'frg=s'=>\$Fragment, 'gp=s'=>\$GridPack);

print("Number of Jobs: ${NumberofJobs}\n");
print("Total Number of Events: ${NumberofEvents} Events\n");
print("Decay Mode: ${DecayMode}\n");
print("Configuration Fragment: ${Fragment}\n");
print("GridPack: ${GridPack}\n");
print("\n");

my $NEpJ       = $NumberofEvents/$NumberofJobs;
my $Name       = "M-${DecayMode}_m${mass}_htj${htbin}_${NumberofEvents}Events";
my $UserName   = getlogin || getpwuid($<);
my $Top_Dir    = Cwd::cwd();
my $CMS_Dir1   = "${Top_Dir}/${Name}/${CMSSW1}";
my $CMS_Dir2   = "${Top_Dir}/${Name}/${CMSSW2}";
my $CMS_Dir3   = "${Top_Dir}/${Name}/${CMSSW3}";
my $CGP        = "${CMS_Dir1}/src/Configuration/GenProduction/python";
my $Log_Dir    = "${Top_Dir}/${Name}/LogFiles";
my $Logs       = "${Log_Dir}/Logs";
my $Errors     = "${Log_Dir}/Errors";
my $Outs       = "${Log_Dir}/Outs";
my $MyPublic   = "/ospool/cms-user/danish.alam/public/${Name}";

# Create needed directories
if (!-e "${Name}") {
  mkpath("${Name}", 0, 0755) || die "Cannot mkpath ${Name}: $! \n";
}
if (!-e "${CMS_Dir1}") {
  system("cd ${Name}; source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el8_amd64_gcc10; scram project CMSSW ${CMSSW1}");
}
if (!-e "${CMS_Dir2}") {
  system("cd ${Name}; source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el8_amd64_gcc10; scram project CMSSW ${CMSSW2}");
}
if (!-e "${CMS_Dir3}") {
  system("cd ${Name}; source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el8_amd64_gcc11; scram project CMSSW ${CMSSW3}");
}
if (!-e "${CGP}") {
  mkpath("${CGP}", 0, 0755) || die "Cannot mkpath ${CGP}: $! \n";
}
if (!-e "${Log_Dir}") {
  mkpath("${Log_Dir}", 0, 0755) || die "Cannot mkpath ${Log_Dir}: $! \n";
}
if (!-e "${Logs}") {
  mkpath("${Logs}", 0, 0755) || die "Cannot mkpath ${Logs}: $! \n";
}
if (!-e "${Errors}") {
  mkpath("${Errors}", 0, 0755) || die "Cannot mkpath ${Errors}: $! \n";
}
if (!-e "${Outs}") {
  mkpath("${Outs}", 0, 0755) || die "Cannot mkpath ${Outs}: $! \n";
}
if (!-e "${MyPublic}") {
  mkpath("${MyPublic}", 0, 0755) || die "Cannot mkpath ${MyPublic}: $! \n";
}

# Check that needed subdirectories exist
if ((!-e "${Name}") || (!-e "${CMS_Dir1}") || (!-e "${CMS_Dir2}") || (!-e "${CMS_Dir3}") || (!-e "${CGP}") || (!-e "${Log_Dir}") || (!-e "${Logs}") || (!-e "${Errors}") || (!-e "${Outs}") || (!-e "${MyPublic}")) {
  die "Some directory is missing \n";
}

system("\\cp ${Fragment} ${CGP}");
system("cd ${CMS_Dir1}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; scram b");
system("\\cp ${Top_Dir}/GridPacks/${GridPack} ${CMS_Dir1}/src/");

my $ConfigFile1 = "${Name}_Step1_cfg.py";
my $ConfigFile2 = "${Name}_Step2_cfg.py";
my $ConfigFile3 = "${Name}_Step3_cfg.py";
my $ConfigFile4 = "${Name}_Step4_cfg.py";
my $ConfigFile5 = "${Name}_Step5_cfg.py";

my $PileUpInput = "PileupFiles";

# Creating cmsRun Configuration Files (Locally)
system("cd ${CMS_Dir1}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; cmsDriver.py Configuration/GenProduction/python/${Fragment} step1 --fileout file:Output1 --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 124X_mcRun3_2022_realistic_v12 --beamspot Realistic25ns13p6TeVEarly2022Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Extended --era Run3 --python_filename ${ConfigFile1} --no_exec  --customise Configuration/DataProcessing/Utils.addMonitoring -n ${NEpJ}");
system("cd ${CMS_Dir2}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; cmsDriver.py step2 --filein file:Output1 --fileout file:Output2 --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 124X_mcRun3_2022_realistic_v12 --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v12 --procModifiers premix_stage2,siPixelQualityRawToDigi --nThreads 8 --geometry DB:Extended --pileup_input ${PileUpInput} --datamix PreMix --era Run3 --python_filename ${ConfigFile2} --no_exec  --customise Configuration/DataProcessing/Utils.addMonitoring -n -1");
system("cd ${CMS_Dir2}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; cmsDriver.py step3 --filein file:Output2 --fileout file:Output3 --mc --eventcontent AODSIM --datatier AODSIM --conditions 124X_mcRun3_2022_realistic_v12 --step RAW2DIGI,L1Reco,RECO,RECOSIM --procModifiers siPixelQualityRawToDigi --nThreads 8 --geometry DB:Extended --era Run3 --python_filename ${ConfigFile3} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1");
system("cd ${CMS_Dir3}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; cmsDriver.py step4 --filein file:Output3 --fileout file:Output4 --mc --eventcontent MINIAODSIM --datatier MINIAODSIM --conditions 130X_mcRun3_2022_realistic_v5 --step PAT --nThreads 8 --geometry DB:Extended --era Run3 --python_filename ${ConfigFile4} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1");
system("cd ${CMS_Dir3}/src; source /cvmfs/cms.cern.ch/cmsset_default.sh; eval `scram runtime -sh`; cmsDriver.py step5 --filein file:Output4 --fileout file:Output5  --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 130X_mcRun3_2022_realistic_v5 --step NANO --scenario pp --era Run3 --nThreads 8 --python_filename ${ConfigFile5} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1");

# Modifying the cmsRun configuration file for Step 1
open(INCFG1, "${CMS_Dir1}/src/${ConfigFile1}") or die "Cannot open file ${CMS_Dir1}/src/${ConfigFile1}\n";
open(TMPOUT1, "> /tmp/${ConfigFile1}.tmp") or die "Cannot open file /tmp/${ConfigFile1}.tmp\n";
while (my $inputline1=<INCFG1>) {
  chomp($inputline1);
  if ($inputline1 =~ /# Output definition/) {
    print TMPOUT1 "# This populates the random seeds differently each time\n";
    print TMPOUT1 "from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper\n";
    print TMPOUT1 "randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)\n";
    print TMPOUT1 "randSvc.populate()\n";
    print TMPOUT1 "\n";
    print TMPOUT1 "# Getting the path to the current directory in order to add it to the GridPack name later\n";    # <---<< Use with 1
    print TMPOUT1 "import os\n";
    print TMPOUT1 "cwd = os.getcwd()\n";
    print TMPOUT1 "GPACK = cwd+'/${GridPack}'\n";
    print TMPOUT1 "\n";
  }
  if ($inputline1 =~ /args = cms\.vstring\('GridPack'\),/) {
    $inputline1   =~ s/'GridPack'/GPACK/;
  }
  print TMPOUT1 "$inputline1\n";
}
close(INCFG1);
close(TMPOUT1);
system("mv -f /tmp/${ConfigFile1}.tmp ${CMS_Dir1}/src/${ConfigFile1}");

# Modifying the cmsRun configuration file for Step 2 (Getting Pileup files)
open(INCFG2, "${CMS_Dir2}/src/${ConfigFile2}") or die "Cannot open file ${CMS_Dir2}/src/${ConfigFile2}\n";
open(TMPOUT2, "> /tmp/${ConfigFile2}.tmp") or die "Cannot open file /tmp/${ConfigFile2}.tmp\n";
while (my $inputline2=<INCFG2>) {
	chomp($inputline2);
	if ($inputline2 =~ /process\.mixData\.input\.fileNames = cms\.untracked\.vstring\(\['PileupFiles'\]\)/) {
		print TMPOUT2 "import subprocess\n";
		print TMPOUT2 "PileupFiles = subprocess.check_output([\n";
		print TMPOUT2 "\t'dasgoclient',\n";
		print TMPOUT2 "\t'-query=file dataset=/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX site=T2_CH_CERN'\n";
		print TMPOUT2 "], universal_newlines=True).splitlines()\n";
		print TMPOUT2 "process.mixData.input.fileNames = cms.untracked.vstring(PileupFiles)\n";
		print TMPOUT2 "\n";
	}
	else {
		print TMPOUT2 "$inputline2\n";
	}
}
close(INCFG2);
close(TMPOUT2);
system("mv -f /tmp/${ConfigFile2}.tmp ${CMS_Dir2}/src/${ConfigFile2}");

my $MyJob      = "${Name}.sh";
my $MyHTCondor = "${Name}.jdl";

# Creating the run script (Bash)
open BASH,">${Top_Dir}/${Name}/${MyJob}" or die "Cannot open file ${Top_Dir}/${Name}/${MyJob}\n";
print BASH "#! /bin/bash\n";
print BASH "date\n";
print BASH "source /cvmfs/cms.cern.ch/cmsset_default.sh\n";
print BASH "export SCRAM_ARCH=el8_amd64_gcc10\n";
print BASH "scram project CMSSW ${CMSSW1}\n";
print BASH "scram project CMSSW ${CMSSW2}\n";
print BASH "export SCRAM_ARCH=el8_amd64_gcc11\n";
print BASH "scram project CMSSW ${CMSSW3}\n";
print BASH "cd ${CMSSW1}/src\n";
print BASH "export SCRAM_ARCH=el8_amd64_gcc10\n";
print BASH "eval `scram runtime -sh`\n";
print BASH "mv ../../${ConfigFile1} ./\n";
print BASH "mv ../../${GridPack} ./\n";
print BASH "time cmsRun ${ConfigFile1}\n";
print BASH "mv Output1 ../../${CMSSW2}/src\n";
print BASH "cd ../../${CMSSW2}/src\n";
print BASH "export SCRAM_ARCH=el8_amd64_gcc10\n";
print BASH "eval `scram runtime -sh`\n";
print BASH "mv ../../${ConfigFile2} ./\n";
print BASH "mv ../../${ConfigFile3} ./\n";
print BASH "time cmsRun ${ConfigFile2}\n";
print BASH "rm -rf Output1\n";
print BASH "time cmsRun ${ConfigFile3}\n";
print BASH "rm -rf Output2\n";
print BASH "mv Output3 ../../${CMSSW3}/src\n";
print BASH "cd ../../${CMSSW3}/src\n";
print BASH "export SCRAM_ARCH=el8_amd64_gcc11\n";
print BASH "eval `scram runtime -sh`\n";
print BASH "mv ../../${ConfigFile4} ./\n";
print BASH "mv ../../${ConfigFile5} ./\n";
print BASH "time cmsRun ${ConfigFile4}\n";
print BASH "rm -rf Output3\n";
print BASH "time cmsRun ${ConfigFile5}\n";
print BASH "mv Output4 ../../\n";
print BASH "mv Output5 ../../\n";
print BASH "date\n";
close BASH;

# Creating HTCondor submission file
open CONDOR,">${Top_Dir}/${Name}/${MyHTCondor}" or die "Cannot open file ${Top_Dir}/${Name}/${MyHTCondor}\n";
print CONDOR "Universe = vanilla\n";
print CONDOR "Executable = ${Name}.sh\n";
print CONDOR "use_x509userproxy = TRUE\n";
print CONDOR "x509userproxy = /tmp/x509up_u11467\n";
print CONDOR "+SingularityImage = \"/cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/el8:x86_64\"\n";
print CONDOR "Requirements = HasSingularity\n";
print CONDOR "Log = ${Log_Dir}/Logs/\$(Cluster)_\$(Process).log\n";
print CONDOR "Error = ${Log_Dir}/Errors/\$(Cluster)_\$(Process).err\n";
print CONDOR "Output = ${Log_Dir}/Outs/\$(Cluster)_\$(Process).out\n";
print CONDOR "should_transfer_files = YES\n";
print CONDOR "when_to_transfer_output = ON_EXIT_OR_EVICT\n";
print CONDOR "transfer_input_files = ${CMS_Dir1}/src/${ConfigFile1},${CMS_Dir2}/src/${ConfigFile2},${CMS_Dir2}/src/${ConfigFile3},${CMS_Dir3}/src/${ConfigFile4},${CMS_Dir3}/src/${ConfigFile5},${CMS_Dir1}/src/${GridPack}\n";
print CONDOR "transfer_output_files = Output4,Output5\n";
print CONDOR "transfer_output_remaps = \"Output4 = ${MyPublic}/${Name}_MiniAOD_\$(Cluster)_\$(Process).root; Output5 = ${MyPublic}/${Name}_NanoAOD_\$(Cluster)_\$(Process).root\"\n";
print CONDOR "request_cpus = 8\n";
print CONDOR "Queue ${NumberofJobs}\n";
close CONDOR;

# Submitting the jobs
system("chmod +x ${Top_Dir}/${Name}/${MyHTCondor}");
#system("cd ${CMS_Dir1}/src; condor_submit ${MyHTCondor}");    // <---<< Need to be executed manually outside Singularity

# MC Generation Using Pythia8 and MadGraph (GridPack) on CMSConnect
###########################################################################################################################################################
# How to run this code (Need to be run inside Singularity):
#
#  e.g.  perl MCGeneration_CMSConnect_ParkingBPH_UL2018_MiniAOD_GridPack.pl -j 10 -n 50000 --dec Ztollbb --m 25 --ht 100to400 --frg Ztollbb_Hadronizer_GridPack.py --gp PPtoZtolltoZtobb.tar.xz
#
#     -j          Number of jobs (must be always >= 1)
#     -n          Total number of events
#     --dec       Decay Mode
#     --frg       Fragment
#     --gp        GridPack Tar Ball --> Note: GridPack must be stored in a sub-directory called "GridPacks" in the current directory.
#                                             Use ONLY the name of the file not the path to the file.
#
#**********************************************************************************************************************************************************
# In order to check the status of the submitted jobs on the network use:
#   condor_q <UserName>
#     e.g.
#       condor_q abbashassani
# 
# In order to delete a submitted job on the network use:
#   condor_rm <job-ID>
#
# For all the submitted jobs:
#   condor_rm <UserName>
#     e.g.
#       condor_rm abbashassani 
#**********************************************************************************************************************************************************
