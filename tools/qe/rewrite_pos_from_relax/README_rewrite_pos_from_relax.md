
# Rewrite POS from Relax Script

This script extracts the final atomic positions from a relaxation output file and replaces the atomic positions in another input file. It is particularly useful in computational materials science workflows, where atomic coordinates need to be updated based on the results of a structural relaxation simulation.

## Features

- **Extract Final Atomic Positions:** The script locates the last "ATOMIC_POSITIONS (crystal)" block in the provided output file.
- **Replace Atomic Positions:** It then uses the extracted atomic positions to replace the positions in another input file.

## Prerequisites

- Python 3.x
- Ensure that the input/output files used with this script are accessible and in the correct format.

## Usage

1. Place the relaxation output file (e.g., `scf_relax.out`) and the input file to be modified in the same directory as this script.
2. Use the script's functions as follows:

    ```python
    from rewrite_pos_from_relax import extract_last_atomic_positions, replace_atomic_positions
    
    # Extract atomic positions from the output file
    positions = extract_last_atomic_positions('scf_relax.out')
    
    # Replace atomic positions in the input file
    replace_atomic_positions('input_file.in', 'scf_relax.out')
    ```

## Functions

- `extract_last_atomic_positions(out_file_path)`: Extracts the last "ATOMIC_POSITIONS (crystal)" block from the specified file.
  - **Parameters**: `out_file_path` - Path to the output file containing atomic positions.
  - **Returns**: A list of strings representing the atomic positions or `None` if the block is not found.
  
- `replace_atomic_positions(in_file_path, out_file_path)`: Replaces the atomic positions in the input file using the extracted positions from the output file.
  - **Parameters**:
    - `in_file_path` - Path to the input file where atomic positions will be replaced.
    - `out_file_path` - Path to the output file containing the new atomic positions.

## Error Handling

- The script prints an error message if the output file specified in `extract_last_atomic_positions` is not found.

## License

This script is licensed under the Mozilla Public License 2.0 (MPL-2.0).

## Author

Kazuyoshi Yoshimi (ISSP, Univ. of Tokyo)
