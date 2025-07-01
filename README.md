# Alignment/Unalignment Pipeline
Align or Unalign files to a reference genome using GATK best practices.

## Overview
This pipeline is used for unaligning/aligning sequencing data. For eg. to convert hg19 aligned BAM files to hg38 (bam_hg19->FASTQ->bam_hg38). It consists of two main scripts:

* Unalignment: 00_unalign_bams_new.sh step_number
* Alignment: 00_run_align_call_filter_hg38.sh step_number
  
Both follow a stepwise approach, allowing users to run specific steps as needed. Please, setup the environment before execution.

## Unalignment
The pipeline consists of multiple steps that can be executed by specifying the number in the same script as follows:

```./00_unalign_bams_new.sh step_number stall r1 r2```

The parameters are:
- stall: seconds to wait between job submissions.

- r1: index of the first job to be submitted

- r2: index of the last job to be submitted

This allows the user to submit in batches and not all the files at the same time. For eg. first run 0-25 (r1:0, r2:25 -> processes first 25 files with 25th file not being processed in this run), second 25-50 (r1:25, r2:50 -> processes next 25 files with 50th file not being processed in this run), etc.

### Steps Description
#### Step1
Aligned BAM --> FASTQ: Unalign the bam files and create fastq files from them.

#### Step2
Fixes disordered paired reads in fastq files generated in previous step. Create a CSV file specifying the fastq files to be fixed. Sample CSV file (fastq_pairs.csv) attached for reference. ```run_02.sh``` runs ```repair.sh``` that does the disordered read fixing.

#### Step3
This step gunzips the fixed fastq file from previous step for downstream operations. ```run_03.sh``` performs this operation. CSV file can be used to specify a subset of files from a folder to perform this step. Sample CSV (gunzip_list.csv) file attached for reference.

## Alignment
This pipeline consists of two steps that can be executed by specifying the number in the same script as follows:

```./00_run_align_call_filter_hg38.sh step_number```

The inputs are hardcoded in the _00_run_align_call_filter_hg38.sh_ script, so modify the script based on files to align:
#### Step1
Compress fastq files: If you haven't run step3 of unalignment pipeline/have a new set of fastq files, you will need to compress them to generate 'fastq.gz' or 'fq.gz' extension fastq files.

#### Step2
Convert fastq.gz files -> unaligned bam files: Given a list of compressed FASTQ files, this step converts them into unaligned BAM files calling the script _FastqToSam2.py_. Outputs are stored in a hidden folder in ${output_path}/.FastqToSam directory that contains the unaligned BAM files. Parameter '-csv' can be used to specify a subset of fastq files out of all the fastq files in a directory. 

Example CSV file:<br/>
```/n/data1/hms/dbmi/gulhan/lab/DATA/Gerburg_ULPWGS/tnbc/unaligned/78_C2D1_1.fastq.fix.fastq.gz /n/data1/hms/dbmi/gulhan/lab/DATA/Gerburg_ULPWGS/tnbc/unaligned/78_C2D1_2.fastq.fix.fastq.gz /n/data1/hms/dbmi/gulhan/lab/DATA/Gerburg_ULPWGS/tnbc/unaligned/83_C1D1_1.fastq.fix.fastq.gz /n/data1/hms/dbmi/gulhan/lab/DATA/Gerburg_ULPWGS/tnbc/unaligned/83_C1D1_2.fastq.fix.fastq.gz```

#### Step3
Unaligned bam files -> aligned bam files: This step aligns the unaligned BAM files created in the previous step to reference genome of our choice using _PreProcessing.py_ script. CSV file can be used to specify a subset of files from a folder to perform this step. Sample CSV (preprocessing.csv) file attached for reference.<br/>
_The WDL_ file defines the tasks and the order of tasks involved in the alignment step and a series of cromwell jobs are invoked to perform different tasks (such as MarkDuplicates, SortAndFixTags, CreateSequenceGroupingTSV, etc.). The cromwell jobs performing different tasks are executed in sequential order. Some tasks also have parallelization feature which enables faster completion of the task. These cromwell jobs, when executed, split data into multiple partitions and each partition is assigned a cromwell job to execute that partition's processing.<br/>
_The JSON_ file is used to define the parameters like reference genome to which you want to aling the BAMs to and all the associated files with ref_genome. It also defines various runtime values like java-mem, taks memory and time for executing different tasks listed in the WDL file for alignment, known resources in case mutation calling needs to be run, path to different softwares being used and disk size. <br/>
_The config_ files store the miscellanious config information to run the alignment step.
