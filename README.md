# DynamicBind Screening Automator (DBSA)

**DynamicBind Screening Automator (DBSA)** is a Python tool designed to automate the process of virtual screening for ligands using the DynamicBind tool. DBSA streamlines the workflow by handling large sets of ligands, running docking simulations, and selecting top candidates based on combined affinity and LDDT scores.

## Features

- **Automated Docking**: Performs docking simulations for a set of ligands against a specified protein using DynamicBind.
- **Result Aggregation**: Collects and combines affinity predictions from multiple docking runs into a single, easy-to-analyze CSV file.
- **Top Ligand Selection**: Normalizes affinity and LDDT scores, ranks ligands, and selects the top candidates based on combined scores.

## Requirements

- **Python 3.x**
- **DynamicBind**: DBSA is an automation tool that requires DynamicBind to be preinstalled and functioning correctly. You can find DynamicBind on its [GitHub page](https://github.com/luwei0917/DynamicBind).
- Required Python libraries:
  - `os`
  - `subprocess`
  - `pandas`
  - `scikit-learn`
  - `tqdm`

To install the required Python libraries, run:
```bash
pip install pandas scikit-learn tqdm
```
## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/aleff-ferreira/DBSA.git
   cd DBSA
   ```

2. **Ensure DynamicBind is Installed**:
   DBSA relies on DynamicBind for docking simulations. Please ensure that DynamicBind is installed and configured correctly on your system. Instructions for setting up DynamicBind can be found on its [GitHub page](https://github.com/luwei0917/DynamicBind).

3. **Activate the Conda Environment**:
   Before running the DBSA script, you must activate the conda environment where DynamicBind is installed. If you followed the standard setup, you can activate the environment as follows:

   ```bash
   conda activate dynamicbind
   ```

4. **Prepare Input Files**:
   - **Protein PDB file**: Your protein file should be in PDB format.
   - **Ligand CSV file**: Create a CSV file containing your ligands. Each row should include a SMILES string and a ligand name, separated by a space.

5. **Set Parameters**:
   Modify the script to define the paths to your protein file, ligand file, DynamicBind script, and output directory.

   ```python
   protein_file = "path/to/your/protein.pdb"  # Path to your protein PDB file
   ligand_file = "path/to/your/ligands.csv"  # Path to your ligands CSV file
   base_output_directory = "path/to/your/output_directory/"  # Directory where results will be saved
   dynamicbind_script = "path/to/DynamicBind/run_single_protein_inference.py"  # Full path to the DynamicBind script
   device_id = "0"  # Replace with your GPU device ID if applicable
   ```

## Usage

1. **Run the Script**:
   ```bash
   python DBSA.py
   ```

   The script will:
   - Create an output directory if it doesn’t exist.
   - Load the ligand file and split it into SMILES and ligand names.
   - Run docking simulations for each ligand using DynamicBind.
   - Aggregate the results into a single CSV file.
   - Normalize and rank the ligands based on affinity and LDDT scores.
   - Save the top-ranked ligands to a CSV file.

2. **Select Top Ligands**:
   The script will prompt you to enter the number of top ligands you wish to select. The results will be saved in a CSV file named `top_{num_top_ligands}_ligands.csv`.

## Example Command

```bash
Enter the number of top ligands to select: 10
Top 10 ligands saved to path/to/your/output_directory/top_10_ligands.csv
```

## Troubleshooting

- **DynamicBind Errors**: Ensure that DynamicBind is correctly installed and that the paths to its scripts are accurate. Refer to the [DynamicBind GitHub page](https://github.com/luwei0917/DynamicBind) for setup instructions.
- **Conda Environment**: Make sure to activate the correct conda environment (`dynamicbind`) before running the script. If not activated, the script will not find the necessary dependencies.
- **Missing Columns**: If the script raises a `ValueError` for missing columns, ensure that your ligand CSV file contains both `smiles` and `name` columns after splitting.
- **File Not Found**: If the script reports missing result files, verify that your DynamicBind script and input files are correctly specified.

## References

For more information on DynamicBind, please refer to the [DynamicBind GitHub page](https://github.com/luwei0917/DynamicBind).
