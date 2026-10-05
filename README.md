# 544lab — MTE544 group repo

Private repo for our MTE544 labs. **Don't make it public or fork it publicly** — it has graded solutions.

## Layout

| Branch | What's in it |
| --- | --- |
| `main` | This README + the macOS/Docker ROS 2 sim setup (`mac-sim-env/`) |
| `LabOne`, `LabTwo`, … | One branch per lab, based on the prof's branch of the same name |

The prof's repo (`UW-MTE544/MTE544_student`) is our `upstream`. Real-robot data goes in `data/` on each lab branch (sim CSVs in the root are git-ignored — they're huge).

## Getting started (labmates)

```bash
git clone -b LabOne https://github.com/ErnestWang31/544lab.git
cd 544lab
git remote add upstream https://github.com/UW-MTE544/MTE544_student.git
```

## Starting a new lab

```bash
git fetch upstream
git checkout -b LabTwo upstream/LabTwo
git push -u origin LabTwo
```

Pull teammates' work with `git pull`; commit small and often to avoid conflicts.

## Running the sim on a Mac

See `mac-sim-env/README.md`. Short version: copy `mac-sim-env/` somewhere, clone the lab branch into `mac-sim-env/workspace/`, then `bash setup.sh` and open http://localhost:6080.
