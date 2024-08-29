import os
import subprocess
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

# Step 1: Define paths and parameters
protein_file = "path/to/your/protein.pdb"  # Path to your protein PDB file
ligand_file = "path/to/your/ligands.csv"  # Path to your ligands CSV file
base_output_directory = "path/to/your/output_directory/"  # Directory where results will be saved
dynamicbind_script = "path/to/DynamicBind/run_single_protein_inference.py"  # Full path to the DynamicBind script
device_id = "0"  # Replace with your GPU device ID if applicable
combined_results_file = os.path.join(base_output_directory, "combined_affinity_predictions.csv")  # Path to save combined results

# Evaluate the Python executable paths
python_path = subprocess.check_output("which python", shell=True).decode().strip()
relax_python_path = subprocess.check_output("which python", shell=True).decode().strip()

# Prompt the user for the number of top ligands to select
num_top_ligands = int(input("Enter the number of top ligands to select: "))
top_ligands_file = os.path.join(base_output_directory, f"top_{num_top_ligands}_ligands.csv")  # Path to save top ligands

# Step 2: Create base output directory if it doesn't exist
if not os.path.exists(base_output_directory):
    os.makedirs(base_output_directory)

# Step 3: Load ligands and extract names
ligands_df = pd.read_csv(ligand_file)
ligands_df[['smiles', 'name']] = ligands_df['ligand'].str.split(' ', n=1, expand=True)

# Check if the 'smiles' and 'name' columns exist
if 'smiles' not in ligands_df.columns or 'name' not in ligands_df.columns:
    raise ValueError("The CSV file must contain 'smiles' and 'name' columns after splitting.")

# Print the number of ligands to be processed
print(f"Number of ligands to be processed: {len(ligands_df)}")

# Optional: Print the ligand CSV contents for debugging (first few rows)
print("Ligand CSV file sample contents:")
print(ligands_df.head())

# Step 4: Run docking simulations
def run_docking(protein_file, ligand_smiles, ligand_name, base_output_directory, dynamicbind_script, device_id, python_path, relax_python_path):
    ligand_specific_output_dir = os.path.join(base_output_directory, ligand_name)
    if not os.path.exists(ligand_specific_output_dir):
        os.makedirs(ligand_specific_output_dir)
    
    # Write the single ligand to a temporary CSV file
    temp_ligand_file = os.path.join(ligand_specific_output_dir, "ligand.csv")
    with open(temp_ligand_file, 'w') as f:
        f.write("ligand\n")
        f.write(f"{ligand_smiles}\n")
    
    command = (
        f"python {dynamicbind_script} {protein_file} {temp_ligand_file} --hts "
        f"--savings_per_complex 3 --inference_steps 20 --header {ligand_name} "
        f"--device {device_id} --python {python_path} --relax_python {relax_python_path}"
    )
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command for {ligand_name}:\n{result.stderr}")
    else:
        print(f"Completed docking for {ligand_name}:\n{result.stdout}")

# Loop through ligands and run docking with progress bar
for _, row in tqdm(ligands_df.iterrows(), total=len(ligands_df), desc="Docking ligands"):
    run_docking(protein_file, row['smiles'], row['name'], base_output_directory, dynamicbind_script, device_id, python_path, relax_python_path)

# Step 5: Extract results with progress bar
def extract_results(base_output_directory, ligands_df):
    all_results = []
    for _, row in tqdm(ligands_df.iterrows(), total=len(ligands_df), desc="Extracting results"):
        ligand_name = row['name']
        ligand_specific_output_dir = os.path.join(base_output_directory, ligand_name)
        results_file = os.path.join(ligand_specific_output_dir, "complete_affinity_prediction.csv")
        if os.path.exists(results_file):
            print(f"Results file found for ligand {ligand_name}: {results_file}")
            results_df = pd.read_csv(results_file)
            results_df['name'] = ligand_name
            all_results.append(results_df)
        else:
            print(f"Results file not found for ligand {ligand_name}. Checked path: {results_file}")
    
    if all_results:
        combined_results_df = pd.concat(all_results, ignore_index=True)
        combined_results_df.to_csv(combined_results_file, index=False)
        print(f"Combined docking results saved to {combined_results_file}")
    else:
        print("No results files found.")
        return None

    return combined_results_df

results_df = extract_results(base_output_directory, ligands_df)

# Step 6: Select top ligands
if results_df is not None:
    # Ensure that the necessary columns are present
    required_columns = ['name', 'affinity', 'lddt']
    for column in required_columns:
        if column not in results_df.columns:
            raise ValueError(f"The column '{column}' is missing from the results file.")

    # Normalize affinity and LDDT
    scaler = MinMaxScaler()
    results_df['norm_affinity'] = 1 - scaler.fit_transform(results_df[['affinity']])  # Invert affinity for normalization
    results_df['norm_lddt'] = scaler.fit_transform(results_df[['lddt']])

    # Compute combined score (weights can be adjusted as needed)
    results_df['combined_score'] = results_df['norm_affinity'] * 0.5 + results_df['norm_lddt'] * 0.5

    # Sort the results by combined score (higher is better)
    sorted_results_df = results_df.sort_values(by='combined_score', ascending=False)

    # Select the top ligands
    top_ligands_df = sorted_results_df.head(num_top_ligands)

    # Display the top ligands
    print(f"Top {num_top_ligands} ligands based on combined score:")
    print(top_ligands_df)

    # Save the top ligands to a CSV file
    top_ligands_df.to_csv(top_ligands_file, index=False)

    print(f"Top {num_top_ligands} ligands saved to {top_ligands_file}")
