import os

def fetch_environ(var, val):
    """
    Test is environment variable flag is set to a specific value.
    Otherwise return False (if not set or set to another value).
    Value should be a string, and case is ignored.
    """
    if var in os.environ and os.environ[var].upper() == val.upper():
        return True
    else:
        return False

######################################################################
# HTTP server settings
######################################################################

port = 3524

devel = fetch_environ('devel', 'True')

if devel:
    print('** WARNING: Running in development mode **')

# Maximum temperature according to RPi foundation
pi_max_temp = 85

######################################################################
# Cluster queue settings                                             #
######################################################################

IPs = [
        ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
        ["10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8"],
        ["10.0.0.9", "10.0.0.10", "10.0.0.11", "10.0.0.12"],
        ["10.0.0.13"],
        ]
nnodes = len(IPs)

cores_per_node = 4

nodes_per_job = 1

root_dir = os.path.dirname(os.path.abspath(__file__)).replace('/nfs/nodeimg','')

cfdcommand = "python3 " + root_dir + "/cfd/runcfd.py {id} {ncores} {hostfile} 2>{output}.err >> {output}"

######################################################################
# CFD settings                                                       #
######################################################################

base_path = os.path.dirname(os.path.realpath(__file__))

# Output files
poly_fname = "simulation.poly"

# Configuration files
elmer_sif_file = '{root_dir}/cfd/config.sif'.format(root_dir=root_dir)

number_timesteps = 10

# The total number of times that "Starting Step" is written to the slurm output file
# This is used for progress indication. Take care when changing this.
jobstep_count = 5

# Executables
triangle_exe = '{root_dir}/cfd/triangle-lib/triangle'.format(root_dir=root_dir)
elmer_postprocess_serial_exe = '{root_dir}/cfd/elmerpostprocessserial'.format(root_dir=root_dir)
elmer_postprocess_parallel_exe = '{root_dir}/cfd/elmerpostprocessparallel'.format(root_dir=root_dir)
