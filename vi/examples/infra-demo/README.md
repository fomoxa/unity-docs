# Infra demo

[fomoxa/fomoxa-infra-demo](https://github.com/fomoxa/fomoxa-infra-demo) là một game nhiều người chơi nhỏ chạy trên mọi phần của một cụm Fomoxa: client Unity, game server build thành console server .NET, directory và gateway, backend của game, Nakama để ghép trận và giữ tài khoản, và Agones trên Kubernetes. Các trang này dẫn bạn từ một máy trắng tới lúc game chạy. Mỗi bước là một lệnh shell copy-paste được, và bạn không cần biết Kubernetes từ trước.

[Cụm server](../../deploy/cluster.md), [Backend của game](../../deploy/backend.md) và [Agones](../../deploy/agones.md) giải thích từng phần riêng. Ví dụ này chạy chúng cùng nhau, từ script và manifest của một repo. Repo dùng `com.fomoxa.networking` 0.3.4, `com.fomoxa.rpc` 0.1.5 và gateway ở tag `0.2.0`.

## Hệ thống gồm những gì <a href="#what-the-system-contains" id="what-the-system-contains"></a>

```
                         YOUR MACHINE (WSL2 or Ubuntu)
 +-----------------------------------------------------------------------------+
 |  Docker                                                                     |
 |  +- k3d = k3s (small Kubernetes) running inside Docker containers           |
 |     +- cluster "fomoxa"                                                     |
 |        +- namespace agones-system   Agones (controls game servers)          |
 |        +- namespace fomoxa                                                  |
 |           +- postgres      Nakama's database                                |
 |           +- nakama        matchmaking, plus accounts/profiles/friends      |
 |           +- directory     knows which pod holds which room, issues tickets |
 |           +- gateway       the only UDP entry point for game servers        |
 |           +- backend       login, room list, join requests                  |
 |           +- game-server   Agones Fleet: the pods that run the game         |
 +-----------------------------------------------------------------------------+
        ^  TCP 9600 (backend)                      ^  UDP 7777 (gateway)
        |  login, room list, ticket requests       |  gameplay, encrypted with the ticket
        +-------------------  UNITY CLIENT  -------+
```

Client chỉ nhìn thấy đúng hai cổng:

| Cổng | Giao thức | Tới đâu | Dùng để |
|---|---|---|---|
| `9600` | TCP | `backend` | đăng nhập, danh sách phòng, xin vào phòng (fRPC) |
| `7777` | UDP | `gateway` | chơi game; gateway chuyển tiếp tới đúng `game-server` |

Mọi thứ còn lại (postgres, nakama, directory, game-server) nằm trong cluster, client không nối trực tiếp.
Ngoại lệ có chủ đích:

| Cổng | Khi nào mở | Ghi chú |
|---|---|---|
| `9643` TCP | tuỳ chọn | cùng việc với 9600 nhưng được mã hoá TLS (proxy `tls-proxy`). Môi trường thật nên dùng cổng này thay 9600. |
| `7350` TCP | chỉ để chạy script test | Nakama API. Client thật không dùng. |

### Luồng một lần vào game <a href="#one-trip-into-a-game" id="one-trip-into-a-game"></a>

```
1. Client --TCP 9600--> backend      log in (name + password), get the room list
2. Client --TCP 9600--> backend      "let me into arena:1"
3.          backend --> nakama        pair two players, receive the assigned room
4.          backend --> directory     "issue a ticket for arena:1"
5.          directory returns the ticket and public_address (the GATEWAY address, not the pod's)
6. Client --UDP 7777--> gateway --> the game server that holds arena:1   (the pod checks the ticket)
```

`public_address` trong `directory.toml` là địa chỉ mà client thấy. Chạy local nó là `127.0.0.1:7777` (k3d đưa cổng 7777 của
máy bạn vào gateway). Đặt sai chỗ này, client sẽ cố nối vào địa chỉ nội bộ của pod và treo.

### k3d là gì? <a href="#what-k3d-is" id="what-k3d-is"></a>

`k3d` chạy k3s (một bản Kubernetes gọn) bên trong các container Docker. Cả cluster là vài container trên máy bạn, xoá đi là sạch.
Cổng của máy bạn được đưa vào cluster qua một container "load balancer" của k3d (tham số `--port ...@loadbalancer`).

## Chọn trang để đọc <a href="#which-document-to-read" id="which-document-to-read"></a>

| Bạn muốn... | Đọc |
|---|---|
| Chỉ thử client Unity trên một máy, không cần Kubernetes | [02: Chạy nhanh bằng cụm giả](getting-started/quickstart-mock-cluster.md) |
| Dựng cụm Kubernetes thật (k3d + Agones) | [01](getting-started/prepare-environment.md) rồi [03: Triển khai K8s](deploy/README.md) |
| Mở project Unity, build client, tham số dòng lệnh | [04: Client Unity](unity-client.md) |
| Logs, scale, cập nhật, TLS, giám sát, autoscaling, sao lưu | [05: Vận hành](operations/README.md) |
| Chạy các bài kiểm thử, hiểu từng test kiểm cái gì | [06: Kiểm thử](testing.md) |
| Gặp lỗi | [07: Xử lý sự cố](troubleshooting.md) |
| Tra cứu cổng, secrets, biến môi trường, script làm gì | [08: Tham khảo](reference.md) |
| Hiểu các thành phần và mã nguồn khớp nhau thế nào, hoặc sửa chúng | [Kiến trúc](architecture/overview.md) |
| Gọi một RPC có sẵn hoặc thêm RPC mới | [Dùng fRPC](architecture/using-frpc.md), [Thêm một phương thức fRPC](architecture/frpc-add-a-method.md) |

Người mới nên đọc 01, 02 (thấy game chạy), 03 (cụm thật), 04, 05.

## Cách đọc một bước <a href="#how-to-read-a-step" id="how-to-read-a-step"></a>

Mỗi bước có cùng một khuôn: mục tiêu, lệnh, lệnh làm gì và vì sao, kết quả mong đợi, cách kiểm tra, và lỗi thường gặp.

- Lệnh nằm trong khối `bash` và chạy từ thư mục gốc của repo nếu không ghi khác (`cd ~/fomoxa-infra-demo`).
- Script chỉ là đường tắt. Mọi script đều được bung ra thành các lệnh tay ngay cạnh, nên bạn có thể làm bằng tay để hiểu chuyện gì xảy ra, hoặc chạy script. Tìm dòng "Hoặc chạy gọn: `./scripts/xxx.sh`". Bảng đối chiếu đầy đủ ở [08](reference.md#4-scripts-and-their-manual-equivalents).
- Kết quả mong đợi cho biết định dạng. Tên pod, tuổi, hash và thời gian trên máy bạn sẽ khác. Dòng log mà các chương trình của game in ra là tiếng Việt hoặc tiếng Việt không dấu, và tài liệu trích nguyên văn.
- Thuật ngữ Kubernetes (pod, deployment, namespace, secret, configmap, service, context) giữ nguyên tiếng Anh và được giải thích ở lần đầu xuất hiện.

## Cấu trúc thư mục repo <a href="#repository-layout" id="repository-layout"></a>

```
fomoxa-infra-demo/
+- deploy/
|  +- k8s/                 Kubernetes manifests (postgres, nakama, directory, gateway, backend, tls-proxy, fleet, ...)
|  +- monitoring/          Prometheus, Alertmanager, Grafana, Loki, Promtail
|  +- nakama/modules/      main.lua, the Nakama module for matchmaking and the key-value store
|  +- Dockerfile.{server,directory,gateway}
|  +- compose.yaml         Nakama + Postgres for local development (no Kubernetes)
|  +- secrets/             generated, never committed: keys and certificates
+- MyGame/                 Unity project (client) and Server~/ (console game server, .NET 8)
+- MyGame.Backend/         .NET backend (login, rooms, accounts, friends)
+- server-deps/            source of the Fomoxa libraries used to build the game server
+- tools/MockCluster/      mock cluster (backend + directory + real pods on one machine)
+- scripts/                helper scripts (.sh for Linux/WSL2, .ps1 for Windows)
+- gateway/                cloned on demand, never committed: Rust source of directory and gateway
```
