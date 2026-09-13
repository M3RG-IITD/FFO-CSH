#!/usr/bin/env python3
"""
trim_water.py — Trim water molecules in a LAMMPS data file to an exact count.

Usage:
    python trim_water.py step2a_untrimmed.data step2a_trimmed.data 1789

Reads the data file, identifies bulk water molecules (atom types 11 & 12),
randomly removes excess molecules, renumbers everything, and writes a
clean LAMMPS data file.
"""

import sys
import random
import copy

def parse_lammps_data(filename):
    """Parse a LAMMPS data file into sections."""
    with open(filename) as f:
        lines = f.readlines()

    data = {
        'header_lines': [],
        'masses': [],
        'atoms': [],
        'bonds': [],
        'angles': [],
        'velocities': [],
        'box': [],
        'counts': {},
        'type_counts': {},
    }

    section = 'header'
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        # Detect section headers
        if line == 'Masses':
            section = 'masses'
            i += 1  # skip blank line
            continue
        elif line == 'Atoms':
            section = 'atoms'
            i += 1
            continue
        elif line == 'Velocities':
            section = 'velocities'
            i += 1
            continue
        elif line == 'Bonds':
            section = 'bonds'
            i += 1
            continue
        elif line == 'Angles':
            section = 'angles'
            i += 1
            continue
        elif line in ('Dihedrals', 'Impropers',
                      'Pair Coeffs', 'Bond Coeffs', 'Angle Coeffs',
                      'Dihedral Coeffs', 'Improper Coeffs'):
            section = line.lower().replace(' ', '_')
            i += 1
            continue

        if not line or line.startswith('#'):
            if section == 'header':
                data['header_lines'].append(lines[i-1])
            continue

        parts = line.split()

        if section == 'header':
            if len(parts) >= 2 and parts[1] == 'atoms':
                data['counts']['atoms'] = int(parts[0])
            elif len(parts) >= 2 and parts[1] == 'bonds':
                data['counts']['bonds'] = int(parts[0])
            elif len(parts) >= 2 and parts[1] == 'angles':
                data['counts']['angles'] = int(parts[0])
            elif len(parts) >= 3 and parts[1] == 'atom' and parts[2] == 'types':
                data['type_counts']['atom'] = int(parts[0])
            elif len(parts) >= 3 and parts[1] == 'bond' and parts[2] == 'types':
                data['type_counts']['bond'] = int(parts[0])
            elif len(parts) >= 3 and parts[1] == 'angle' and parts[2] == 'types':
                data['type_counts']['angle'] = int(parts[0])
            elif len(parts) >= 4 and parts[2] in ('xlo', 'ylo', 'zlo'):
                data['box'].append(line)
            else:
                data['header_lines'].append(lines[i-1])
        elif section == 'masses':
            if parts[0].replace('.','',1).lstrip('-').isdigit():
                data['masses'].append(line)
        elif section == 'atoms':
            if parts[0].isdigit():
                data['atoms'].append(parts)
        elif section == 'velocities':
            pass  # skip velocities
        elif section == 'bonds':
            if parts[0].isdigit():
                data['bonds'].append(parts)
        elif section == 'angles':
            if parts[0].isdigit():
                data['angles'].append(parts)

    return data


def trim_water(data, target_water, water_types={11, 12}, seed=42):
    """
    Remove excess water molecules to reach target_water count.

    Water molecules are identified by having ALL atoms with types in water_types.
    """
    random.seed(seed)

    # --- Identify water molecules ---
    # Group atoms by molecule ID
    mol_atoms = {}  # mol_id -> list of atom entries
    for atom in data['atoms']:
        mol_id = int(atom[1])
        if mol_id not in mol_atoms:
            mol_atoms[mol_id] = []
        mol_atoms[mol_id].append(atom)

    # Find water molecule IDs (all atoms have water types)
    water_mol_ids = []
    non_water_mol_ids = []
    for mol_id, atoms in mol_atoms.items():
        if all(int(a[2]) in water_types for a in atoms):
            water_mol_ids.append(mol_id)
        else:
            non_water_mol_ids.append(mol_id)

    current_water = len(water_mol_ids)
    print(f"  Current water molecules: {current_water}")
    print(f"  Target water molecules:  {target_water}")

    if target_water > current_water:
        print(f"  ERROR: target ({target_water}) > available ({current_water})")
        sys.exit(1)
    elif target_water == current_water:
        print(f"  No trimming needed.")
        return data

    n_remove = current_water - target_water
    print(f"  Removing {n_remove} water molecules...")

    # Randomly select molecules to REMOVE
    remove_mols = set(random.sample(water_mol_ids, n_remove))

    # --- Filter atoms ---
    keep_atom_ids = set()
    new_atoms = []
    for atom in data['atoms']:
        mol_id = int(atom[1])
        if mol_id not in remove_mols:
            new_atoms.append(atom)
            keep_atom_ids.add(int(atom[0]))

    # --- Filter bonds ---
    new_bonds = []
    for bond in data['bonds']:
        a1, a2 = int(bond[2]), int(bond[3])
        if a1 in keep_atom_ids and a2 in keep_atom_ids:
            new_bonds.append(bond)

    # --- Filter angles ---
    new_angles = []
    for angle in data['angles']:
        a1, a2, a3 = int(angle[2]), int(angle[3]), int(angle[4])
        if a1 in keep_atom_ids and a2 in keep_atom_ids and a3 in keep_atom_ids:
            new_angles.append(angle)

    # --- Renumber atom IDs ---
    old_to_new = {}
    for i, atom in enumerate(new_atoms, 1):
        old_id = int(atom[0])
        old_to_new[old_id] = i
        atom[0] = str(i)

    # Renumber molecule IDs (compact)
    old_mol_to_new = {}
    mol_counter = 0
    for atom in new_atoms:
        old_mol = int(atom[1])
        if old_mol not in old_mol_to_new:
            mol_counter += 1
            old_mol_to_new[old_mol] = mol_counter
        atom[1] = str(old_mol_to_new[old_mol])

    # Renumber bond atom references
    for i, bond in enumerate(new_bonds, 1):
        bond[0] = str(i)
        bond[2] = str(old_to_new[int(bond[2])])
        bond[3] = str(old_to_new[int(bond[3])])

    # Renumber angle atom references
    for i, angle in enumerate(new_angles, 1):
        angle[0] = str(i)
        angle[2] = str(old_to_new[int(angle[2])])
        angle[3] = str(old_to_new[int(angle[3])])
        angle[4] = str(old_to_new[int(angle[4])])

    data['atoms'] = new_atoms
    data['bonds'] = new_bonds
    data['angles'] = new_angles
    data['counts']['atoms'] = len(new_atoms)
    data['counts']['bonds'] = len(new_bonds)
    data['counts']['angles'] = len(new_angles)

    print(f"  Final: {len(new_atoms)} atoms, {len(new_bonds)} bonds, {len(new_angles)} angles")
    return data


def write_lammps_data(data, filename):
    """Write a clean LAMMPS data file."""
    with open(filename, 'w') as f:
        f.write(f"# LAMMPS data file — trimmed to target water count\n\n")
        f.write(f"{data['counts']['atoms']} atoms\n")
        f.write(f"{data['counts']['bonds']} bonds\n")
        f.write(f"{data['counts']['angles']} angles\n\n")
        f.write(f"{data['type_counts']['atom']} atom types\n")
        f.write(f"{data['type_counts']['bond']} bond types\n")
        f.write(f"{data['type_counts']['angle']} angle types\n\n")
        for box_line in data['box']:
            f.write(box_line + '\n')
        f.write('\n')

        f.write('Masses\n\n')
        for m in data['masses']:
            f.write(m + '\n')
        f.write('\n')

        f.write('Atoms\n\n')
        for atom in data['atoms']:
            f.write(' '.join(atom) + '\n')
        f.write('\n')

        f.write('Bonds\n\n')
        for bond in data['bonds']:
            f.write(' '.join(bond) + '\n')
        f.write('\n')

        f.write('Angles\n\n')
        for angle in data['angles']:
            f.write(' '.join(angle) + '\n')

    print(f"  Written to: {filename}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python trim_water.py <input.data> <output.data> <target_water_count>")
        print("Example: python trim_water.py step2a_untrimmed.data step2a_trimmed.data 1789")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    target = int(sys.argv[3])

    print(f"Reading {input_file}...")
    data = parse_lammps_data(input_file)
    print(f"  {data['counts']['atoms']} atoms, {data['counts']['bonds']} bonds, {data['counts']['angles']} angles")

    data = trim_water(data, target)
    write_lammps_data(data, output_file)
    print("Done!")
