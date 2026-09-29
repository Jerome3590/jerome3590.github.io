---
description: Required patterns for any Rocket League BakkesMod capture plugin — match-scoped lifecycle, worker-thread network I/O, dual-write env vars, libcurl+OpenSSL CA bundle, DLL deploy with rename-then-copy
globs:
  - "rocket_league_screen_capture_*/**/*.cpp"
  - "rocket_league_screen_capture_*/**/*.h"
  - "rocket_league_screen_capture_*/CMakeLists.txt"
  - "scripts/build_screen_capture_*.bat"
  - "scripts/launch_rl.ps1"
alwaysApply: false
---

# BakkesMod capture-plugin patterns (RL streaming analytics)

These rules codify the lessons learned during the 2026-04-22/23 KVS
bring-up session. Full postmortems: [`docs/DLL_LOAD_ISSUES.md`](../../docs/DLL_LOAD_ISSUES.md)
§2.4–§2.8. Session-level summary: [`docs/IMPLEMENTATION_TODO.md`](../../docs/IMPLEMENTATION_TODO.md)
Lessons learned L-1 through L-7.

The reference implementation for all of these lives in
`rocket_league_screen_capture_kvs/KvsCapturePlugin.cpp`. When editing
`_s3` or `_combined` plugins, bring the pattern across verbatim unless
there's a plugin-specific reason not to.

## 1. `onLoad()` registers hooks only — nothing else

`onLoad()` runs during BakkesMod's injector phase, before RL's main
menu is visible. This means:

- No Game_ID exists yet → any captured frame is orphaned from DynamoDB.
- The game thread is mid-startup and cannot tolerate blocking work.
- Every DLL you force-load stays in RL's address space for the entire
  session → amplifies any DLL detach-order hazard on exit
  (`log4cplus.dll_unloaded` BEX64 is the recurring offender).

Therefore `onLoad()` may only:

- Initialize the diagnostic trace sink (`DiagTrace::instance().init(...)`).
- `HookEvent` for `TAGame.GameEvent_TA.StartEvent` +
  `ProjectX.GRI_X.EventGameStarted` → route both to `onMatchStarted()`.
- `HookEvent` for `TAGame.GameEvent_Soccar_TA.EventMatchEnded` +
  `TAGame.GameEvent_TA.Destroyed` → route both to `onMatchEnded()`.
- Log a `[hooks] registered …` confirmation line.

Everything else — `configureGStreamerEnv()`, `gst_init()`,
`logElementAvailability()`, `Aws::InitAPI()`, factory probes, CA
setup — belongs in the first call to `startCapture()` under a
one-shot `gstInitialized_`/`awsInitialized_` guard.

## 2. `startCapture()` runs on a dedicated worker thread

`kvssink`'s `READY → PAUSED` transition calls `createStreamSync()`
synchronously and can block for the full 2-minute libcurl timeout.
Running that on the game thread triggers Windows' hang detector
(Event ID 10002) — RL gets terminated ~2 min after match start.

Required pattern in `onMatchStarted()`:

```cpp
void CapturePlugin::onMatchStarted() {
    if (capturing_.load() || startingUp_.exchange(true)) return;
    if (startThread_.joinable()) startThread_.join();
    startThread_ = std::thread([this]() {
        try { startCapture(); }
        catch (const std::exception& e) { log(std::string("[fatal] startCapture worker::") + e.what()); }
        catch (...) { log("[fatal] startCapture worker: unknown exception"); }
        startingUp_ = false;
    });
}
```

`onMatchEnded()` and `onUnload()` **must** `join()` `startThread_`
before any pipeline teardown. A still-running `createStreamSync`
while `gst_deinit()` runs is a textbook use-after-free.

## 3. Probe the network before you trust the SDK

`startCapture()` must call `probeKvsEndpoint()` (WinHTTP bounded
HTTPS HEAD against `kinesisvideo.us-east-1.amazonaws.com`, 5 s per
phase) **before** `buildPipeline()` + `set_state(PLAYING)`. A
probe success + SDK hang points at SDK TLS/credentials config. A
probe failure points at firewall / DNS / corporate proxy.

Don't debug a 2-minute opaque `createStreamSync` timeout when a
sub-second `[probe]` log line will tell you the layer that failed.

`probeKvsEndpoint()` uses WinHTTP (SChannel) — if it succeeds it
proves Windows can reach KVS. It does **not** prove libcurl+OpenSSL
can (see §5). Different TLS stacks, different trust stores.

## 4. Windows env vars need a dual write for co-loaded DLLs

`_putenv_s` only updates the caller's CRT env block. `SetEnvironmentVariable`
only updates Win32. A DLL with its own CRT (like `gstkvssink.dll`)
won't see a single-path update if its CRT already initialized from
Win32 before you made the change.

Always write both paths:

```cpp
_putenv_s("KVSSINK_CA_CERT_PATH", path.c_str());
SetEnvironmentVariableW(L"KVSSINK_CA_CERT_PATH", wpath.c_str());
```

Applies to every env var `kvssink` or AWS-via-libcurl consumes:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
- `AWS_CA_BUNDLE`, `KVSSINK_CA_CERT_PATH`
- `AWS_ENDPOINT_URL_KINESIS_VIDEO`

Reference: `ensureKvsCredentialEnv()` + `ensureCaCertPathEnv()` in
the KVS plugin.

## 5. Ship a CA bundle for libcurl+OpenSSL

The KVS Producer SDK's libcurl links OpenSSL, and OpenSSL on Windows
has **no** access to the system certificate store. Without an
explicit CA bundle, every TLS handshake against
`*.amazonaws.com` fails verification, libcurl retries until the
full 2 min timeout, and `createStreamSync` throws
`STATUS_OPERATION_TIMED_OUT` (0xF) with "Could not initialize
supporting library".

- Canonical bundle: `external/kvs_producer_sdk/certs/cacert.pem`
  (Mozilla; from <https://curl.se/ca/cacert.pem>). Committed.
- CMake bakes the path in: `target_compile_definitions(... PRIVATE
  "KVSSINK_CA_BUNDLE_PATH=\"${REPO_ROOT}/external/kvs_producer_sdk/certs/cacert.pem\"")`.
- `ensureCaCertPathEnv()` must run **before** `set_state(PLAYING)`
  and before `ensureKvsCredentialEnv()`.
- Log the resolved path + a `verified readable` confirmation so
  future regressions are obvious in the log.

## 6. DLL deploy uses rename-then-copy

After an RL crash or hang-kill, child processes (`crashpad_handler`,
`XboxGameBarSpotify`, `EpicWebHelper`, `EpicGamesLauncher`) can hold
open handles on the RL process for minutes, pinning RL's mapped
plugin DLLs against overwrite. Plain `Copy-Item` fails with a
sharing violation.

NTFS allows a file rename while the image section is locked:

```powershell
$dll = "$env:APPDATA\bakkesmod\bakkesmod\plugins\<plugin>.dll"
if (Test-Path $dll) {
    try { Rename-Item $dll "$dll.stale.$([int](Get-Date -UFormat %s))" -Force } catch {}
}
Copy-Item "<build-output>\<plugin>.dll" $dll -Force
```

Build scripts (`scripts/build_screen_capture_*.bat`) should bake
this pattern in. Accumulated `*.stale.*` files clear on next reboot.

## 7. Launcher liveness checks must not trust zombie PIDs

`Get-Process -Name RocketLeague` returns zombie entries with
`HasExited=$false` and valid PIDs but no UI. `launch_rl.ps1`'s
"RL already running" short-circuit triggers incorrectly on these.

Gate the short-circuit on responsiveness, not presence:

```powershell
$rl = Get-Process -Name RocketLeague -ErrorAction SilentlyContinue
if ($rl -and $rl.Responding) { Write-Host "[launch] RL already running"; exit 0 }
```

## Cross-reference

When you edit the KVS plugin's lifecycle or env-var handling, update
[`docs/DLL_LOAD_ISSUES.md`](../../docs/DLL_LOAD_ISSUES.md) §2.5–§2.8
and [`docs/IMPLEMENTATION_TODO.md`](../../docs/IMPLEMENTATION_TODO.md)
L-section in the same commit. The code and the postmortems are the
same story told twice; diverging them is how regressions sneak back in.
