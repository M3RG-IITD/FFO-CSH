#!/usr/bin/env python3

import csv
import json
import re
import shutil
from pathlib import Path


##############################################################################
# Utilities
##############################################################################

def timestep_range(dumpfile):
    """Return first timestep, last timestep, number of frames."""
    first = None
    last = None
    frames = 0

    with open(dumpfile) as f:
        while True:
            line = f.readline()
            if not line:
                break

            if line.startswith("ITEM: TIMESTEP"):
                ts = int(f.readline())
                if first is None:
                    first = ts
                last = ts
                frames += 1

    return first, last, frames


##############################################################################
# Dump merging
##############################################################################

def merge_dump(files, outfile):

    last_written = -1
    total_frames = 0

    with open(outfile, "w") as out:

        for dump in files:

            kept = 0
            skipped = 0

            with open(dump) as f:

                while True:

                    line = f.readline()

                    if not line:
                        break

                    if not line.startswith("ITEM: TIMESTEP"):
                        continue

                    ts = int(f.readline())

                    frame = [line, str(ts) + "\n"]

                    # read rest of frame
                    while True:
                        pos = f.tell()
                        l = f.readline()

                        if not l:
                            break

                        if l.startswith("ITEM: TIMESTEP"):
                            f.seek(pos)
                            break

                        frame.append(l)

                    if ts <= last_written:
                        skipped += 1
                        continue

                    out.writelines(frame)

                    last_written = ts
                    kept += 1
                    total_frames += 1

            print(f"    {dump.name:40s} kept={kept:5d} skipped={skipped:4d}")

    return total_frames


##############################################################################
# Merge log.lammps
##############################################################################

def merge_logs(logfiles, outfile):

    written_steps = set()

    with open(outfile, "w") as out:

        first = True

        for log in logfiles:

            thermo = False

            with open(log) as f:

                for line in f:

                    if first:
                        out.write(line)

                    if line.startswith("Step"):
                        thermo = True
                        if not first:
                            continue

                    elif line.startswith("Loop time"):
                        thermo = False
                        continue

                    if thermo and not line.startswith("Step"):

                        cols = line.split()

                        if len(cols) == 0:
                            continue

                        try:
                            step = int(cols[0])
                        except:
                            continue

                        if step in written_steps:
                            continue

                        written_steps.add(step)

                        if not first:
                            out.write(line)

            first = False


##############################################################################
# Copy useful files
##############################################################################

def copy_latest(simdir, analysis):

    candidates = []

    for ext in ["*.restart", "*.data"]:

        for f in simdir.rglob(ext):
            candidates.append(f)

    latest = {}

    for f in candidates:

        name = f.name

        m = re.search(r'(\d+)', name)

        key = f.suffix

        if key not in latest:
            latest[key] = f
        else:

            if f.stat().st_mtime > latest[key].stat().st_mtime:
                latest[key] = f

    for f in latest.values():
        shutil.copy2(f, analysis/f.name)

    inp = analysis/"input_files"
    inp.mkdir(exist_ok=True)

    for ext in ["*.in", "*.sh", "*.params"]:
        for f in simdir.glob(ext):
            shutil.copy2(f, inp/f.name)


##############################################################################
# Main
##############################################################################

root = Path(".")
import sys

if len(sys.argv) > 1:
    root = Path(sys.argv[1])

summary = []

for sim in sorted(root.rglob("*")):

    if not sim.is_dir():
        continue

    dumpfiles = []

    logfiles = []

    for f in sim.glob("*.lammpstrj"):
        dumpfiles.append(f)

    for r in sorted(sim.glob("restart*")):
        dumpfiles.extend(sorted(r.glob("*.lammpstrj")))

    if len(dumpfiles) == 0:
        continue

    for f in sim.glob("log.lammps"):
        logfiles.append(f)

    for r in sorted(sim.glob("restart*")):
        logfiles.extend(sorted(r.glob("log.lammps")))

    print("="*70)
    print(sim)
    print("="*70)

    analysis = sim/"analysis"
    analysis.mkdir(exist_ok=True)

    metadata = []

    for d in dumpfiles:

        first,last,n=timestep_range(d)

        metadata.append(dict(
            file=str(d.relative_to(sim)),
            first=first,
            last=last,
            frames=n
        ))

        print(f"{d.name:40s} {first:10d} -> {last:10d}  frames={n}")

    print()

    merged = analysis/"merged.lammpstrj"

    frames = merge_dump(dumpfiles, merged)

    if logfiles:
        merge_logs(logfiles, analysis/"merged.log")

    copy_latest(sim,analysis)

    with open(analysis/"metadata.json","w") as f:
        json.dump(metadata,f,indent=4)

    with open(analysis/"merge_report.txt","w") as f:

        f.write(f"Simulation : {sim}\n\n")

        for m in metadata:
            f.write(json.dumps(m)+"\n")

    summary.append([
        str(sim.relative_to(root)),
        metadata[0]["first"],
        metadata[-1]["last"],
        frames,
        len(dumpfiles)-1
    ])

print("\nWriting summary.csv\n")

with open(root/"summary.csv","w",newline="") as f:

    writer=csv.writer(f)

    writer.writerow([
        "Simulation",
        "FirstStep",
        "LastStep",
        "Frames",
        "RestartSegments"
    ])

    writer.writerows(summary)

print("Done.")