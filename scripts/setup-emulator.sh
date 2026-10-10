#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
source "$ROOT/config/dependencies.env"
cd "$ROOT"
mkdir -p .build-deps logs
command -v cmake >/dev/null || { echo 'Missing cmake: brew install cmake or sudo apt-get install cmake' >&2; exit 1; }
if [[ ! -d .build-deps/mgba/.git ]]; then
    git init .build-deps/mgba
    git -C .build-deps/mgba remote add origin https://github.com/mgba-emu/mgba.git
    git -C .build-deps/mgba fetch --depth 1 origin "$MGBA_REVISION"
fi
git -C .build-deps/mgba checkout --detach "$MGBA_REVISION"
echo 'Building pinned headless mGBA; log: logs/setup-mgba.log'
cmake -S .build-deps/mgba -B .build-deps/mgba-build -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_FFMPEG=OFF -DUSE_LIBZIP=OFF -DUSE_PNG=OFF -DUSE_LZMA=OFF \
    -DUSE_SQLITE3=OFF -DUSE_DISCORD_RPC=OFF -DUSE_EPOXY=OFF -DUSE_MINIZIP=OFF -DENABLE_SCRIPTING=OFF -DBUILD_GL=OFF -DBUILD_GLES2=OFF -DBUILD_GLES3=OFF \
    -DBUILD_SHARED=ON -DBUILD_STATIC=OFF > logs/setup-mgba.log 2>&1
cmake --build .build-deps/mgba-build --parallel "${JOBS:-4}" >> logs/setup-mgba.log 2>&1
cc -Wall -Wextra tests/emulator_driver.c -I.build-deps/mgba-build/include -I.build-deps/mgba/include \
    -L.build-deps/mgba-build -lmgba -Wl,-rpath,"$ROOT/.build-deps/mgba-build" -o .build-deps/emulator-driver
echo 'mGBA headless test driver ready.'
