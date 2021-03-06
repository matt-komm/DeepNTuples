import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing
### parsing job options 
import sys
import os

options = VarParsing.VarParsing()

options.register('inputScript','',VarParsing.VarParsing.multiplicity.singleton,VarParsing.VarParsing.varType.string,"input Script")
options.register('percentage','1.0',VarParsing.VarParsing.multiplicity.singleton,VarParsing.VarParsing.varType.float,"percentage")
options.register('outputFile','output',VarParsing.VarParsing.multiplicity.singleton,VarParsing.VarParsing.varType.string,"output File (w/o .root)")
options.register('maxEvents',-1,VarParsing.VarParsing.multiplicity.singleton,VarParsing.VarParsing.varType.int,"maximum events")
options.register('skipEvents', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "skip N events")
options.register('job', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "job number")
options.register('nJobs', 1, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "total jobs")
options.register('release','8_0_25', VarParsing.VarParsing.multiplicity.singleton,VarParsing.VarParsing.varType.string,"release number (w/o CMSSW)")

cmsswversion = os.environ["CMSSW_VERSION"].split("_")


print("Using release "+str(cmsswversion))


if hasattr(sys, "argv"):
    options.parseArguments()




process = cms.Process("DNNFiller")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.EventContent.EventContent_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.options = cms.untracked.PSet(
   allowUnscheduled = cms.untracked.bool(True),  
   wantSummary=cms.untracked.bool(False)
)

from PhysicsTools.PatAlgos.patInputFiles_cff import filesRelValTTbarPileUpMINIAODSIM
#660673,
process.source = cms.Source('PoolSource',
                      	    fileNames=cms.untracked.vstring ('root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/SMS-T1qqqq_ctau-0p01_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_GridpackScan_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v2/110000/0C07E448-338A-E711-B877-0CC47A4D75F2.root'),
                            #skipEvents=cms.untracked.uint32(25585)
)

if options.inputScript != '' and options.inputScript != 'DeepNTuples.DeepNtuplizer.samples.TEST':
    process.load(options.inputScript)

numberOfFiles = len(process.source.fileNames)
numberOfJobs = options.nJobs
jobNumber = options.job


process.source.fileNames = process.source.fileNames[jobNumber:numberOfFiles:numberOfJobs]
if options.nJobs > 1:
    print ("running over these files:")
    print (process.source.fileNames)
#process.source.fileNames = ['file:/uscms/home/verzetti/nobackup/CMSSW_8_0_25/src/DeepNTuples/copy_numEvent100.root']

#process.source.skipEvents = cms.untracked.uint32(options.skipEvents)
process.maxEvents  = cms.untracked.PSet( 
    input = cms.untracked.int32 (options.maxEvents) 
)


if int(cmsswversion[1])>=8 and int(cmsswversion[2])>=4:
 bTagInfos = [
        'pfImpactParameterTagInfos',
        'pfInclusiveSecondaryVertexFinderTagInfos',
        'pfDeepCSVTagInfos',
 ]
else :
 bTagInfos = [
        'pfImpactParameterTagInfos',
        'pfInclusiveSecondaryVertexFinderTagInfos',
        'deepNNTagInfos',
 ]


if int(cmsswversion[1])>=8 and int(cmsswversion[2])>=4:
 bTagDiscriminators = [
     #'softPFMuonBJetTags',
     #'softPFElectronBJetTags',
     #'pfJetBProbabilityBJetTags',
     #'pfJetProbabilityBJetTags',
     'pfCombinedInclusiveSecondaryVertexV2BJetTags',
     'pfDeepCSVJetTags:probudsg', #to be fixed with new names
     'pfDeepCSVJetTags:probb',
     'pfDeepCSVJetTags:probc',
     'pfDeepCSVJetTags:probbb',
     #'pfDeepCSVJetTags:probcc',
 ]
else :
 bTagDiscriminators = [
     #'softPFMuonBJetTags',
     #'softPFElectronBJetTags',
     #'pfJetBProbabilityBJetTags',
     #'pfJetProbabilityBJetTags',
     'pfCombinedInclusiveSecondaryVertexV2BJetTags',
     'deepFlavourJetTags:probudsg', #to be fixed with new names
     'deepFlavourJetTags:probb',
     'deepFlavourJetTags:probc',
     'deepFlavourJetTags:probbb',
     #'deepFlavourJetTags:probcc',
 ]

bTagDiscriminators = ['pfCombinedInclusiveSecondaryVertexV2BJetTags']

jetCorrectionsAK4 = ('AK4PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
updateJetCollection(
        process,
        labelName = "DeepFlavour",
        jetSource = cms.InputTag('slimmedJets'),#'ak4Jets'
        jetCorrections = jetCorrectionsAK4,
        pfCandidates = cms.InputTag('packedPFCandidates'),
        pvSource = cms.InputTag("offlineSlimmedPrimaryVertices"),
        svSource = cms.InputTag('slimmedSecondaryVertices'),
        muSource = cms.InputTag('slimmedMuons'),
        elSource = cms.InputTag('slimmedElectrons'),
        btagInfos = bTagInfos,
        btagDiscriminators = bTagDiscriminators,
        explicitJTA = False
)

process.eventFilter = cms.EDFilter("RandomEventFilter",
    percentage = cms.double(options.percentage)
)

process.jecSequence = cms.Sequence(process.patJetCorrFactorsDeepFlavour * process.updatedPatJetsDeepFlavour)
#process.btagSequence = cms.Sequence(process.pfImpactParameterTagInfosDeepFlavour * process.pfInclusiveSecondaryVertexFinderTagInfosDeepFlavour* process.pfDeepCSVTagInfosDeepFlavour*process.pfCombinedInclusiveSecondaryVertexV2BJetTagsDeepFlavour*process.pfDeepCSVJetTagsDeepFlavour)
process.updateSequence = cms.Sequence(process.patJetCorrFactorsTransientCorrectedDeepFlavour * process.updatedPatJetsTransientCorrectedDeepFlavour)


if hasattr(process,'updatedPatJetsTransientCorrectedDeepFlavour'):
	process.updatedPatJetsTransientCorrectedDeepFlavour.addTagInfos = cms.bool(True) 
	process.updatedPatJetsTransientCorrectedDeepFlavour.addBTagInfo = cms.bool(True)
else:
	raise ValueError('I could not find updatedPatJetsTransientCorrectedDeepFlavour to embed the tagInfos, please check the cfg')


# QGLikelihood

qgDatabaseVersion = 'cmssw8020_v2'

from CondCore.CondDB.CondDB_cfi import *
QGPoolDBESSource = cms.ESSource("PoolDBESSource",
      CondDB.DBParameters,
      toGet = cms.VPSet(),
      connect = cms.string("sqlite_file:QGL_"+qgDatabaseVersion+".db"),
)

for type in ['AK4PFchs','AK4PFchs_antib']:
  QGPoolDBESSource.toGet.extend(cms.VPSet(cms.PSet(
    record = cms.string('QGLikelihoodRcd'),
    tag    = cms.string('QGLikelihoodObject_'+qgDatabaseVersion+'_'+type),
    label  = cms.untracked.string('QGL_'+type)
)))


process.load('RecoJets.JetProducers.QGTagger_cfi')
#process.QGTagger.srcJets   = cms.InputTag("selectedUpdatedPatJetsDeepFlavour")
process.QGTagger.srcJets   = cms.InputTag("updatedPatJetsTransientCorrectedDeepFlavour")
process.QGTagger.jetsLabel = cms.string('QGL_AK4PFchs')


from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets
process.ak4GenJetsWithNu = ak4GenJets.clone(src = 'packedGenParticles')
 
 ## Filter out neutrinos from packed GenParticles
process.packedGenParticlesForJetsNoNu = cms.EDFilter("CandPtrSelector", src = cms.InputTag("packedGenParticles"), cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16"))
 ## Define GenJets
process.ak4GenJetsRecluster = ak4GenJets.clone(src = 'packedGenParticlesForJetsNoNu')
 
 
process.patGenJetMatchWithNu = cms.EDProducer("GenJetMatcher",  # cut on deltaR; pick best by deltaR           
    #src         = cms.InputTag("selectedUpdatedPatJetsDeepFlavour"),      # RECO jets (any View<Jet> is ok) 
    src         = cms.InputTag("updatedPatJetsTransientCorrectedDeepFlavour"),
    matched     = cms.InputTag("ak4GenJetsWithNu"),        # GEN jets  (must be GenJetCollection)              
    mcPdgId     = cms.vint32(),                      # n/a   
    mcStatus    = cms.vint32(),                      # n/a   
    checkCharge = cms.bool(False),                   # n/a   
    maxDeltaR   = cms.double(0.4),                   # Minimum deltaR for the match   
    #maxDPtRel   = cms.double(3.0),                  # Minimum deltaPt/Pt for the match (not used in GenJetMatcher)                     
    resolveAmbiguities    = cms.bool(True),          # Forbid two RECO objects to match to the same GEN object 
    resolveByMatchQuality = cms.bool(False),         # False = just match input in order; True = pick lowest deltaR pair first          
)

process.patGenJetMatchRecluster = cms.EDProducer("GenJetMatcher",  # cut on deltaR; pick best by deltaR           
    #src         = cms.InputTag("selectedUpdatedPatJetsDeepFlavour"),      # RECO jets (any View<Jet> is ok) 
    src         = cms.InputTag("updatedPatJetsTransientCorrectedDeepFlavour"),
    matched     = cms.InputTag("ak4GenJetsRecluster"),        # GEN jets  (must be GenJetCollection)              
    mcPdgId     = cms.vint32(),                      # n/a   
    mcStatus    = cms.vint32(),                      # n/a   
    checkCharge = cms.bool(False),                   # n/a   
    maxDeltaR   = cms.double(0.4),                   # Minimum deltaR for the match   
    #maxDPtRel   = cms.double(3.0),                  # Minimum deltaPt/Pt for the match (not used in GenJetMatcher)                     
    resolveAmbiguities    = cms.bool(True),          # Forbid two RECO objects to match to the same GEN object 
    resolveByMatchQuality = cms.bool(False),         # False = just match input in order; True = pick lowest deltaR pair first          
)

process.genJetSequence = cms.Sequence(process.packedGenParticlesForJetsNoNu*process.ak4GenJetsWithNu*process.ak4GenJetsRecluster*process.patGenJetMatchWithNu*process.patGenJetMatchRecluster)
 
process.load('XTag.DisplacedVertex.GenDisplacedVertices_cff')



process.TFileService = cms.Service("TFileService", 
                                   fileName = cms.string("deepNtuples.root"))

# DeepNtuplizer
process.load("DeepNTuples.DeepNtuplizer.DeepNtuplizer_cfi")

#process.deepntuplizer.jets = cms.InputTag('selectedUpdatedPatJetsDeepFlavour');
process.deepntuplizer.jets = cms.InputTag('updatedPatJetsTransientCorrectedDeepFlavour');
process.deepntuplizer.bDiscriminators = bTagDiscriminators 

if int(cmsswversion[1])>=8 and int(cmsswversion[2])>=4:
   process.deepntuplizer.tagInfoName = cms.string('pfDeepCSV')

process.dump=cms.EDAnalyzer('EventContentAnalyzer')

process.p = cms.Path( process.eventFilter +
                      process.jecSequence +
                      #process.btagSequence +
                      process.updateSequence +
                      process.QGTagger +
                      process.genJetSequence +
                      process.DisplacedGenVertexSequence +
                      process.deepntuplizer)
