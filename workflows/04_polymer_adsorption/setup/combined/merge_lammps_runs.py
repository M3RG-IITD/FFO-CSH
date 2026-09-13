#!/usr/bin/env python3
"""
merge_lammps_runs.py

Safely merge LAMMPS trajectories and logs from restarted simulations.

Features
--------
- NEVER modifies the original simulation directory.
- Creates a separate output directory (default: <input>_analysis).
- Merges *.lammpstrj while removing overlapping timesteps.
- Merges log.lammps thermo tables while removing duplicate steps.
- Copies latest .restart and .data files.
- Copies *.in, *.sh and *.params files.
- Creates metadata.json, merge_report.txt and summary.csv.

Usage
-----
python merge_lammps_runs.py 0_run13_pcff
python merge_lammps_runs.py 0_run13_pcff --output merged_results
"""

import argparse
import csv
import json
import shutil
from pathlib import Path

def frame_iterator(path):
    with open(path,"r") as f:
        while True:
            line=f.readline()
            if not line:
                break
            if not line.startswith("ITEM: TIMESTEP"):
                continue
            ts=int(f.readline().strip())
            frame=[line,f"{ts}\n"]
            while True:
                pos=f.tell()
                nxt=f.readline()
                if not nxt:
                    break
                if nxt.startswith("ITEM: TIMESTEP"):
                    f.seek(pos)
                    break
                frame.append(nxt)
            yield ts, frame

def dump_info(path):
    first=last=None
    n=0
    for ts,_ in frame_iterator(path):
        if first is None:
            first=ts
        last=ts
        n+=1
    return first,last,n

def merge_dumps(files,outfile):
    last=-1
    kept_total=0
    report=[]
    with open(outfile,"w") as out:
        for f in files:
            kept=0
            skipped=0
            first,last,n=dump_info(f)
            for ts,frame in frame_iterator(f):
                if ts<=last:
                    skipped+=1
                    continue
                out.writelines(frame)
                last=ts
                kept+=1
                kept_total+=1
            report.append({
                "file":str(f),
                "first":first,
                "last":last,
                "frames":n,
                "kept":kept,
                "skipped_overlap":skipped
            })
    return kept_total, report

def merge_logs(logs,outfile):
    seen=set()
    wrote_header=False
    with open(outfile,"w") as out:
        for log in logs:
            thermo=False
            with open(log) as f:
                for line in f:
                    if not wrote_header:
                        out.write(line)
                    if line.startswith("Step"):
                        thermo=True
                        if wrote_header:
                            continue
                        else:
                            wrote_header=True
                            continue
                    if line.startswith("Loop time"):
                        thermo=False
                        continue
                    if thermo:
                        cols=line.split()
                        if not cols:
                            continue
                        try:
                            step=int(cols[0])
                        except:
                            continue
                        if step in seen:
                            continue
                        seen.add(step)
                        out.write(line)

def copy_latest(src,dst):
    restart_files=list(src.rglob("*.restart"))
    if restart_files:
        newest=max(restart_files,key=lambda p:p.stat().st_mtime)
        shutil.copy2(newest,dst/newest.name)
    data_files=list(src.rglob("*.data"))
    if data_files:
        newest=max(data_files,key=lambda p:p.stat().st_mtime)
        shutil.copy2(newest,dst/newest.name)
    inp=dst/"input_files"
    inp.mkdir(exist_ok=True)
    for ext in ("*.in","*.sh","*.params"):
        for f in src.glob(ext):
            shutil.copy2(f,inp/f.name)

def collect_segments(simdir):
    seg=[]
    for f in simdir.glob("*.lammpstrj"):
        first,last,n=dump_info(f)
        seg.append((first,f))
    for r in simdir.iterdir():
        if r.is_dir() and r.name.startswith("restart"):
            for f in r.glob("*.lammpstrj"):
                first,last,n=dump_info(f)
                seg.append((first,f))
    seg.sort(key=lambda x:x[0])
    return [x[1] for x in seg]

def collect_logs(simdir):
    logs=[]
    if (simdir/"log.lammps").exists():
        logs.append(simdir/"log.lammps")
    tmp=[]
    for r in simdir.iterdir():
        if r.is_dir() and r.name.startswith("restart"):
            lg=r/"log.lammps"
            if lg.exists():
                tmp.append(lg)
    tmp.sort(key=lambda p:p.stat().st_mtime)
    logs.extend(tmp)
    return logs

def is_sim_dir(d):
    if not d.is_dir():
        return False
    if any(d.glob("*.lammpstrj")):
        return True
    return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o","--output",default=None)
    args=ap.parse_args()

    root=Path(args.input).resolve()
    outroot=Path(args.output).resolve() if args.output else root.parent/(root.name+"_analysis")

    if outroot.exists():
        raise SystemExit(f"\nERROR: Output directory already exists:\n{outroot}\nRefusing to overwrite.\n")

    outroot.mkdir(parents=True)

    summary=[]

    simdirs=[]
    for d in root.rglob("*"):
        if is_sim_dir(d):
            simdirs.append(d)

    for sim in sorted(simdirs):
        rel=sim.relative_to(root)
        dest=outroot/rel
        dest.mkdir(parents=True,exist_ok=True)

        print(f"\nProcessing {rel}")

        dumps=collect_segments(sim)
        if not dumps:
            continue

        frames,report=merge_dumps(dumps,dest/"merged.lammpstrj")

        logs=collect_logs(sim)
        if logs:
            merge_logs(logs,dest/"merged.log")

        copy_latest(sim,dest)

        with open(dest/"metadata.json","w") as f:
            json.dump(report,f,indent=2)

        with open(dest/"merge_report.txt","w") as f:
            for r in report:
                f.write(json.dumps(r)+"\n")

        summary.append([
            str(rel),
            report[0]["first"],
            report[-1]["last"],
            frames,
            len(dumps)-1
        ])

    with open(outroot/"summary.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["Simulation","FirstStep","LastStep","MergedFrames","RestartSegments"])
        w.writerows(summary)

    print("\nDone.")
    print(f"\nOutput written to:\n{outroot}")

if __name__=="__main__":
    main()
