# 544lab — MTE544 group repo

## Layout

| Branch | What's in it |
| --- | --- |
| `main` | This README + the macOS/Docker ROS 2 sim setup (`mac-sim-env/`) |
| `LabOne`, `LabTwo`, … | One branch per lab, based on the prof's branch of the same name |

The prof's repo (`UW-MTE544/MTE544_student`) is our `upstream`. Real-robot data goes in `data/` on each lab branch (sim CSVs in the root are git-ignored — they're huge).

## Starting a new lab

```bash
git fetch upstream
git checkout -b LabTwo upstream/LabTwo
git push -u origin LabTwo
```
