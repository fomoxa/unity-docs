# Hướng dẫn phát triển

Lên đầu tài liệu: [trang chủ tài liệu](../README.md) · Trước: [frpc-add-a-method.md](frpc-add-a-method.md)

Công thức cho những thay đổi hay gặp nhất. Mỗi mục nêu các file cần sửa và các kiểm tra cần chạy. Các kiểm tra được mô tả ở [kiểm thử](../testing.md).

## Chuẩn bị <a href="#set-up" id="set-up"></a>

```bash
git clone https://github.com/fomoxa/fomoxa-infra-demo.git
cd fomoxa-infra-demo
./scripts/run-mock-cluster.sh --selftest
```

Bạn cần .NET SDK 8 ([chuẩn bị môi trường](../getting-started/prepare-environment.md#step-7-install-the-net-8-sdk)). Lệnh trên build game server và cụm giả rồi chạy selftest. Nếu kết thúc bằng `TAT CA DAT` thì bộ công cụ đã hoạt động.

## Mã nằm ở đâu <a href="#where-the-code-lives" id="where-the-code-lives"></a>

| Khu vực | Đường dẫn |
|---|---|
| Backend | `MyGame.Backend/MyGame.Backend/` ([backend](backend.md)) |
| Game server | `MyGame/Server~/` ([game server](game-server.md)) |
| Client Unity và gameplay dùng chung | `MyGame/Assets/Network/` ([mã client](client-code.md)) |
| Cụm giả | `tools/MockCluster/` |
| Module Nakama | `deploy/nakama/modules/main.lua` ([module Nakama](nakama-module.md)) |
| Manifest Kubernetes | `deploy/k8s/` ([đọc manifest](../deploy/manifest-walkthrough.md)) |
| Giám sát | `deploy/monitoring/` |
| Script | `scripts/` ([danh sách](../reference.md#4-scripts-and-their-manual-equivalents)) |
| CI | `.github/workflows/ci.yml` |

## Thêm hoặc đổi một RPC <a href="#add-or-change-an-rpc" id="add-or-change-an-rpc"></a>

[Thêm một phương thức fRPC](frpc-add-a-method.md) đi qua các bước này với một ví dụ chạy được.

1. Thêm hoặc sửa message trong `MyGame.Backend/MyGame.Backend/Models/*.cs`. Đánh dấu lớp bằng `[Network]` và `[Codec("rpc")]`, mỗi thuộc tính bằng `[Network("<kiểu>")]` và `[Codec("rpc")]`.
2. Khai báo phương thức trong `Services.cs` ở dịch vụ phù hợp. Dùng `Requires = Roles.Player` cho lệnh của sảnh.
3. Cài đặt trong `Players.cs` (cho `Lobby`) hoặc `Pods.cs` (cho `PodGate`). Logic dùng chung với cụm giả đặt ở `Accounts/LobbyCore.cs`.
4. Chép cùng model và dịch vụ sang cây Unity: `MyGame/Assets/Network/Models/Backend/*.cs` và `MyGame/Assets/Network/Rpc/Services.cs`.
5. Sinh lại cả hai cây ([mục kế](#regenerate-the-code)).
6. Nếu cụm giả cần hỗ trợ, cài đặt trong `tools/MockCluster/MockBackend.cs`.
7. Thêm một bước vào `--selftest` trong `tools/MockCluster/Program.cs`.
8. Cập nhật trang [giao diện RPC](rpc-api.md) ở cả hai ngôn ngữ.

## Sinh lại mã <a href="#regenerate-the-code" id="regenerate-the-code"></a>

Backend và Unity mỗi bên có cây mã sinh riêng, và chúng phải khớp nhau. `fomoxac` đọc model và ghi codec.

```bash
FOMOXAC=$PWD/MyGame.Backend/tools/fomoxac/linux-x64/fomoxac
chmod +x "$FOMOXAC"
( cd MyGame.Backend/MyGame.Backend && "$FOMOXAC" generate )
( cd MyGame && "$FOMOXAC" generate )
```

CI chạy `generate --check` trên cả hai và thất bại khi file đã commit bị cũ. Hãy commit file sinh cùng với thay đổi.

## Đổi gameplay <a href="#change-the-gameplay" id="change-the-gameplay"></a>

Các luật nằm trong `MyGame/Assets/Network/Models/Course.cs` và dùng chung cho client và server. Sau khi đổi một hằng số:

1. Dựng lại scene trong Unity: **Tools > Demo > Rebuild Scene** (nó vẽ lại các bục).
2. Build lại image game server: `./scripts/build-images.sh`, rồi `k3d image import` và tạo lại Fleet ([cập nhật](../operations/01-status-and-updates.md)).
3. Kiểm tra bằng `./scripts/run-mock-cluster.sh --bot-test`. Bot vẫn phải leo được các bục. Nếu bạn làm cú nhảy khó hơn, hãy chờ số bậc ít hơn.

## Thêm phòng <a href="#add-a-room" id="add-a-room"></a>

Các phòng được liệt kê trong `FOMOXA_ROOM` của `deploy/k8s/fleet.yaml` (`arena:1` đến `arena:16`). Muốn thêm, mở rộng danh sách và tăng `maxReplicas` trong `fleet-autoscaler.yaml` để số pod và số phòng luôn bằng nhau. Pod không có phòng trống sẽ đợi và thử lại mỗi 2 giây.

Nhóm `auto` trong module Lua mặc định dùng `arena:1` đến `arena:4`. Backend thường ghi đè nó bằng các phòng mà pod báo lên, nên bạn không cần sửa Lua cho việc này.

## Sửa module Nakama <a href="#change-the-nakama-module" id="change-the-nakama-module"></a>

Xem [sửa module](nakama-module.md#changing-the-module). Bản chép trong ConfigMap và file phải khớp nhau, nếu không CI thất bại.

## Thêm một metric <a href="#add-a-metric" id="add-a-metric"></a>

Ở backend, gọi `Metrics?.Count("tên")` cho counter hoặc `metrics.Gauge("tên", "mô tả", () => giá trị)` cho gauge. Ở game server, dùng đối tượng `Metrics("fomoxa_pod")` trong `Program.cs`. Thêm một panel vào dashboard ở `deploy/monitoring/30-grafana.yaml` và, nếu cần, một cảnh báo ở `10-prometheus.yaml`. Rồi kiểm tra bằng `promtool` ([giám sát](../operations/04-monitoring.md)).

## Trước khi push <a href="#before-you-push" id="before-you-push"></a>

```bash
./scripts/run-mock-cluster.sh --selftest
./scripts/run-mock-cluster.sh --bot-test
```

Thêm `./scripts/test-real-backend.sh` khi bạn đổi tài khoản, ghép trận hoặc module Lua (cần Docker). Các job CI được liệt kê cuối trang [kiểm thử](../testing.md#how-this-maps-to-ci-github-actions).

Các trang này thuộc tài liệu Fomoxa for Unity trong [fomoxa/unity-docs](https://github.com/fomoxa/unity-docs). Trang [tài liệu](../../../contributing/documentation.md) của nó có các quy tắc khi sửa chúng.
