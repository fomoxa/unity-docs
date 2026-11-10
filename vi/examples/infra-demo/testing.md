# 06: Kiểm thử

Danh sách các bài kiểm thử của repo: mỗi bài kiểm cái gì, chạy thế nào (lệnh tay + script), kết quả mong đợi, và phần nó không bao phủ.

## Bản đồ kiểm thử <a href="#map-of-the-tests" id="map-of-the-tests"></a>

| # | Bài | Kiểm gì | Cần | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 1 | [`--selftest` cụm giả](#1-selftest-of-the-mock-cluster) | tài khoản, phòng, bạn bè, lời mời, bảng điểm, kỷ lục, TLS qua fRPC thật | .NET 8 | ~30 s | không cần Docker |
| 2 | [`--bot-test`](#2-bot-test-a-bot-climbs-the-platforms-over-real-udp) | ticket → UDP mã hoá → pod → nhảy/đáp bục → bảng điểm → kỷ lục | .NET 8 | ~40 s | gần người chơi thật nhất mà không cần Unity |
| 3 | [`test-nakama.sh`, `test-nakama-pool.sh`](#3-the-nakama-lua-module) | module Lua: ghép cặp, ticket, chặn RPC nội bộ | Nakama (compose hoặc cụm) | ~10 s | |
| 4 | [`test-real-backend.sh`](#4-real-backend-with-real-nakama) | backend thật + Nakama thật + pod thật: toàn bộ chức năng + `/metrics` | Docker, .NET 8 | ~2 phút | CI chạy bài này |
| 5 | [Kiểm tra tĩnh](#5-static-checks-generated-code-yaml-shell-lua-monitoring-config) | mã sinh khớp model, YAML, shell, Lua = ConfigMap, cấu hình giám sát | tuỳ | vài giây | |
| 6 | [`test-p5.sh`](#6-test-p5-gameservers-on-kubernetes-and-agones-needs-the-unity-player) | Agones: `Ready` → `Allocated`, ghép cặp 4 client | cụm K8s + `MyGame.exe` | ~1 phút | |
| 7 | [Kịch bản thử tay trong Unity](#7-manual-script-in-unity) | giao diện, camera, nhảy, bạn bè | Unity | 10 phút | |

> Mọi bài `--selftest`/`--bot-test` đều dựng cụm giả riêng rồi tắt, vì vậy tắt cụm giả đang chạy (Ctrl+C) trước khi chạy chúng, nếu không sẽ trùng cổng.

## 1. Selftest cụm giả <a href="#1-selftest-of-the-mock-cluster" id="1-selftest-of-the-mock-cluster"></a>

Lệnh tay:

```bash
cd ~/fomoxa-infra-demo
dotnet publish "MyGame/Server~/MyGame.Server.csproj" -c Release -o .mock/server
dotnet publish tools/MockCluster/MockCluster.csproj   -c Release -o .mock/cluster
dotnet .mock/cluster/MockCluster.dll --server=.mock/server/MyGame.Server.dll --pods=2 --selftest
echo "exit code: $?"
```

Hoặc chạy gọn: `./scripts/run-mock-cluster.sh --selftest --pods=2`

Nó làm gì: khởi động directory/backend giả + 2 pod thật, rồi một "client" dùng đúng giao thức fRPC của game thực hiện lần lượt:

| Nhóm | Các kiểm tra |
|---|---|
| Tài khoản | đăng ký trùng tên / mật khẩu yếu / sai mật khẩu / tài khoản không tồn tại đều bị từ chối; đăng nhập không phân biệt hoa-thường; nhận mã khôi phục; khôi phục bằng mã sai bị từ chối, mã đúng thành công; mã cũ hết hiệu lực; mật khẩu cũ không còn dùng được; đổi mật khẩu (mật khẩu cũ sai bị từ chối) |
| Phòng | `ListRooms`, hai người cùng xin phòng "auto", `Presence` (danh sách online), phòng không tồn tại bị từ chối |
| Bảng điểm | pod báo điểm → bảng xếp hạng đúng thứ tự → kỷ lục lưu bậc cao nhất (3, rồi 2, rồi 5 → 5) |
| Xã hội | lời mời kết bạn đến người nhận; chấp nhận → bạn 2 chiều; mời bạn vào phòng; bạn hiện online + đang ở đâu; không mời được người chưa là bạn |
| TLS | nối qua cổng TLS với đúng pin và gọi RPC; sai pin bị `TlsRejected` |

Kết quả mong đợi: các dòng `[selftest] OK ...`, kết thúc bằng:

```
[selftest] TAT CA DAT
[selftest] OK   Ket noi qua TLS (dung pin) va goi RPC (3 phong)
[selftest] TLS DAT
```

và `mã thoát: 0`. Có dòng `FAIL`/`CO LOI` → mã thoát 3.

Không kiểm: UDP (xem bài 2), Nakama thật (bài 4), Unity.

## 2. Bot test: bot leo bục qua UDP thật <a href="#2-bot-test-a-bot-climbs-the-platforms-over-real-udp" id="2-bot-test-a-bot-climbs-the-platforms-over-real-udp"></a>

Lệnh tay:

```bash
dotnet .mock/cluster/MockCluster.dll --server=.mock/server/MyGame.Server.dll --pods=2 --bot-test
# put BOT_TRACE=1 in front to print the bot's position
```

Hoặc chạy gọn: `./scripts/run-mock-cluster.sh --bot-test --pods=2`

Nó làm gì: (1) bot đăng ký `botjumper` qua fRPC và xin vào `arena:1` để lấy ticket; (2) dựng một runtime mạng Fomoxa thật (cùng thư viện với Unity), nối UDP mã hoá vào pod bằng ticket;
(3) pod xác thực ticket và biết đây là `botjumper`; (4) bot đọc vị trí server gửi về và tự đi/nhảy lên các bục; (5) sau ~25 giây kiểm bảng điểm và hồ sơ.

Kết quả mong đợi:

```
[bot] OK   Co ticket vao arena:1 -> 127.0.0.1:7779
[bot] ket noi: Starting None
[bot] ket noi: Authenticating None
[bot] ket noi: Started None
[bot] OK   Da vao pod (client Started)
[bot] OK   Bang diem co ten bot (botjumper:18/18)
[bot] OK   Bot leo duoc it nhat 3 bac (steps=18)
[bot] OK   Ky luc ca nhan duoc luu (best=18, matches=1)
[bot] TAT CA DAT
```

`steps=18` nghĩa là bot leo hết 18 bục, chứng tỏ vật lý nhảy/đáp bục của server cho phép leo trọn đường đi. Số bậc bot đạt có thể khác giữa các lần chạy (bot đơn giản); ngưỡng kiểm là ≥ 3.

## 3. Module Lua của Nakama <a href="#3-the-nakama-lua-module" id="3-the-nakama-lua-module"></a>

Cần một Nakama có module `deploy/nakama/modules/main.lua`. Hai cách:

```bash
# (a) Nakama and Postgres from docker compose (no Kubernetes)
docker compose -f deploy/compose.yaml up -d
until curl -fsS http://127.0.0.1:7350/healthcheck >/dev/null; do sleep 2; done

ALLOW_COMPOSE=1 ./scripts/test-nakama.sh
ALLOW_COMPOSE=1 ./scripts/test-nakama-pool.sh

docker compose -f deploy/compose.yaml down -v
```

```bash
# (b) Nakama in the k3d cluster (the scripts read its own keys from the fomoxa-nakama secret)
./scripts/test-nakama.sh
./scripts/test-nakama-pool.sh
```

Ý nghĩa của `ALLOW_COMPOSE=1`: script từ chối chạy nếu cổng 7350 đang do `docker compose` giữ (để bạn không vô tình test nhầm Nakama của compose khi tưởng đang test cụm). Đặt biến này để xác nhận bạn *cố ý*.

Các bước script làm (bung ra thành `curl` tay ở [03, Bước 12](deploy/07-test-nakama.md#step-12-test-nakama-with-curl)): đăng nhập 2 device → `reset_match` → ana `find_match` (`waiting`) → bo `find_match` (`matched` + ticket) → ana `poll_match` → backend `verify_ticket` (đúng người `ok:true`, người lạ `ok:false`).
Bài `pool` cho 4 người vào "auto": cặp 1 vào một phòng, cặp 2 vào phòng khác.

Kết quả mong đợi:

```
OK: 2 client ghep dung room, ticket dung, user ngoai bi chan!
...
Chung minh thanh cong: Cap 1 (arena:1) va Cap 2 (arena:2) duoc cap 2 room khac nhau tu pool!
=== DoD P5.5 HOAN TAT THANH CONG! ===
```

Bản PowerShell: `scripts\test-nakama.ps1`, `scripts\test-nakama-pool.ps1`.

## 4. Backend thật + Nakama thật <a href="#4-real-backend-with-real-nakama" id="4-real-backend-with-real-nakama"></a>

Mục tiêu: chạy đúng mã backend của cụm thật, nối vào Nakama thật (tài khoản/hồ sơ/bạn bè lưu trong Nakama storage qua RPC Lua `kv_get`/`kv_put`; ghép cặp qua Nakama), với pod thật cấp ticket. Chỉ directory được giả.

Hoặc chạy gọn (làm trọn các bước dưới): `./scripts/test-real-backend.sh`

Lệnh tay:

```bash
cd ~/fomoxa-infra-demo
WORK=$PWD/.mock/real-test && mkdir -p "$WORK"

# 1) Nakama and Postgres (if not already running)
docker compose -f deploy/compose.yaml up -d
until curl -fsS http://127.0.0.1:7350/healthcheck >/dev/null; do sleep 2; done

# 2) Build the backend, game server and mock cluster
dotnet publish MyGame.Backend/MyGame.Backend/MyGame.Backend.csproj -c Release -p:FomoxaGenerate=false -o "$WORK/backend"
dotnet publish "MyGame/Server~/MyGame.Server.csproj" -c Release -o "$WORK/server"
dotnet publish tools/MockCluster/MockCluster.csproj -c Release -o "$WORK/mock"

# 3) Keys: a random directory.key; pod.key is 32 zero bytes (the selftest logs in to the pod port with it)
head -c 32 /dev/urandom > "$WORK/directory.key"
head -c 32 /dev/zero    > "$WORK/pod.key"

# 4) The REAL backend pointing at the real Nakama (in the background)
Fomoxa__Directory__Address=127.0.0.1:9500 \
Fomoxa__Directory__Key__File="$WORK/directory.key" \
Fomoxa__Pods__Key__File="$WORK/pod.key" \
Fomoxa__Players__WebSocket="" \
Fomoxa__Nakama__Url=http://127.0.0.1:7350 \
Fomoxa__Metrics__Listen=127.0.0.1:9610 \
    dotnet "$WORK/backend/MyGame.Backend.dll" > "$WORK/backend.log" 2>&1 &
BACKEND_PID=$!
sleep 6

# 5) The mock cluster acts ONLY as directory and pods (its own mock backend moves to another port) and runs the selftest against the real backend
dotnet "$WORK/mock/MockCluster.dll" \
    --players=127.0.0.1:19600 --pods-listen=127.0.0.1:19602 --no-tls --pods=4 \
    --server="$WORK/server/MyGame.Server.dll" \
    --selftest-target=9600,9602 --selftest

# 6) Look at the real backend's metrics, then clean up
curl -s http://127.0.0.1:9610/metrics | grep -E '^fomoxa_(logins_total|joins_total|online_players|score_reports_total)'
kill $BACKEND_PID
docker compose -f deploy/compose.yaml down -v
```

Giải thích các tham số quan trọng:
- `-p:FomoxaGenerate=false`: bỏ bước chạy `fomoxac` lúc build, dùng mã sinh sẵn đã commit (CI kiểm riêng bằng `--check`).
- `Fomoxa__X__Y=...` là cách đặt cấu hình `X:Y` của .NET bằng biến môi trường (`__` thay cho `:`). `Fomoxa__Nakama__Url` bật chế độ Nakama của backend.
- `--selftest-target=9600,9602`: chạy selftest vào backend ngoài (cổng người chơi 9600, cổng pod 9602) thay vì backend giả.
- Tên người chơi trong selftest có hậu tố ngẫu nhiên (`st1a2b3c`...) vì tài khoản được lưu lâu dài trong Nakama, chạy lại không bị "tên đã có người dùng".

Kết quả mong đợi:

```
[selftest] OK   Dang ky tra ve ma khoi phuc (XNM7-NS5F-GBBC-QZV3)
[selftest] OK   Khoi phuc bang ma dung
[selftest] OK   ListRooms (auto[0/2] open, arena:1[0/2] open, arena:2[0/2] open, arena:3[0/2] open, arena:4[0/2] open)
[selftest] OK   JoinRoom auto (2 nguoi) -> 127.0.0.1:7778 / 127.0.0.1:7778 (qua Nakama that)
[selftest] OK   Cap ghep vao cung mot pod
[selftest] OK   JoinRoom phong khong ton tai bi tu choi
[selftest] OK   Bang diem xep hang (st8822e8:3/3, guestx:1/0)
[selftest] OK   Ky luc luu lai la bac cao nhat (best=5, matches=1)
[selftest] OK   Loi moi ket ban den nguoi nhan
[selftest] TAT CA DAT
=== /metrics cua backend ===
fomoxa_joins_total{result="ok"} 2
fomoxa_logins_total{mode="login",result="ok"} 5
fomoxa_logins_total{mode="register",result="ok"} 2
fomoxa_score_reports_total 3
fomoxa_online_players 2
```

Nếu bước 6 báo `Connection refused` ngay lúc đầu selftest: backend chưa kịp lên, tăng `sleep 6`.

Không kiểm: Kubernetes, Agones, gateway, `public_address`, UDP qua k3d.

## 5. Kiểm tra tĩnh: mã sinh, YAML, shell, Lua, cấu hình giám sát <a href="#5-static-checks-generated-code-yaml-shell-lua-monitoring-config" id="5-static-checks-generated-code-yaml-shell-lua-monitoring-config"></a>

```bash
# Is the committed generated code still in step with the models? (non-zero exit if stale)
FOMOXAC=$PWD/MyGame.Backend/tools/fomoxac/linux-x64/fomoxac; chmod +x "$FOMOXAC"
( cd MyGame.Backend/MyGame.Backend && "$FOMOXAC" generate --check )
( cd MyGame && "$FOMOXAC" generate --check )

# Syntax of every bash script
for f in scripts/*.sh; do bash -n "$f" && echo "ok $f"; done

# Every Kubernetes manifest is valid YAML
python3 - <<'PY'
import glob, yaml
for f in sorted(glob.glob("deploy/k8s/*.yaml") + glob.glob("deploy/monitoring/*.yaml")):
    docs = [d for d in yaml.safe_load_all(open(f)) if d]
    print("ok", f, len(docs), "doc")
PY

# main.lua must be IDENTICAL to the copy embedded in nakama.yaml's ConfigMap
python3 - <<'PY'
import yaml
docs = list(yaml.safe_load_all(open("deploy/k8s/nakama.yaml")))
lua = [d for d in docs if d and d.get("kind") == "ConfigMap"][0]["data"]["main.lua"]
assert lua.strip() == open("deploy/nakama/modules/main.lua").read().strip(), "main.lua differs from the ConfigMap"
print("main.lua == ConfigMap: ok")
PY
```

Ý nghĩa: `main.lua` tồn tại ở hai nơi (file cho docker compose và bản nhúng trong ConfigMap cho K8s). Sửa một nơi mà quên nơi kia là lỗi hay gặp, bài kiểm này bắt nó. Lệnh `promtool`/`amtool` kiểm cấu hình giám sát: xem [05, mục Giám sát](operations/04-monitoring.md#104-built-in-alerts).

Kết quả mong đợi: `Lien ket noi bo: OK`; `fomoxac: up to date` hai lần; `ok scripts/...`; `main.lua == ConfigMap: ok`.

## 6. `test-p5`: GameServer trên K8s + Agones (cần Unity Player) <a href="#6-test-p5-gameservers-on-kubernetes-and-agones-needs-the-unity-player" id="6-test-p5-gameservers-on-kubernetes-and-agones-needs-the-unity-player"></a>

Xem [03, Bước 13](deploy/08-test-client-and-cleanup.md#step-13-test-with-the-unity-client-real-players) để biết script làm gì từng bước.

```bash
./scripts/test-p5.sh                 # four automatic clients, checks exactly 2 Allocated pods
TEST_SCALE=1 ./scripts/test-p5.sh    # also scale the Fleet up by one, then back
```

Điều kiện: cụm k3d đang chạy ([03](deploy/README.md)), có `MyGame/Builds/MyGame.exe` ([04](unity-client.md)), chạy từ WSL2 có `powershell.exe`.
Từ PowerShell thuần: `powershell -ExecutionPolicy Bypass -File scripts\test-p5.ps1`.

## 7. Kịch bản thử tay trong Unity <a href="#7-manual-script-in-unity" id="7-manual-script-in-unity"></a>

Chạy một lần sau mỗi thay đổi lớn ở client (backend: cụm giả cho nhanh).

| # | Thao tác | Kỳ vọng |
|---|---|---|
| 1 | Mở `Lobby.unity`, Play | thấy form đăng nhập; thẻ Đăng nhập / Đăng ký / Quên mật khẩu |
| 2 | Đăng ký mật khẩu < 8 ký tự | thông báo đỏ "mật khẩu phải có ít nhất 8 ký tự" |
| 3 | Đăng ký hợp lệ | hiện mã khôi phục (ô chép được); "Tôi đã lưu mã" → vào sảnh |
| 4 | Đăng xuất, đăng nhập sai mật khẩu | "sai tên hoặc mật khẩu" |
| 5 | Quên mật khẩu với mã đúng + mật khẩu mới | vào được, hiện mã khôi phục mới |
| 6 | Thẻ Tài khoản: đổi mật khẩu | "Đã đổi mật khẩu" |
| 7 | Bấm `arena:1` | scene `Game` chỉ tải sau khi có ticket; nhân vật xuất hiện |
| 8 | Camera | đứng sau lưng nhân vật; chuột phải/Q/E xoay; cuộn zoom; W đi về phía camera nhìn |
| 9 | Space trong trận | nhảy; không thoát phòng; HUD ẩn |
| 10 | Nhảy lên bục 1, 2, 3... | đứng được trên mặt bục; đi ngang vào thân bục thì bị chặn |
| 11 | Esc / Tab | hiện menu + bảng điểm (số bậc của bạn); Esc lần nữa ẩn |
| 12 | Hai client, kết bạn nhau, mời vào phòng | lời mời hiện ở thẻ Bạn bè của người kia; "Tham gia" đưa họ vào phòng |
| 13 | "Thoát phòng" | về sảnh, vẫn đăng nhập; kỷ lục trong hồ sơ cập nhật |

## Ánh xạ sang CI (GitHub Actions) <a href="#how-this-maps-to-ci-github-actions" id="how-this-maps-to-ci-github-actions"></a>

File `.github/workflows/ci.yml` chạy tự động trên mỗi push/PR:

| Job | Bước | Bài ở trên |
|---|---|---|
| `build-and-selftest` | `fomoxac generate --check` (2 cây), build backend, build game server, `--selftest`, `--bot-test` | 1, 2, 5 |
| `real-backend` | `./scripts/test-real-backend.sh`, rồi `test-nakama.sh` + `test-nakama-pool.sh` với compose | 3, 4 |
| `lint-scripts-and-manifests` | `bash -n`, YAML hợp lệ, `promtool`/`amtool`, `main.lua` = ConfigMap | 5 |

Chạy lại cục bộ đúng như CI: các lệnh ở các mục 1-5 là chính nội dung các bước đó.
