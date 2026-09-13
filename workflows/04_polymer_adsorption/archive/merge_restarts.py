#!/usr/bin/env python3
"""
Merge LAMMPS restart trajectories and log files into a single
continuous trajectory per system. Handles overlapping frames at
restart boundaries by keeping only the first occurrence of each
timestep.

Writes everything to a NEW directory — originals are never touched.

Usage:
    python merge_restarts.py

Edit SRC and DST below, then run.
"""
import os
import sys
import shutil
from pathlib import Path

max_steps =  27_00_0000  # maximum number of steps to keep in merged trajectory

# ============================================================
#  CONFIGURATION — edit these two paths
# ============================================================

SRC = Path(
    ""
    "MDSetup/example/mechanical_properties/"
    "0_CSH_transfer/CSH_surface/try/"
    "2_combined_new/0_run13_pcff"
)

DST = Path(
    ""
    "MDSetup/example/mechanical_properties/"
    "0_CSH_transfer/CSH_surface/try/"
    "2_combined_new/0_run13_pcff_merged_fix_max_steps"
)

# Define what to merge for each system.
# Each entry: (sub_directory, list_of_traj_files, list_of_log_files,
#              merged_traj_name, data_file_to_copy)

MERGE_JOBS = {
    # ── S1 systems (CSH + PCE + water) ──
    "1_1-12E/S1": {
        "trajs": [
            "S1_1_1_15_dump.lammpstrj",
            "restart1/S1_1_1_15_ext_dump.lammpstrj",
            "restart2/S1_1_1_15_ext_dump.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart1/log.lammps",
            "restart2/log.lammps",
        ],
        "merged_traj": "S1_1_1_15_dump_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S1_1_1_15_Relaxed.data"],
    },
    "2_1-8E/S1": {
        "trajs": [
            "S1_2_1_15_dump.lammpstrj",
            "restart1/S1_2_1_15_ext_dump.lammpstrj",
            "restart2/S1_2_1_15_ext_dump.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart1/log.lammps",
            "restart2/log.lammps",
        ],
        "merged_traj": "S1_2_1_15_dump_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S1_2_1_15_Relaxed.data"],
    },
    "3_1-6E/S1": {
        "trajs": [
            "S1_3_1_15_dump.lammpstrj",
            "restart1/S1_3_1_15_ext_dump.lammpstrj",
            "restart2/S1_3_1_15_ext_dump.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart1/log.lammps",
            "restart2/log.lammps",
        ],
        "merged_traj": "S1_3_1_15_dump_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S1_3_1_15_Relaxed.data"],
    },

    # ── S2 systems (PCE + water) ──
    "1_1-12E/S2": {
        "trajs": [
            "S2_dump_1_1_12E.lammpstrj",
            "restart/S2_dump_1_1_12E_ext.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart/log.lammps",
        ],
        "merged_traj": "S2_dump_1_1_12E_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S2_1_1_15_Relaxed.data"],
    },
    "2_1-8E/S2": {
        "trajs": [
            "S2_dump_2_1_8E.lammpstrj",
            "restart/S2_dump_2_1_12E_ext.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart/log.lammps",
        ],
        "merged_traj": "S2_dump_2_1_8E_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S2_2_1_15_Relaxed.data"],
    },
    "3_1-6E/S2": {
        "trajs": [
            "S2_dump_3_1_6E.lammpstrj",
            "restart/S2_dump_3_1_15_ext.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart/log.lammps",
        ],
        "merged_traj": "S2_dump_3_1_6E_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S2_3_1_15_Relaxed.data"],
    },

    # ── S3 (CSH + water, shared) ──
    "S3": {
        "trajs": [
            "3_dump_csh_water.lammpstrj",
            "restart/3_dump_csh_water_ext.lammpstrj",
        ],
        "logs": [
            "log.lammps",
            "restart/log.lammps",
        ],
        "merged_traj": "3_dump_csh_water_merged.lammpstrj",
        "merged_log": "log_merged.lammps",
        "copy_files": ["S3_csh_water.data"],
    },
}


# ============================================================
#  TRAJECTORY MERGER
# ============================================================

def merge_lammpstrj(traj_files, output_path):
    """
    Merge multiple LAMMPS dump files into one, removing duplicate
    frames at restart boundaries.

    A LAMMPS dump frame looks like:
        ITEM: TIMESTEP
        <step>
        ITEM: NUMBER OF ATOMS
        ...
        ITEM: ATOMS ...
        <atom lines>

    Strategy: stream through each file, buffer one frame at a time,
    write only if timestep > last_written_timestep.
    """
    last_step = -1
    frames_written = 0
    frames_skipped = 0

    with open(output_path, 'w') as out:
        for traj_file in traj_files:
            print(f"    Reading: {traj_file.name}")
            frame_lines = []
            current_step = None
            in_frame = False

            with open(traj_file, 'r') as f:
                for line in f:
                    if line.startswith("ITEM: TIMESTEP"):
                        # Flush previous frame if it's new
                        if frame_lines and current_step is not None:

                            if current_step > max_steps:
                                # Finished; later files only contain larger timesteps.
                                print(f"    Reached max_steps ({max_steps:,}). Stopping.")
                                return frames_written, last_step

                            if current_step > last_step:
                                out.writelines(frame_lines)
                                last_step = current_step
                                frames_written += 1
                            else:
                                frames_skipped += 1

                        frame_lines = [line]
                        in_frame = True
                        current_step = None

                    elif in_frame and current_step is None and len(frame_lines) == 1:
                        # This line is the timestep value
                        current_step = int(line.strip())
                        frame_lines.append(line)

                    else:
                        frame_lines.append(line)

                # Flush last frame in file

                if frame_lines and current_step is not None:
                    if current_step > max_steps:
                        print(f"    Reached max_steps ({max_steps:,}). Stopping.")
                        return frames_written, last_step
                    if current_step > last_step:
                        out.writelines(frame_lines)
                        last_step = current_step
                        frames_written += 1
                    else:
                        frames_skipped += 1
                
    print(f"    → {frames_written} frames written, "
          f"{frames_skipped} duplicates skipped, "
          f"last step = {last_step}")
    return frames_written, last_step


# ============================================================
#  LOG FILE MERGER
# ============================================================

def merge_logs(log_files, output_path):
    """
    Merge multiple LAMMPS log files, deduplicating thermo data.

    Strategy:
    - Keep ALL non-thermo content from the first log (LAMMPS header,
      input script echo, etc.)
    - For thermo blocks (between "Step ..." header and "Loop time"):
      skip rows with step ≤ last_written_step
    - From restart logs, only extract thermo data blocks (skip their
      headers/input echo since that's redundant)
    """
    last_step = -1
    total_rows = 0

    with open(output_path, 'w') as out:
        for i, log_file in enumerate(log_files):
            print(f"    Reading: {log_file.name}")
            rows_this_file = 0

            with open(log_file, 'r') as f:
                lines = f.readlines()

            j = 0
            while j < len(lines):
                line = lines[j]

                # Detect thermo header
                if line.strip().startswith("Step") and any(
                    kw in line for kw in ["PotEng", "TotEng", "Temp", "Press", "pe"]
                ):
                    # Write header (from first file, or if format changes)
                    if i == 0 or rows_this_file == 0:
                        out.write(line)
                    header_cols = line.split()
                    j += 1

                    # Process data rows
                    while j < len(lines):
                        parts = lines[j].split()
                        if len(parts) != len(header_cols):
                            # End of thermo block
                            if i == 0:
                                out.write(lines[j])  # "Loop time..." line
                            break
                        try:
                            step = int(parts[0])
                            if step > max_steps:
                                print(f"    Reached max_steps ({max_steps:,}) in log.")
                                return total_rows + rows_this_file, last_step
                            if step > last_step:
                                out.write(lines[j])
                                last_step = step
                                rows_this_file += 1
                        except ValueError:
                            if i == 0:
                                out.write(lines[j])
                            break
                        j += 1
                else:
                    # Non-thermo content: keep from first log only
                    if i == 0:
                        out.write(line)
                j += 1

            total_rows += rows_this_file
            print(f"      {rows_this_file} thermo rows added")

    print(f"    → {total_rows} total thermo rows, last step = {last_step}")
    return total_rows, last_step


# ============================================================
#  MAIN
# ============================================================

def main():
    print(f"\nSource: {SRC}")
    print(f"Destination: {DST}\n")

    if not SRC.exists():
        print(f"ERROR: Source directory not found: {SRC}")
        sys.exit(1)

    # Safety check
    if DST.exists():
        print(f"WARNING: Destination already exists: {DST}")
        resp = input("Continue and overwrite? [y/N] ").strip().lower()
        if resp != 'y':
            print("Aborted.")
            sys.exit(0)

    summary = []

    for subdir, job in MERGE_JOBS.items():
        print(f"\n{'='*60}")
        print(f"  Merging: {subdir}")
        print(f"{'='*60}")

        src_dir = SRC / subdir
        dst_dir = DST / subdir
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Check all source files exist
        missing = []
        for t in job["trajs"]:
            if not (src_dir / t).exists():
                missing.append(t)
        for l in job["logs"]:
            if not (src_dir / l).exists():
                missing.append(l)
        if missing:
            print(f"  WARNING: Missing files, skipping {subdir}:")
            for m in missing:
                print(f"    - {m}")
            continue

        # Merge trajectories
        print(f"\n  Merging trajectories → {job['merged_traj']}")
        traj_files = [src_dir / t for t in job["trajs"]]
        n_frames, last_traj_step = merge_lammpstrj(
            traj_files, dst_dir / job["merged_traj"]
        )

        # Merge logs
        print(f"\n  Merging logs → {job['merged_log']}")
        log_files = [src_dir / l for l in job["logs"]]
        n_rows, last_log_step = merge_logs(
            log_files, dst_dir / job["merged_log"]
        )

        # Copy data files
        for cf in job.get("copy_files", []):
            src_file = src_dir / cf
            if src_file.exists():
                shutil.copy2(src_file, dst_dir / cf)
                print(f"\n  Copied: {cf}")
            else:
                print(f"\n  WARNING: {cf} not found, skipping copy")

        summary.append({
            "system": subdir,
            "traj_frames": n_frames,
            "last_traj_step": last_traj_step,
            "thermo_rows": n_rows,
            "last_log_step": last_log_step,
        })

    # Print summary
    print(f"\n\n{'='*70}")
    print("  MERGE SUMMARY")
    print(f"{'='*70}")
    print(f"  {'System':<20} {'Frames':>8} {'Last traj step':>16} "
          f"{'Thermo rows':>12} {'Last log step':>16}")
    print(f"  {'-'*20} {'-'*8} {'-'*16} {'-'*12} {'-'*16}")
    for s in summary:
        print(f"  {s['system']:<20} {s['traj_frames']:>8} "
              f"{s['last_traj_step']:>16} {s['thermo_rows']:>12} "
              f"{s['last_log_step']:>16}")

    # Generate updated config snippet
    print(f"\n\n{'='*70}")
    print("  UPDATED CONFIG.PY PATHS")
    print(f"{'='*70}")
    print(f"""
# After merging, update config.py:

RUN = "0_run13_pcff_merged_fix_max_steps"

SYSTEMS = {{
    "1:1": {{
        "S1_data": BASE / RUN / "1_1-12E/S1/S1_1_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "1_1-12E/S1/S1_1_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "1_1-12E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "1_1-12E/S2/S2_1_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "1_1-12E/S2/S2_dump_1_1_12E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "1_1-12E/S2/log_merged.lammps",
        "n_side_chains": 12,
        "CE_ratio": "1:1",
    }},
    "2:1": {{
        "S1_data": BASE / RUN / "2_1-8E/S1/S1_2_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "2_1-8E/S1/S1_2_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "2_1-8E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "2_1-8E/S2/S2_2_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "2_1-8E/S2/S2_dump_2_1_8E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "2_1-8E/S2/log_merged.lammps",
        "n_side_chains": 8,
        "CE_ratio": "2:1",
    }},
    "3:1": {{
        "S1_data": BASE / RUN / "3_1-6E/S1/S1_3_1_15_Relaxed.data",
        "S1_traj": BASE / RUN / "3_1-6E/S1/S1_3_1_15_dump_merged.lammpstrj",
        "S1_log":  BASE / RUN / "3_1-6E/S1/log_merged.lammps",
        "S2_data": BASE / RUN / "3_1-6E/S2/S2_3_1_15_Relaxed.data",
        "S2_traj": BASE / RUN / "3_1-6E/S2/S2_dump_3_1_6E_merged.lammpstrj",
        "S2_log":  BASE / RUN / "3_1-6E/S2/log_merged.lammps",
        "n_side_chains": 6,
        "CE_ratio": "3:1",
    }},
}}

S3_CONFIG = {{
    "data": BASE / RUN / "S3/S3_csh_water.data",
    "traj": BASE / RUN / "S3/3_dump_csh_water_merged.lammpstrj",
    "log":  BASE / RUN / "S3/log_merged.lammps",
}}

# With ~25.6M steps total and 7M equil:
EQUIL_STEPS = 7_000_000
# Total frames ≈ 25610000/10000 ≈ 2561, equil = 700
# Production ≈ 1861 frames ≈ 18.6 ns
PRODUCTION_LAST_NS = 18
""")

    print(f"\nAll merged files written to: {DST}")
    print("Original files in 0_run13_pcff are UNTOUCHED.\n")


if __name__ == "__main__":
    main()