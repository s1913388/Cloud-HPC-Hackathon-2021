"""
Tests `gatk CountBases` using public example data 

This is a more basic test that verifies GATK is fully installed.

This tests relies on a publically accessible HiSEQ 2500 BAM file. It is saved in scratch to avoid repetitively downloading big files.

```
mkdir /scratch/home/jayson/gatk-data
cd /scratch/home/jayson/gatk-data
wget https://storage.googleapis.com/genomics-public-data/test-data/dna/wgs/hiseq2500/NA12878/H06HDADXX130110.1.ATCACGAT.20k_reads.bam
```
"""
import reframe as rfm
import reframe.utility.sanity as sn
import hackathon as hack

@rfm.simple_test
class GATKTest(hack.HackathonBase):
    # Where to run the binaries 'aws:c6gn' on Arm or 'aws:c5n' on Intel
    valid_systems = ['aws:c6gn']

    # Logging Variables
    log_team_name = 'Falkners'
    log_app_name = 'GATK'

    # no pre-run. File are big and already in scratch
    prerun_cmds = []

    # Binary to run
    executable = 'gatk'
    # Where the output is written to
    logfile = 'gatk.out'
    # Store the output file (used for validation later)
    keep_files = [logfile]

    # Parameters - Compilers - Defined as their Spack specs (use spec or hash)
    # Only gcc on x86 but all three on ARM
    spec = parameter([
        'gatk@4.1.8.1%gcc@10.3.0',     # CoMD with the GCC compiler
        #'comd@1.1 %arm@21.0.0.879', # CoMD with the Arm compiler
        #'comd@1.1 %nvhpc@21.2'      # CoMD with the NVIDIA compiler
    ])

    log_test_name = f'gatk_countbases'

        # CLI args. "strong" largely means more atoms with eam potential
    executable_opts = [
         'CountBases -I /scratch/home/jayson/gatk-data/H06HDADXX130110.1.ATCACGAT.20k_reads.bam > gatk.out'
    ]

    # Scale MPI to confirm that more work takes similar time 
    parallelism = parameter([{ 'nodes' : 1, 'mpi' : 1, 'omp' : 1}])

    # Code validation
    @run_before('sanity')
    def set_sanity_patterns(self):

        # Use the logfile for validation testing and performance
        expected_count_regex = r'5000000'
        expected_count = sn.extractsingle(expected_count, self.logfile, 1, float)

        self.sanity_patterns = sn.assert_equal(expected_count, 5000000)

        # timing is taken from the code's self-reporting numbers
        self.reference = {
            '*': {'Total Time': (0, None, None, 's'),}
        }

        perf_regex = r'Processed 20000 total reads in (\S+) minutes'
        self.perf_patterns = {
            'Total Time': sn.extractsingle(pref_regex, self.logfile, 1, float, item=-1)
        }
