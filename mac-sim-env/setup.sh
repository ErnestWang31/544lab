#!/usr/bin/env bash
# One-shot setup for the MTE544 ROS 2 environment on macOS.
# Usage:  cd ~/Downloads/mte544-env && bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

say() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

# 1. Docker Desktop
if ! [ -d /Applications/Docker.app ]; then
  say "Installing Docker Desktop (you'll be asked for your Mac password)"
  if [ "$(uname -m)" = "arm64" ]; then ARCH=arm64; else ARCH=amd64; fi
  DMG=/tmp/Docker.dmg
  curl -fL -o "$DMG" "https://desktop.docker.com/mac/main/${ARCH}/Docker.dmg"
  hdiutil attach -nobrowse -quiet "$DMG"
  sudo /Volumes/Docker/Docker.app/Contents/MacOS/install --accept-license --user="$USER"
  hdiutil detach -quiet /Volumes/Docker
  rm -f "$DMG"
fi

# 2. Start Docker and wait for the engine
say "Starting Docker Desktop"
open -a Docker
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"
for i in $(seq 1 90); do
  docker info >/dev/null 2>&1 && break
  [ "$i" = 90 ] && { echo "Docker didn't start. Open Docker Desktop, finish its first-run screens, then re-run this script."; exit 1; }
  sleep 2
done

# 3. Build and start the ROS 2 container
# Plain docker build/run (no compose/buildx plugins needed; those are broken on some installs).
say "Building the ROS 2 Humble image (first time: ~10-15 min)"
# Gazebo Classic / turtlebot3_gazebo are only packaged for amd64 in Humble, so build an
# amd64 image; Docker emulates it on Apple Silicon (slower, but it's what the course uses).
BASE=tiryoh/ros2-desktop-vnc:humble
if [ "$(docker image inspect -f '{{.Architecture}}' $BASE 2>/dev/null)" != "amd64" ]; then
  docker rmi $BASE >/dev/null 2>&1 || true   # drop a cached arm64 copy
  docker pull --platform linux/amd64 $BASE
fi
DOCKER_BUILDKIT=0 docker build --platform linux/amd64 -t mte544-humble .

ARCH_BUILT=$(docker image inspect -f '{{.Architecture}}' mte544-humble)
[ "$ARCH_BUILT" = "amd64" ] || { echo "Image built as $ARCH_BUILT, expected amd64."; exit 1; }

say "Starting the container"
docker rm -f mte544 >/dev/null 2>&1 || true
mkdir -p workspace
docker run -d --platform linux/amd64 --name mte544 \
  -p 6080:80 \
  --shm-size=2g \
  -e RESOLUTION=1600x1000 \
  -v "$PWD/workspace:/mte544" \
  --restart unless-stopped \
  mte544-humble

# 4. Wait for the web desktop and open it
say "Waiting for the desktop to come up"
for i in $(seq 1 60); do
  curl -fs http://localhost:6080 >/dev/null 2>&1 && break
  sleep 2
done
open http://localhost:6080

say "Done (stop: docker stop mte544, start again: docker start mte544). Desktop: http://localhost:6080 (click Connect). Lab code: ./workspace/MTE544_student"
echo "Tip: in Docker Desktop > Settings > Resources, give it >= 4 CPUs and 8 GB RAM for Gazebo."
