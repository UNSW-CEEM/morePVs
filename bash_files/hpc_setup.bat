#!/bin/bash
#SBATCH --mail-user=m.roberts@unsw.edu.au
#SBATCH --mail-type=ALL
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8192
#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_3/slurm/slurm-%j.out"
module load python/3.6
source /home/z5044992/python_venv/bin/activate
python /home/z5044992/InputOutput/en/morePVs/hpc_setup.py
deactivate
module unload python/3.6