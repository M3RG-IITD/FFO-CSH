# ## Cleaning data - removing coreshell O and it's bond
# 
# ### Definitions of Core shell data file
# 
# #### 1 40.08  #Ca  
# #### 2 28.10  #Si 
# #### 3 15.59  #O 
# #### 4 0.40   #O(S) 
# #### 5 16.00  #Ow 
# #### 6 16.00  #Oh 
# #### 7 1.00   #Hw 
# #### 8 1.00   #H 
# 
# ### bonds
# #### 1 #Oh-H
# #### 2 #Ow-Hw
# #### 3 #O-O(S)
# 
# ### Angles
# #### 1  #SPC/Fw
# #### 2  #O-Si-O
# #### 3  #Si-Oh-H
# 
# 
# 

import os
os.chdir('0_CSH_transfer/pyCSH-clean/output/final_data/cemff/data')

for file_name in os.listdir():
    if file_name.endswith('3.data'):
        print(file_name)

        def modify_lammps_data():
            
            # EDIT THESE VARIABLES
            input_file = file_name  # Change to your input filename
            output_file = "Output.data"  # Output filename
            atom_type_to_remove = 4             # Atom type to remove
            bond_type_to_remove = 3             # Bond type to remove
            
            print(f"Processing {input_file} to remove atom type {atom_type_to_remove} and bond type {bond_type_to_remove}")
            
            # Read the entire file
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            # Parse the header and box dimensions
            header = {}
            box_section = []
            tilt_factors = []
            body_start = 0
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):
                    if 'atoms' in line:
                        header['atoms'] = int(line.split()[0])
                    elif 'bonds' in line:
                        header['bonds'] = int(line.split()[0])
                    elif 'angles' in line:
                        header['angles'] = int(line.split()[0])
                    elif 'atom types' in line:
                        header['atom_types'] = int(line.split()[0])
                    elif 'bond types' in line:
                        header['bond_types'] = int(line.split()[0])
                    elif 'angle types' in line:
                        header['angle_types'] = int(line.split()[0])
                    elif 'dihedrals' in line:
                        header['dihedrals'] = int(line.split()[0])
                    elif 'impropers' in line:
                        header['impropers'] = int(line.split()[0])
                    elif 'xlo xhi' in line:
                        # Capture box dimensions
                        box_section.append(f"    {line}\n")
                        # Get ylo yhi, zlo zhi, and tilt factors in subsequent lines
                        for j in range(i+1, i+4):
                            if j < len(lines):
                                box_line = lines[j].strip()
                                if box_line and not box_line.startswith('#'):
                                    if 'ylo yhi' in box_line:
                                        box_section.append(f"    {box_line}\n")
                                    elif 'zlo zhi' in box_line:
                                        box_section.append(f"    {box_line}\n")
                                    elif 'xy xz yz' in box_line:
                                        tilt_factors = box_line.split()
                                        box_section.append(f"    {box_line}\n")
                        body_start = i + 4  # Skip past box dimensions
                        break
            
            print("\nOriginal counts:")
            print(f"Atoms: {header['atoms']}")
            print(f"Bonds: {header['bonds']}")
            print(f"Angles: {header['angles']}")
            print(f"Atom types: {header['atom_types']}")
            print(f"Bond types: {header['bond_types']}")
            print(f"Angle types: {header.get('angle_types', 'N/A')}")
            print("\nBox dimensions:")
            print("".join(box_section))
            
            # Initialize variables
            masses = []
            atoms = []
            bonds = []
            angles = []
            dihedrals = []
            impropers = []
            
            # Dictionaries for mapping old IDs to new IDs
            atom_id_map = {}
            atom_type_map = {}
            bond_id_map = {}
            
            # Track current section
            current_section = None
            
            # Process all sections in one pass
            for i in range(body_start, len(lines)):
                line = lines[i].strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Check for section headers
                if line in ["Masses", "Atoms", "Bonds", "Angles", "Dihedrals", "Impropers"]:
                    current_section = line
                    continue
                    
                # Process content based on current section
                if current_section == "Masses":
                    parts = line.split()
                    if len(parts) >= 2:
                        old_type = int(parts[0])
                        if old_type != atom_type_to_remove:
                            atom_type_map[old_type] = len(atom_type_map) + 1
                            masses.append((atom_type_map[old_type], parts[1]))
                        else:
                            print(f"Removing mass for atom type {old_type}")
                            
                elif current_section == "Atoms":
                    parts = line.split()
                    if len(parts) >= 5:
                        atom_id = int(parts[0])
                        atom_type = int(parts[2])
                        if atom_type == atom_type_to_remove:
                            print(f"Removing atom {atom_id} of type {atom_type}")
                        else:
                            atom_id_map[atom_id] = len(atom_id_map) + 1
                            parts[0] = str(atom_id_map[atom_id])
                            parts[2] = str(atom_type_map[atom_type])
                            atoms.append(" ".join(parts))
                            
                elif current_section == "Bonds":
                    parts = line.split()
                    if len(parts) >= 4:
                        bond_id = int(parts[0])
                        bond_type = int(parts[1])
                        atom1 = int(parts[2])
                        atom2 = int(parts[3])
                        
                        if (bond_type == bond_type_to_remove or 
                            atom1 not in atom_id_map or 
                            atom2 not in atom_id_map):
                            print(f"Removing bond {bond_id} (type {bond_type}) between atoms {atom1}-{atom2}")
                        else:
                            bond_id_map[bond_id] = len(bond_id_map) + 1
                            parts[0] = str(bond_id_map[bond_id])
                            parts[2] = str(atom_id_map[atom1])
                            parts[3] = str(atom_id_map[atom2])
                            bonds.append(" ".join(parts))
                            
                elif current_section == "Angles":
                    parts = line.split()
                    if len(parts) >= 5:
                        angle_id = int(parts[0])
                        atom1 = int(parts[2])
                        atom2 = int(parts[3])
                        atom3 = int(parts[4])
                        
                        if (atom1 not in atom_id_map or 
                            atom2 not in atom_id_map or 
                            atom3 not in atom_id_map):
                            print(f"Removing angle {angle_id} involving atoms {atom1}-{atom2}-{atom3}")
                        else:
                            parts[2] = str(atom_id_map[atom1])
                            parts[3] = str(atom_id_map[atom2])
                            parts[4] = str(atom_id_map[atom3])
                            angles.append(" ".join(parts))
            
            # Update header counts
            header['atoms'] = len(atom_id_map)
            header['bonds'] = len(bond_id_map)
            header['angles'] = len(angles)
            header['atom_types'] = len(atom_type_map)
            header['bond_types'] -= 1 if any(b[1] == bond_type_to_remove for b in bonds) else 0
            
            # Write the modified file
            with open(output_file, 'w') as f:
                # Write header
                f.write("LAMMPS data file - modified version\n\n")
                f.write(f"    {header['atoms']} atoms\n")
                f.write(f"    {header['bonds']} bonds\n")
                f.write(f"    {header['angles']} angles\n")
                f.write(f"    {header['atom_types']} atom types\n")
                f.write(f"    {header['bond_types']} bond types\n")
                if 'angle_types' in header:
                    f.write(f"    {header['angle_types']} angle types\n")
                if 'dihedrals' in header:
                    f.write(f"    {header['dihedrals']} dihedrals\n")
                if 'impropers' in header:
                    f.write(f"    {header['impropers']} impropers\n")
                f.write("\n")
                
                # Write box dimensions
                f.write("".join(box_section))
                f.write("\n")
                
                # Write Masses section
                if masses:
                    f.write("Masses\n\n")
                    for mass in masses:
                        f.write(f"    {mass[0]} {mass[1]}\n")
                    f.write("\n")
                
                # Write Atoms section
                if atoms:
                    f.write("Atoms\n\n")
                    for atom in atoms:
                        f.write(f"    {atom}\n")
                    f.write("\n")
                
                # Write Bonds section
                if bonds:
                    f.write("Bonds\n\n")
                    for bond in bonds:
                        f.write(f"    {bond}\n")
                    f.write("\n")
                
                # Write Angles section
                if angles:
                    f.write("Angles\n\n")
                    for angle in angles:
                        f.write(f"    {angle}\n")
                    f.write("\n")
            
            print("\nProcessing complete!")
            print(f"New file saved as {output_file}")

        # Run the function
        modify_lammps_data()


        # ## Addition of bond
        # 
        # #### 3 - Si - O
        # #### 4 - Si - Oh


        import numpy as np
        from collections import defaultdict

        class LAMMPSDataFile:
            def __init__(self, filename):
                self.filename = filename
                self.headers = {}
                self.atoms = []
                self.masses = []
                self.bonds = []
                self.angles = []
                self.dihedrals = []
                self.impropers = []
                self.atom_types = 0
                self.bond_types = 0
                self.angle_types = 0
                self.dihedral_types = 0
                self.improper_types = 0
                self.xlo = self.xhi = self.ylo = self.yhi = self.zlo = self.zhi = 0.0
                self.xy = self.xz = self.yz = 0.0
                self.box = np.zeros((3,3))
                self.inv_box = None
                
                self._read_data_file()  # Changed method name to avoid confusion
                self._setup_box_vectors()

            def _parse_header(self, line):
                """Parse header lines from LAMMPS data file"""
                if 'atoms' in line:
                    self.headers['atoms'] = int(line.split()[0])
                elif 'bonds' in line:
                    self.headers['bonds'] = int(line.split()[0])
                elif 'angles' in line:
                    self.headers['angles'] = int(line.split()[0])
                elif 'atom types' in line:
                    self.atom_types = int(line.split()[0])
                elif 'bond types' in line:
                    self.bond_types = int(line.split()[0])
                elif 'angle types' in line:
                    self.angle_types = int(line.split()[0])
                elif 'xlo xhi' in line:
                    self.xlo, self.xhi = map(float, line.split()[:2])
                elif 'ylo yhi' in line:
                    self.ylo, self.yhi = map(float, line.split()[:2])
                elif 'zlo zhi' in line:
                    self.zlo, self.zhi = map(float, line.split()[:2])
                elif 'xy xz yz' in line:
                    self.xy, self.xz, self.yz = map(float, line.split()[:3])

            def _parse_section(self, section, line):
                """Parse data sections from LAMMPS data file"""
                if not line or not line[0].isdigit():
                    return
                    
                parts = line.split()
                if section == 'Atoms':
                    self.atoms.append({
                        'id': int(parts[0]),
                        'mol': int(parts[1]),
                        'type': int(parts[2]),
                        'charge': float(parts[3]),
                        'x': float(parts[4]),
                        'y': float(parts[5]),
                        'z': float(parts[6])
                    })
                elif section == 'Bonds':
                    self.bonds.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3])
                    })
                elif section == 'Angles':
                    self.angles.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3]),
                        'atom3': int(parts[4])
                    })
                elif section == 'Masses':
                    self.masses.append({
                        'type': int(parts[0]),
                        'mass': float(parts[1])
                    })

            def _read_data_file(self):
                """Read LAMMPS data file and parse sections"""
                try:
                    with open(self.filename, 'r') as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    raise FileNotFoundError(f"Could not find file: {self.filename}")
                
                section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Section headers
                    if line.startswith('Atoms'):
                        section = 'Atoms'
                        continue
                    elif line.startswith('Bonds'):
                        section = 'Bonds'
                        continue
                    elif line.startswith('Masses'):
                        section = 'Masses'
                        continue
                    elif line.startswith('Angles'):
                        section = 'Angles'
                        continue
                    
                    # Parse content
                    if section:
                        self._parse_section(section, line)
                    else:
                        self._parse_header(line)

            def _setup_box_vectors(self):
                """Initialize triclinic box vectors and inverse"""
                self.box[0][0] = self.xhi - self.xlo
                self.box[1][1] = self.yhi - self.ylo
                self.box[2][2] = self.zhi - self.zlo
                self.box[1][0] = self.xy
                self.box[2][0] = self.xz
                self.box[2][1] = self.yz
                self.inv_box = np.linalg.inv(self.box)

            def add_bonds_with_rules(self, bonding_rules):
                """
                User-friendly bond creation interface
                Example rules:
                [
                    {'type_a': 2, 'type_b': 3, 'cutoff': 2.0, 'bond_type': 3}, 
                    {'type_a': 2, 'type_b': 5, 'cutoff': 2.0, 'bond_type': 2}
                ]
                """
                for rule in bonding_rules:
                    self._add_bonds_by_cutoff(
                        type_a=rule['type_a'],
                        type_b=rule['type_b'],
                        cutoff=rule['cutoff'],
                        bond_type=rule['bond_type'],
                        allow_duplicates=rule.get('allow_duplicates', False)
                    )
                # Update bond types count
                existing_types = {b['type'] for b in self.bonds}
                self.bond_types = max(existing_types)

            def _add_bonds_by_cutoff(self, type_a, type_b, cutoff, bond_type, allow_duplicates=False):
                """Core bonding function with PBC handling"""
                cutoff_sq = cutoff**2
                existing_pairs = {(min(b['atom1'], b['atom2']), max(b['atom1'], b['atom2'])) 
                                for b in self.bonds}
                new_bonds = []

                atoms_a = [a for a in self.atoms if a['type'] == type_a]
                atoms_b = [a for a in self.atoms if a['type'] == type_b]

                for a in atoms_a:
                    for b in atoms_b:
                        if a['id'] == b['id']:
                            continue
                        
                        # Sort atom IDs to avoid duplicates
                        atom1, atom2 = sorted((a['id'], b['id']))
                        if not allow_duplicates and (atom1, atom2) in existing_pairs:
                            continue
                        
                        # Check all periodic images
                        for dx, dy, dz in [(i,j,k) for i in (-1,0,1) for j in (-1,0,1) for k in (-1,0,1)]:
                            # Replicate atom position
                            x = b['x'] + dx*self.box[0][0] + dy*self.box[1][0] + dz*self.box[2][0]
                            y = b['y'] + dy*self.box[1][1] + dz*self.box[2][1]
                            z = b['z'] + dz*self.box[2][2]
                            
                            # Distance check
                            r_sq = (x-a['x'])**2 + (y-a['y'])**2 + (z-a['z'])**2
                            if r_sq <= cutoff_sq:
                                new_bonds.append({
                                    'atom1': atom1,
                                    'atom2': atom2,
                                    'type': bond_type
                                })
                                existing_pairs.add((atom1, atom2))
                                break  # Only need one periodic image

                # Add new bonds
                start_id = max([b['id'] for b in self.bonds], default=0) + 1
                for i, bond in enumerate(new_bonds):
                    self.bonds.append({
                        'id': start_id + i,
                        'type': bond['type'],
                        'atom1': bond['atom1'],
                        'atom2': bond['atom2']
                    })
                
                print(f"Added {len(new_bonds)} bonds (type {bond_type}) between types {type_a}-{type_b}")

            def write_data_file(self, output_filename):
                """Write updated LAMMPS data file"""
                with open(output_filename, 'w') as f:
                    # Headers
                    f.write("LAMMPS data file - Custom Bonded\n\n")
                    f.write(f"{len(self.atoms)} atoms\n")
                    f.write(f"{len(self.bonds)} bonds\n")
                    f.write(f"{len(self.angles)} angles\n")
                    f.write(f"{self.atom_types} atom types\n")
                    f.write(f"{self.bond_types} bond types\n")
                    f.write(f"{self.angle_types} angle types\n\n")
                    
                    # Box
                    f.write(f"{self.xlo:.6f} {self.xhi:.6f} xlo xhi\n")
                    f.write(f"{self.ylo:.6f} {self.yhi:.6f} ylo yhi\n")
                    f.write(f"{self.zlo:.6f} {self.zhi:.6f} zlo zhi\n")
                    f.write(f"{self.xy:.6f} {self.xz:.6f} {self.yz:.6f} xy xz yz\n\n")
                    
                    # Masses
                    f.write("Masses\n\n")
                    for mass in sorted(self.masses, key=lambda x: x['type']):
                        f.write(f"{mass['type']} {mass['mass']:.4f}\n")
                    f.write("\n")
                    
                    # Atoms
                    f.write("Atoms # full\n\n")
                    for atom in sorted(self.atoms, key=lambda x: x['id']):
                        f.write(f"{atom['id']} {atom['mol']} {atom['type']} {atom['charge']:.6f} "
                            f"{atom['x']:.6f} {atom['y']:.6f} {atom['z']:.6f}\n")
                    
                    # Bonds
                    f.write("\nBonds\n\n")
                    for bond in sorted(self.bonds, key=lambda x: x['id']):
                        f.write(f"{bond['id']} {bond['type']} {bond['atom1']} {bond['atom2']}\n")
                    
                    # Angles
                    if self.angles:
                        f.write("\nAngles\n\n")
                        for angle in sorted(self.angles, key=lambda x: x['id']):
                            f.write(f"{angle['id']} {angle['type']} {angle['atom1']} {angle['atom2']} {angle['atom3']}\n")

        if __name__ == "__main__":
            try:
                # Example Usage
                data = LAMMPSDataFile("Output.data")
                
                # Define bonding rules for your system
                bonding_rules = [
                    {'type_a': 2, 'type_b': 3, 'cutoff': 2.0, 'bond_type': 3},   #Si-O
                    {'type_a': 2, 'type_b': 5, 'cutoff': 1.8, 'bond_type': 4},   #Si-Oh
                ]
                
                # Create bonds
                data.add_bonds_with_rules(bonding_rules)
                
                # Save result
                data.write_data_file("Output.data")
                print("Bond creation complete!")
            
            except Exception as e:
                print(f"Error: {str(e)}")
                print("Make sure:")
                print("1. Your input file exists and is accessible")
                print("2. The file follows standard LAMMPS data format")
                print("3. The atom types in bonding rules exist in your system")


        # ## Addition of angles
        # 
        # ### 4. Si - O -Si
        # 


        import re

        def find_and_add_angles(data_file, angle_definitions):
            print(f"\nProcessing file: {data_file}")
            
            with open(data_file, 'r') as f:
                lines = [line.rstrip('\n') for line in f]

            # Find section indices
            sections = {}
            for i, line in enumerate(lines):
                if re.match(r'^Atoms\b', line.strip()):
                    sections['Atoms'] = i
                elif re.match(r'^Bonds\b', line.strip()):
                    sections['Bonds'] = i
                elif re.match(r'^Angles\b', line.strip()):
                    sections['Angles'] = i
                elif re.match(r'^Masses\b', line.strip()):
                    sections['Masses'] = i

            # Parse atoms
            atoms = {}
            if 'Atoms' in sections:
                atoms_start = sections['Atoms'] + 2
                atoms_end = min([i for sec, i in sections.items() if i > sections['Atoms']], default=len(lines))
                for line in lines[atoms_start:atoms_end]:
                    if not line.strip():
                        continue
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 3:
                        try:
                            atom_id = int(parts[0])
                            atom_type = int(parts[2])
                            atoms[atom_id] = atom_type
                        except ValueError:
                            continue

            # Parse bonds
            bonds = []
            if 'Bonds' in sections:
                bonds_start = sections['Bonds'] + 2
                bonds_end = min([i for sec, i in sections.items() if i > sections['Bonds']], default=len(lines))
                for line in lines[bonds_start:bonds_end]:
                    if not line.strip():
                        continue
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 4:
                        try:
                            bond_type = int(parts[1])
                            atom1 = int(parts[2])
                            atom2 = int(parts[3])
                            bonds.append((atom1, atom2, bond_type))
                        except ValueError:
                            continue

            print(f"\nFound {len(atoms)} atoms")
            print(f"Found {len(bonds)} bonds")
            print(f"Atom types: {sorted(set(atoms.values()))}")
            print(f"Bond types: {sorted(set(b[2] for b in bonds))}")

            if not atoms or not bonds:
                print("\nERROR: No atoms or bonds found - cannot proceed")
                return

            # Build neighbor dictionary
            neighbors = {}
            for a1, a2, btype in bonds:
                neighbors.setdefault(a1, []).append((a2, btype))
                neighbors.setdefault(a2, []).append((a1, btype))

            all_angles = set()
            for a_type, b_type, c_type, angle_type, bond_type_ab, bond_type_bc in angle_definitions:
                print(f"\nSearching for angle pattern: {a_type}-{b_type}-{c_type} (type {angle_type})")
                matches = 0
                central_atoms = [aid for aid, atype in atoms.items() if atype == b_type]
                for b_atom in central_atoms:
                    if b_atom not in neighbors:
                        continue
                    for a_atom, ab_btype in neighbors[b_atom]:
                        if atoms.get(a_atom) != a_type:
                            continue
                        if bond_type_ab is not None and ab_btype != bond_type_ab:
                            continue
                        for c_atom, bc_btype in neighbors[b_atom]:
                            if c_atom == a_atom:
                                continue
                            if atoms.get(c_atom) != c_type:
                                continue
                            if bond_type_bc is not None and bc_btype != bond_type_bc:
                                continue
                            angle_key = tuple(sorted((a_atom, c_atom))) + (b_atom,)
                            if (angle_type, angle_key) not in all_angles:
                                all_angles.add((angle_type, angle_key))
                                matches += 1
                print(f"Found {matches} matches for this pattern")

            if not all_angles:
                print("\nERROR: No angles found matching your definitions")
                return

            # Prepare existing angles
            existing_angle_lines = []
            existing_angle_types = set()
            next_angle_id = 1

            if 'Angles' in sections:
                angles_start = sections['Angles'] + 2
                angles_end = angles_start
                while angles_end < len(lines) and lines[angles_end].strip():
                    angles_end += 1
                for line in lines[angles_start:angles_end]:
                    existing_angle_lines.append(line.strip())
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 2:
                        try:
                            existing_angle_types.add(int(parts[1]))
                            angle_id = int(parts[0])
                            next_angle_id = max(next_angle_id, angle_id + 1)
                        except ValueError:
                            pass
                # Remove old Angles section
                lines = lines[:sections['Angles']] + lines[angles_end:]
            else:
                sections['Angles'] = None  # To mark we are adding it fresh

            # Add new angles
            new_angle_lines = []
            sorted_angles = sorted(all_angles, key=lambda x: (x[0], x[1]))
            for angle_type, (a, c, b) in sorted_angles:
                new_angle_lines.append(f"{next_angle_id} {angle_type} {a} {b} {c}")
                existing_angle_types.add(angle_type)
                next_angle_id += 1

            final_angle_lines = ["Angles", ""] + existing_angle_lines + new_angle_lines

            # Insert Angles section
            insert_pos = sections['Angles'] if sections['Angles'] is not None else sections.get('Masses', len(lines))
            lines = lines[:insert_pos] + final_angle_lines + [""] + lines[insert_pos:]

            total_angles = len(existing_angle_lines) + len(new_angle_lines)
            total_angle_types = len(existing_angle_types)

            # Update header
            updated_header = []
            header_updated = {"angles": False, "angle types": False}
            for line in lines:
                if not header_updated["angles"] and re.match(r'^\s*\d+\s+angles\b', line):
                    updated_header.append(f"{total_angles} angles")
                    header_updated["angles"] = True
                elif not header_updated["angle types"] and re.match(r'^\s*\d+\s+angle types\b', line):
                    updated_header.append(f"{total_angle_types} angle types")
                    header_updated["angle types"] = True
                else:
                    updated_header.append(line)

            if not header_updated["angles"] or not header_updated["angle types"]:
                for i, line in enumerate(updated_header):
                    if re.match(r'^\s*\d+\s+atoms\b', line):
                        if not header_updated["angles"]:
                            updated_header.insert(i + 1, f"{total_angles} angles")
                            header_updated["angles"] = True
                        if not header_updated["angle types"]:
                            updated_header.insert(i + 2, f"{total_angle_types} angle types")
                            header_updated["angle types"] = True
                        break

            output_file = data_file
            with open(output_file, 'w') as f:
                f.write("\n".join(updated_header))
                f.write("\n")

            print(f"\nSUCCESS: Total {total_angles} angles")
            print(f"Total {total_angle_types} angle types")
            print(f"Output written to {output_file}")

        if __name__ == "__main__":
            data_file = "Output.data"
            angle_definitions = [
                (2, 3, 2, 4, None, None),      #Si-O-Si
                #(2, 3, 2, 5, None, None),
            ]
            find_and_add_angles(data_file, angle_definitions)



        # ## Differentiating Ohs from all Oh
        # 


        import numpy as np
        from collections import defaultdict

        class LAMMPSDataFile:
            def __init__(self, filename):
                self.filename = filename
                self.headers = {}
                self.atoms = []
                self.masses = []
                self.bonds = []
                self.angles = []
                self.dihedrals = []
                self.impropers = []
                self.atom_types = 0
                self.bond_types = 0
                self.angle_types = 0
                self.dihedral_types = 0
                self.improper_types = 0
                self.xlo = self.xhi = self.ylo = self.yhi = self.zlo = self.zhi = 0.0
                self.xy = self.xz = self.yz = 0.0
                self.box = np.zeros((3, 3))
                self.inv_box = None

                self._read_data_file()
                self._setup_box_vectors()

            def _parse_header(self, line):
                """Parse header lines from LAMMPS data file"""
                if 'atoms' in line:
                    self.headers['atoms'] = int(line.split()[0])
                elif 'bonds' in line:
                    self.headers['bonds'] = int(line.split()[0])
                elif 'angles' in line:
                    self.headers['angles'] = int(line.split()[0])
                elif 'atom types' in line:
                    self.atom_types = int(line.split()[0])
                elif 'bond types' in line:
                    self.bond_types = int(line.split()[0])
                elif 'angle types' in line:
                    self.angle_types = int(line.split()[0])
                elif 'xlo xhi' in line:
                    self.xlo, self.xhi = map(float, line.split()[:2])
                elif 'ylo yhi' in line:
                    self.ylo, self.yhi = map(float, line.split()[:2])
                elif 'zlo zhi' in line:
                    self.zlo, self.zhi = map(float, line.split()[:2])
                elif 'xy xz yz' in line:
                    self.xy, self.xz, self.yz = map(float, line.split()[:3])

            def _parse_section(self, section, line):
                """Parse data sections from LAMMPS data file"""
                if not line or not line[0].isdigit():
                    return

                parts = line.split()
                if section == 'Atoms':
                    self.atoms.append({
                        'id': int(parts[0]),
                        'mol': int(parts[1]),
                        'type': int(parts[2]),
                        'charge': float(parts[3]),
                        'x': float(parts[4]),
                        'y': float(parts[5]),
                        'z': float(parts[6])
                    })
                elif section == 'Bonds':
                    self.bonds.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3])
                    })
                elif section == 'Angles':
                    self.angles.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3]),
                        'atom3': int(parts[4])
                    })
                elif section == 'Masses':
                    self.masses.append({
                        'type': int(parts[0]),
                        'mass': float(parts[1])
                    })

            def _read_data_file(self):
                """Read LAMMPS data file and parse sections"""
                try:
                    with open(self.filename, 'r') as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    raise FileNotFoundError(f"Could not find file: {self.filename}")

                section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Section headers
                    if line.startswith('Atoms'):
                        section = 'Atoms'
                        continue
                    elif line.startswith('Bonds'):
                        section = 'Bonds'
                        continue
                    elif line.startswith('Masses'):
                        section = 'Masses'
                        continue
                    elif line.startswith('Angles'):
                        section = 'Angles'
                        continue

                    # Parse content
                    if section:
                        self._parse_section(section, line)
                    else:
                        self._parse_header(line)

            def _setup_box_vectors(self):
                """Initialize triclinic box vectors and inverse"""
                self.box[0][0] = self.xhi - self.xlo
                self.box[1][1] = self.yhi - self.ylo
                self.box[2][2] = self.zhi - self.zlo
                self.box[1][0] = self.xy
                self.box[2][0] = self.xz
                self.box[2][1] = self.yz
                self.inv_box = np.linalg.inv(self.box)

            def differentiate_oh_groups(self, si_type, oh_type, bond_type_x):
                """
                Differentiate OH groups bonded to Silicon by assigning a new atom type.
                
                Args:
                    si_type (int): Atom type of Silicon.
                    oh_type (int): Original atom type of OH.
                    bond_type_x (int): Bond type representing Si-OH bonds.
                Returns:
                    new_oh_type (int): The new atom type assigned to bonded OH groups.
                """
                # Step 1: Find the current maximum atom type
                max_atom_type = max(atom['type'] for atom in self.atoms)
                new_oh_type = max_atom_type + 1

                # Step 2: Find all OH atoms bonded to Silicon
                oh_bonded_to_si = set()
                
                for bond in self.bonds:
                    if bond['type'] == bond_type_x:
                        atom1 = next(atom for atom in self.atoms if atom['id'] == bond['atom1'])
                        atom2 = next(atom for atom in self.atoms if atom['id'] == bond['atom2'])
                        
                        # Check which atom is Si and which is OH
                        if atom1['type'] == si_type and atom2['type'] == oh_type:
                            oh_bonded_to_si.add(atom2['id'])
                        elif atom2['type'] == si_type and atom1['type'] == oh_type:
                            oh_bonded_to_si.add(atom1['id'])

                # Step 3: Modify the OH atom types
                for atom in self.atoms:
                    if atom['type'] == oh_type and atom['id'] in oh_bonded_to_si:
                        atom['type'] = new_oh_type

                # Step 4: Update atom types count
                self.atom_types = new_oh_type

                # Step 5: Add mass entry for the new type (if masses exist)
                if self.masses:
                    original_oh_mass = next(mass['mass'] for mass in self.masses if mass['type'] == oh_type)
                    self.masses.append({'type': new_oh_type, 'mass': original_oh_mass})

                print(f"Assigned new type {new_oh_type} to {len(oh_bonded_to_si)} OH atoms bonded to Si")
                return new_oh_type

            def write_data_file(self, output_filename):
                """Write updated LAMMPS data file"""
                with open(output_filename, 'w') as f:
                    # Headers
                    f.write("LAMMPS data file - Differentiated OH Groups\n\n")
                    f.write(f"{len(self.atoms)} atoms\n")
                    f.write(f"{len(self.bonds)} bonds\n")
                    f.write(f"{len(self.angles)} angles\n")
                    f.write(f"{self.atom_types} atom types\n")
                    f.write(f"{self.bond_types} bond types\n")
                    f.write(f"{self.angle_types} angle types\n\n")

                    # Box
                    f.write(f"{self.xlo:.6f} {self.xhi:.6f} xlo xhi\n")
                    f.write(f"{self.ylo:.6f} {self.yhi:.6f} ylo yhi\n")
                    f.write(f"{self.zlo:.6f} {self.zhi:.6f} zlo zhi\n")
                    if any([self.xy, self.xz, self.yz]):
                        f.write(f"{self.xy:.6f} {self.xz:.6f} {self.yz:.6f} xy xz yz\n\n")
                    else:
                        f.write("\n")

                    # Masses (if present)
                    if self.masses:
                        f.write("Masses\n\n")
                        for mass in sorted(self.masses, key=lambda x: x['type']):
                            f.write(f"{mass['type']} {mass['mass']:.4f}\n")
                        f.write("\n")

                    # Atoms
                    f.write("Atoms # full\n\n")
                    for atom in sorted(self.atoms, key=lambda x: x['id']):
                        f.write(f"{atom['id']} {atom['mol']} {atom['type']} {atom['charge']:.6f} "
                            f"{atom['x']:.6f} {atom['y']:.6f} {atom['z']:.6f}\n")

                    # Bonds
                    if self.bonds:
                        f.write("\nBonds\n\n")
                        for bond in sorted(self.bonds, key=lambda x: x['id']):
                            f.write(f"{bond['id']} {bond['type']} {bond['atom1']} {bond['atom2']}\n")

                    # Angles
                    if self.angles:
                        f.write("\nAngles\n\n")
                        for angle in sorted(self.angles, key=lambda x: x['id']):
                            f.write(f"{angle['id']} {angle['type']} {angle['atom1']} {angle['atom2']} {angle['atom3']}\n")


        if __name__ == "__main__":
            try:
                # Example Usage
                data = LAMMPSDataFile("Output.data")

                # Define parameters
                si_type = 2       # Atom type of Silicon
                oh_type = 5       # Original atom type of OH
                bond_type_x = 4   # Bond type for Si-OH bonds

                # Differentiate OH groups (automatically assigns new type)
                new_oh_type = data.differentiate_oh_groups(si_type, oh_type, bond_type_x)

                # Save the modified data
                data.write_data_file("Output.data")
                print(f"OH differentiation complete! New OH type: {new_oh_type}")

            except Exception as e:
                print(f"Error: {str(e)}")
                print("Make sure:")
                print("1. Your input file exists and is accessible")
                print("2. The atom types and bond types are correctly specified")


        # ## Differentiating Ohs from all H


        import numpy as np
        from collections import defaultdict

        class LAMMPSDataFile:
            def __init__(self, filename):
                self.filename = filename
                self.headers = {}
                self.atoms = []
                self.masses = []
                self.bonds = []
                self.angles = []
                self.dihedrals = []
                self.impropers = []
                self.atom_types = 0
                self.bond_types = 0
                self.angle_types = 0
                self.dihedral_types = 0
                self.improper_types = 0
                self.xlo = self.xhi = self.ylo = self.yhi = self.zlo = self.zhi = 0.0
                self.xy = self.xz = self.yz = 0.0
                self.box = np.zeros((3, 3))
                self.inv_box = None

                self._read_data_file()
                self._setup_box_vectors()

            def _parse_header(self, line):
                """Parse header lines from LAMMPS data file"""
                if 'atoms' in line:
                    self.headers['atoms'] = int(line.split()[0])
                elif 'bonds' in line:
                    self.headers['bonds'] = int(line.split()[0])
                elif 'angles' in line:
                    self.headers['angles'] = int(line.split()[0])
                elif 'atom types' in line:
                    self.atom_types = int(line.split()[0])
                elif 'bond types' in line:
                    self.bond_types = int(line.split()[0])
                elif 'angle types' in line:
                    self.angle_types = int(line.split()[0])
                elif 'xlo xhi' in line:
                    self.xlo, self.xhi = map(float, line.split()[:2])
                elif 'ylo yhi' in line:
                    self.ylo, self.yhi = map(float, line.split()[:2])
                elif 'zlo zhi' in line:
                    self.zlo, self.zhi = map(float, line.split()[:2])
                elif 'xy xz yz' in line:
                    self.xy, self.xz, self.yz = map(float, line.split()[:3])

            def _parse_section(self, section, line):
                """Parse data sections from LAMMPS data file"""
                if not line or not line[0].isdigit():
                    return

                parts = line.split()
                if section == 'Atoms':
                    self.atoms.append({
                        'id': int(parts[0]),
                        'mol': int(parts[1]),
                        'type': int(parts[2]),
                        'charge': float(parts[3]),
                        'x': float(parts[4]),
                        'y': float(parts[5]),
                        'z': float(parts[6])
                    })
                elif section == 'Bonds':
                    self.bonds.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3])
                    })
                elif section == 'Angles':
                    self.angles.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3]),
                        'atom3': int(parts[4])
                    })
                elif section == 'Masses':
                    self.masses.append({
                        'type': int(parts[0]),
                        'mass': float(parts[1])
                    })

            def _read_data_file(self):
                """Read LAMMPS data file and parse sections"""
                try:
                    with open(self.filename, 'r') as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    raise FileNotFoundError(f"Could not find file: {self.filename}")

                section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Section headers
                    if line.startswith('Atoms'):
                        section = 'Atoms'
                        continue
                    elif line.startswith('Bonds'):
                        section = 'Bonds'
                        continue
                    elif line.startswith('Masses'):
                        section = 'Masses'
                        continue
                    elif line.startswith('Angles'):
                        section = 'Angles'
                        continue

                    # Parse content
                    if section:
                        self._parse_section(section, line)
                    else:
                        self._parse_header(line)

            def _setup_box_vectors(self):
                """Initialize triclinic box vectors and inverse"""
                self.box[0][0] = self.xhi - self.xlo
                self.box[1][1] = self.yhi - self.ylo
                self.box[2][2] = self.zhi - self.zlo
                self.box[1][0] = self.xy
                self.box[2][0] = self.xz
                self.box[2][1] = self.yz
                self.inv_box = np.linalg.inv(self.box)

            def differentiate_oh_groups(self, si_type, oh_type, bond_type_x, new_bond_type=None):
                """
                Differentiate OH groups bonded to Silicon and update bond types.
                
                Args:
                    si_type (int): Atom type of Silicon.
                    oh_type (int): Original atom type of OH.
                    bond_type_x (int): Original bond type for Si-OH bonds.
                    new_bond_type (int, optional): New bond type for Si-OH. If None, uses max_bond_type + 1.
                Returns:
                    new_oh_type (int): New atom type assigned to bonded OH groups.
                    new_bond_type (int): New bond type assigned to Si-OH bonds.
                """
                # Step 1: Assign new OH type (max_atom_type + 1)
                max_atom_type = max(atom['type'] for atom in self.atoms)
                new_oh_type = max_atom_type + 1
                self.atom_types = new_oh_type  #new change to test

                # Step 2: Assign new bond type (if not user-defined)
                if new_bond_type is None:
                    max_bond_type = max(bond['type'] for bond in self.bonds) if self.bonds else 0
                    new_bond_type = max_bond_type + 1
                self.bond_types = max(self.bond_types, new_bond_type)

                # Step 3: Find all OH atoms bonded to Silicon
                oh_bonded_to_si = set()
                bonds_to_update = []  # Stores bonds that need their type changed
                
                for bond in self.bonds:
                    if bond['type'] == bond_type_x:
                        atom1 = next(atom for atom in self.atoms if atom['id'] == bond['atom1'])
                        atom2 = next(atom for atom in self.atoms if atom['id'] == bond['atom2'])
                        
                        # Check which atom is Si and which is OH
                        if atom1['type'] == si_type and atom2['type'] == oh_type:
                            oh_bonded_to_si.add(atom2['id'])
                            bonds_to_update.append(bond)
                        elif atom2['type'] == si_type and atom1['type'] == oh_type:
                            oh_bonded_to_si.add(atom1['id'])
                            bonds_to_update.append(bond)

                # Step 4: Modify the OH atom types and bond types
                for atom in self.atoms:
                    if atom['type'] == oh_type and atom['id'] in oh_bonded_to_si:
                        atom['type'] = new_oh_type

                for bond in bonds_to_update:
                    bond['type'] = new_bond_type

                # Step 5: Add mass entry for the new type (if masses exist)
                if self.masses:
                    original_oh_mass = next(mass['mass'] for mass in self.masses if mass['type'] == oh_type)
                    self.masses.append({'type': new_oh_type, 'mass': original_oh_mass})

                print(
                    f"Modified {len(oh_bonded_to_si)} OH atoms (type {oh_type} -> {new_oh_type})\n"
                    f"Updated {len(bonds_to_update)} bonds (type {bond_type_x} -> {new_bond_type})"
                )
                return new_oh_type, new_bond_type


            def write_data_file(self, output_filename):
                """Write updated LAMMPS data file"""
                with open(output_filename, 'w') as f:
                    # Headers
                    f.write("LAMMPS data file - Differentiated OH Groups\n\n")
                    f.write(f"{len(self.atoms)} atoms\n")
                    f.write(f"{len(self.bonds)} bonds\n")
                    f.write(f"{len(self.angles)} angles\n")
                    f.write(f"{self.atom_types} atom types\n")
                    f.write(f"{self.bond_types} bond types\n")
                    f.write(f"{self.angle_types} angle types\n\n")

                    # Box
                    f.write(f"{self.xlo:.6f} {self.xhi:.6f} xlo xhi\n")
                    f.write(f"{self.ylo:.6f} {self.yhi:.6f} ylo yhi\n")
                    f.write(f"{self.zlo:.6f} {self.zhi:.6f} zlo zhi\n")
                    if any([self.xy, self.xz, self.yz]):
                        f.write(f"{self.xy:.6f} {self.xz:.6f} {self.yz:.6f} xy xz yz\n\n")
                    else:
                        f.write("\n")

                    # Masses (if present)
                    if self.masses:
                        f.write("Masses\n\n")
                        for mass in sorted(self.masses, key=lambda x: x['type']):
                            f.write(f"{mass['type']} {mass['mass']:.4f}\n")
                        f.write("\n")

                    # Atoms
                    f.write("Atoms # full\n\n")
                    for atom in sorted(self.atoms, key=lambda x: x['id']):
                        f.write(f"{atom['id']} {atom['mol']} {atom['type']} {atom['charge']:.6f} "
                            f"{atom['x']:.6f} {atom['y']:.6f} {atom['z']:.6f}\n")

                    # Bonds
                    if self.bonds:
                        f.write("\nBonds\n\n")
                        for bond in sorted(self.bonds, key=lambda x: x['id']):
                            f.write(f"{bond['id']} {bond['type']} {bond['atom1']} {bond['atom2']}\n")

                    # Angles
                    if self.angles:
                        f.write("\nAngles\n\n")
                        for angle in sorted(self.angles, key=lambda x: x['id']):
                            f.write(f"{angle['id']} {angle['type']} {angle['atom1']} {angle['atom2']} {angle['atom3']}\n")


        if __name__ == "__main__":
            try:
                # Example Usage
                data = LAMMPSDataFile("Output.data")

                # Define parameters
                si_type = 8       # Atom type of Silicon
                oh_type = 7       # Original atom type of OH
                bond_type_x = 1   # Original bond type for Si-OH bonds
                new_bond_type = 5 # User-defined new bond type (or None for auto-assign)

                # Differentiate OH groups and update bonds
                new_oh_type, new_bond_type = data.differentiate_oh_groups(
                    si_type, oh_type, bond_type_x, new_bond_type
                )

                # Save the modified data
                data.write_data_file("Output.data")
                print(
                    f"OH differentiation complete!\n"
                    f"New OH type: {new_oh_type}\n"
                    f"New bond type: {new_bond_type}"
                )

            except Exception as e:
                print(f"Error: {str(e)}")


        # ## Differentiating "Ob" and editing new assosiated bond and angles


        import numpy as np
        from collections import defaultdict

        class LAMMPSDataFile:
            def __init__(self, filename):
                self.filename = filename
                self.headers = {}
                self.atoms = []
                self.masses = []
                self.bonds = []
                self.angles = []
                self.dihedrals = []
                self.impropers = []
                self.atom_types = 0
                self.bond_types = 0
                self.angle_types = 0
                self.dihedral_types = 0
                self.improper_types = 0
                self.xlo = self.xhi = self.ylo = self.yhi = self.zlo = self.zhi = 0.0
                self.xy = self.xz = self.yz = 0.0
                self.box = np.zeros((3, 3))
                self.inv_box = None
                self._read_data_file()
                self._setup_box_vectors()

            def _parse_header(self, line):
                """Parse header lines from LAMMPS data file"""
                if 'atoms' in line:
                    self.headers['atoms'] = int(line.split()[0])
                elif 'bonds' in line:
                    self.headers['bonds'] = int(line.split()[0])
                elif 'angles' in line:
                    self.headers['angles'] = int(line.split()[0])
                elif 'atom types' in line:
                    self.atom_types = int(line.split()[0])
                elif 'bond types' in line:
                    self.bond_types = int(line.split()[0])
                elif 'angle types' in line:
                    self.angle_types = int(line.split()[0])
                elif 'xlo xhi' in line:
                    self.xlo, self.xhi = map(float, line.split()[:2])
                elif 'ylo yhi' in line:
                    self.ylo, self.yhi = map(float, line.split()[:2])
                elif 'zlo zhi' in line:
                    self.zlo, self.zhi = map(float, line.split()[:2])
                elif 'xy xz yz' in line:
                    self.xy, self.xz, self.yz = map(float, line.split()[:3])

            def _parse_section(self, section, line):
                """Parse data sections from LAMMPS data file"""
                if not line or not line[0].isdigit():
                    return

                parts = line.split()
                if section == 'Atoms':
                    self.atoms.append({
                        'id': int(parts[0]),
                        'mol': int(parts[1]),
                        'type': int(parts[2]),
                        'charge': float(parts[3]),
                        'x': float(parts[4]),
                        'y': float(parts[5]),
                        'z': float(parts[6])
                    })
                elif section == 'Bonds':
                    self.bonds.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3])
                    })
                elif section == 'Angles':
                    self.angles.append({
                        'id': int(parts[0]),
                        'type': int(parts[1]),
                        'atom1': int(parts[2]),
                        'atom2': int(parts[3]),
                        'atom3': int(parts[4])
                    })
                elif section == 'Masses':
                    self.masses.append({
                        'type': int(parts[0]),
                        'mass': float(parts[1])
                    })

            def _read_data_file(self):
                """Read LAMMPS data file and parse sections"""
                try:
                    with open(self.filename, 'r') as f:
                        lines = f.readlines()
                except FileNotFoundError:
                    raise FileNotFoundError(f"Could not find file: {self.filename}")

                section = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith('Atoms'):
                        section = 'Atoms'
                        continue
                    elif line.startswith('Bonds'):
                        section = 'Bonds'
                        continue
                    elif line.startswith('Masses'):
                        section = 'Masses'
                        continue
                    elif line.startswith('Angles'):
                        section = 'Angles'
                        continue
                    elif line.startswith('Dihedrals'):
                        section = 'Dihedrals'
                        continue

                    if section:
                        self._parse_section(section, line)
                    else:
                        self._parse_header(line)

            def _setup_box_vectors(self):
                """Initialize triclinic box vectors and inverse"""
                self.box[0][0] = self.xhi - self.xlo
                self.box[1][1] = self.yhi - self.ylo
                self.box[2][2] = self.zhi - self.zlo
                self.box[1][0] = self.xy
                self.box[2][0] = self.xz
                self.box[2][1] = self.yz
                self.inv_box = np.linalg.inv(self.box)

            def differentiate_bridging_oxygen(self, si_type, o_type, bridging_angle_type,
                                            si_o_bond_type, new_bond_type=None):
                """
                Identify bridging O in Si-O-Si and update bonds
                Returns:
                    new_o_type, new_bond_type
                """
                # Assign new atom type for bridging O
                new_o_type = max(atom['type'] for atom in self.atoms) + 1
                self.atom_types = new_o_type

                # Auto-assign new bond type
                new_bond_type = new_bond_type or max(bond['type'] for bond in self.bonds) + 1
                self.bond_types = max(self.bond_types, new_bond_type)

                # Find bridging O atoms (central in Si-O-Si)
                bridging_o_ids = {
                    angle['atom2'] for angle in self.angles 
                    if angle['type'] == bridging_angle_type
                    and all(self.atoms[a-1]['type'] == si_type for a in [angle['atom1'], angle['atom3']])
                    and self.atoms[angle['atom2']-1]['type'] == o_type
                }

                # Update atom types
                for atom in self.atoms:
                    if atom['id'] in bridging_o_ids:
                        atom['type'] = new_o_type

                # Update Si-O bonds involving bridging O
                updated_bonds = [
                    bond for bond in self.bonds
                    if bond['type'] == si_o_bond_type
                    and any(self.atoms[bond[f'atom{i}']-1]['type'] == new_o_type for i in [1, 2])
                ]
                for bond in updated_bonds:
                    bond['type'] = new_bond_type

                # Add mass for new O type
                if self.masses:
                    original_mass = next(m['mass'] for m in self.masses if m['type'] == o_type)
                    self.masses.append({'type': new_o_type, 'mass': original_mass})

                print(f"\nBridging oxygen modification:")
                print(f"- Created new O type: {new_o_type}")
                print(f"- Modified {len(bridging_o_ids)} bridging O atoms")
                print(f"- Updated {len(updated_bonds)} Si-O bonds to type {new_bond_type}")

                return new_o_type, new_bond_type

            def differentiate_angle_types(self, original_angle_type, type_patterns):
                """
                Split angles into subtypes based on atom type patterns
                Args:
                    type_patterns: {(type1, type2, type3): new_type}
                    Example: {(3,2,10):5, (10,2,10):6, (8,2,3):7, (8,2,10):8}
                """
                updated_counts = {pattern: 0 for pattern in type_patterns}
                
                for angle in self.angles:
                    if angle['type'] == original_angle_type:
                        types = tuple(self.atoms[a-1]['type'] for a in 
                                    [angle['atom1'], angle['atom2'], angle['atom3']])
                        
                        for pattern, new_type in type_patterns.items():
                            if types == pattern:
                                angle['type'] = new_type
                                updated_counts[pattern] += 1
                                break
                
                # Update angle_types count
                self.angle_types = max(max(type_patterns.values()), self.angle_types)
                
                print("\nAngle type differentiation:")
                for pattern, count in updated_counts.items():
                    print(f"Updated {count} angles {pattern} → type {type_patterns[pattern]}")

            def write_data_file(self, output_filename):
                """Write updated LAMMPS data file"""
                with open(output_filename, 'w') as f:
                    # Headers
                    f.write("LAMMPS data file - Modified\n\n")
                    f.write(f"{len(self.atoms)} atoms\n")
                    f.write(f"{len(self.bonds)} bonds\n")
                    f.write(f"{len(self.angles)} angles\n")
                    f.write(f"{self.atom_types} atom types\n")
                    f.write(f"{self.bond_types} bond types\n")
                    f.write(f"{self.angle_types} angle types\n\n")

                    # Box
                    f.write(f"{self.xlo:.6f} {self.xhi:.6f} xlo xhi\n")
                    f.write(f"{self.ylo:.6f} {self.yhi:.6f} ylo yhi\n")
                    f.write(f"{self.zlo:.6f} {self.zhi:.6f} zlo zhi\n")
                    if any([self.xy, self.xz, self.yz]):
                        f.write(f"{self.xy:.6f} {self.xz:.6f} {self.yz:.6f} xy xz yz\n\n")
                    else:
                        f.write("\n")

                    # Masses
                    if self.masses:
                        f.write("Masses\n\n")
                        for mass in sorted(self.masses, key=lambda x: x['type']):
                            f.write(f"{mass['type']} {mass['mass']:.4f}\n")
                        f.write("\n")

                    # Atoms
                    f.write("Atoms # full\n\n")
                    for atom in sorted(self.atoms, key=lambda x: x['id']):
                        f.write(f"{atom['id']} {atom['mol']} {atom['type']} {atom['charge']:.6f} "
                            f"{atom['x']:.6f} {atom['y']:.6f} {atom['z']:.6f}\n")

                    # Bonds
                    if self.bonds:
                        f.write("\nBonds\n\n")
                        for bond in sorted(self.bonds, key=lambda x: x['id']):
                            f.write(f"{bond['id']} {bond['type']} {bond['atom1']} {bond['atom2']}\n")

                    # Angles
                    if self.angles:
                        f.write("\nAngles\n\n")
                        for angle in sorted(self.angles, key=lambda x: x['id']):
                            f.write(f"{angle['id']} {angle['type']} {angle['atom1']} {angle['atom2']} {angle['atom3']}\n")


        if __name__ == "__main__":
            try:
                # Load data
                print("Processing LAMMPS data file...")
                data = LAMMPSDataFile("Output.data")
                
                # System parameters (MODIFY THESE)
                SI_TYPE = 2           # Silicon atom type
                O_TYPE = 3            # Original bridging oxygen type
                BRIDGING_ANGLE = 4    # Si-O-Si angle type 
                SI_O_BOND = 3         # Original Si-O bond type
                O_SI_O_ANGLE = 2      # Original O-Si-O angle type

                # Step 1: Process bridging oxygen
                new_o_type, new_bond_type = data.differentiate_bridging_oxygen(
                    si_type=SI_TYPE,
                    o_type=O_TYPE,
                    bridging_angle_type=BRIDGING_ANGLE,
                    si_o_bond_type=SI_O_BOND
                )

                # Step 2: Split angle types
                angle_type_mapping = {
                    (10, 2, 3): 5,    # O-Si-BridgingO
                    (3, 2, 10):5,
                    (10, 2, 10): 6,    # BridgingO-Si-BridgingO
                    (8, 2, 3): 7,      # Type8-Si-O
                    (3, 2, 8): 7,
                    (8, 2, 10): 8,      # Type8-Si-BridgingO
                    (10, 2, 8): 8
                }
                data.differentiate_angle_types(
                    original_angle_type=O_SI_O_ANGLE,
                    type_patterns=angle_type_mapping
                )

                # Save results
                output_file = f"IFF/{file_name[:-5]}_IFF.data"
                data.write_data_file(output_file)
                print(f"\nSuccess! Output written to {output_file}")

            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Debugging tips:")
                print("1. Verify atom/bond/angle types match your data file")
                print("2. Check input file exists and is accessible")
