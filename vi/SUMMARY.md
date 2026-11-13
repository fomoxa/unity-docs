# Mục lục

* [Fomoxa for Unity](README.md)

## Bắt đầu

* [Giới thiệu](getting-started/introduction.md)
* [Cài đặt](getting-started/installation.md)
* [Tutorial: game nhiều người chơi đầu tiên](getting-started/tutorial/README.md)
  * [1. Chuẩn bị project](getting-started/tutorial/project-setup.md)
  * [2. Khởi động server](getting-started/tutorial/server.md)
  * [3. Kết nối client](getting-started/tutorial/clients.md)
* [Xử lý sự cố](getting-started/troubleshooting.md)
* [Ghi chú phát hành](release-notes.md)

## Kiến thức nền

* [Package được xây dựng thế nào](concepts/architecture.md)
* [Server, client và message](concepts/networking-model.md)
* [Tick và thời gian](concepts/tick.md)
* [Authority](concepts/authority.md)
* [Replication](concepts/replication.md)
* [Prediction](concepts/prediction.md)
* [Mô phỏng tất định](concepts/deterministic-simulation.md)
* [Vòng đời](concepts/lifecycle.md)

## Kết nối

* [NetworkManager](connections/network-manager.md)
* [Server](connections/server.md)
* [Client](connections/client.md)
* [Xác thực](connections/authentication.md)
* [Host mode](connections/host-mode.md)
* [Chuyển server](connections/transfer.md)
* [Transport](connections/transports/README.md)
  * [UDP](connections/transports/udp.md)
  * [UDP mã hóa](connections/transports/encrypted-udp.md)
  * [WebSocket mã hóa](connections/transports/encrypted-websocket.md)
  * [TCP](connections/transports/tcp.md)
  * [WebSocket](connections/transports/websocket.md)
  * [Steam](connections/transports/steam.md)
  * [TLS phía client](connections/transports/tls.md)
  * [Nhiều transport](connections/transports/multi-transport.md)
  * [Loopback](connections/transports/loopback.md)
  * [Giả lập mạng](connections/transports/simulated.md)
  * [Transport tùy chỉnh](connections/transports/custom-transport.md)

## Network object

* [NetworkObject](objects/network-object.md)
* [NetworkBehaviour](objects/network-behaviour.md)
* [Spawn](objects/spawning.md)
* [Ownership](objects/ownership.md)
* [Observer](objects/observers.md)
* [Network scene](objects/scenes.md)

## Messaging

* [Model và codec](messaging/models.md)
* [RPC](messaging/rpc.md)
* [Channel và độ tin cậy](messaging/channels.md)
* [Raw message](messaging/messages.md)

## Đồng bộ

* [State](synchronization/state.md)
* [Collection](synchronization/collections.md)
* [NetworkTransform](synchronization/transform.md)
* [NetworkAnimator](synchronization/animator.md)

## Prediction

* [Tổng quan](prediction/overview.md)
* [Input](prediction/input.md)
* [Reconciliation](prediction/reconciliation.md)
* [Rollback với physics](prediction/rollback.md)

## Physics

* [Tổng quan](physics/overview.md)
* [PhysicsBody](physics/physics-body.md)
* [Truy vấn physics](physics/queries.md)
* [Contact event](physics/contacts.md)
* [Kiến trúc physics](physics/architecture.md)

## Triển khai

* [Dedicated server](deploy/dedicated-server.md)
* [Đưa server lên môi trường thật](deploy/deployment.md)
* [Backend của game](deploy/backend.md)
* [Cụm server](deploy/cluster.md)
* [Agones](deploy/agones.md)
* [WebGL](deploy/webgl.md)

## Nâng cao

* [Tích hợp Editor](advanced/editor-integration.md)
* [Codec tùy chỉnh và type của Unity](advanced/custom-codecs.md)
* [Hiệu năng](advanced/performance.md)
* [Debug](advanced/debugging.md)

## Rapier physics

* [Tổng quan](rapier/overview.md)
* [Cài đặt](rapier/setup.md)
* [Body và collider](rapier/bodies.md)
* [Contact event](rapier/contacts.md)
* [Joint](rapier/joints.md)
* [Character controller](rapier/character-controller.md)
* [Effector](rapier/effectors.md)
* [Tính tất định](rapier/determinism.md)

## Server console

* [Tổng quan](console-server/overview.md)
* [Project](console-server/project.md)
* [Runtime](console-server/runtime.md)
* [Physics](console-server/physics.md)
* [Tham chiếu](console-server/reference.md)

## Ví dụ

* [Red Runner](examples/redrunner/README.md)
  * [Bản offline ban đầu](examples/redrunner/offline-baseline.md)
  * [Từ offline lên online](examples/redrunner/offline-to-online/README.md)
    * [Bước 01: Nền tảng network](examples/redrunner/offline-to-online/step-01-network-foundation.md)
    * [Bước 02: Level dùng chung](examples/redrunner/offline-to-online/step-02-shared-level.md)
    * [Bước 03: Spawn người chơi](examples/redrunner/offline-to-online/step-03-player-spawning.md)
    * [Bước 04: Input của người chơi](examples/redrunner/offline-to-online/step-04-player-input.md)
    * [Bước 05: Prediction và reconciliation](examples/redrunner/offline-to-online/step-05-prediction-and-reconciliation.md)
    * [Bước 06: Chết và hồi sinh](examples/redrunner/offline-to-online/step-06-death-and-respawn.md)
    * [Bước 07: Chướng ngại di chuyển](examples/redrunner/offline-to-online/step-07-moving-hazards.md)
    * [Bước 08: Hai client](examples/redrunner/offline-to-online/step-08-two-clients.md)
    * [Bước 09: Game online hoàn chỉnh](examples/redrunner/offline-to-online/step-09-final-online-game.md)
  * [Kiến trúc bản online](examples/redrunner/architecture.md)
  * [Xử lý sự cố](examples/redrunner/troubleshooting.md)
  * [Rapier và server console](examples/redrunner/rapier-and-console/README.md)
    * [Bước 10: Backend Rapier](examples/redrunner/rapier-and-console/step-10-rapier-backend.md)
    * [Bước 11: Thư viện mô phỏng](examples/redrunner/rapier-and-console/step-11-simulation-library.md)
    * [Bước 12: Catalogue level](examples/redrunner/rapier-and-console/step-12-level-catalogue.md)
    * [Bước 13: Server console](examples/redrunner/rapier-and-console/step-13-console-server.md)
* [Infra demo](examples/infra-demo/README.md)
  * [Chuẩn bị môi trường (Ubuntu / WSL2)](examples/infra-demo/getting-started/prepare-environment.md)
  * [Chạy nhanh bằng cụm giả (không cần Kubernetes)](examples/infra-demo/getting-started/quickstart-mock-cluster.md)
  * [Triển khai cụm Kubernetes (k3d + Agones) từng bước](examples/infra-demo/deploy/README.md)
    * [Khái niệm Kubernetes dùng trong demo này](examples/infra-demo/deploy/concepts.md)
    * [Chuẩn bị, cổng trống, khoá và chứng chỉ](examples/infra-demo/deploy/01-prepare-and-keys.md)
    * [Lấy mã nguồn gateway và build image Docker](examples/infra-demo/deploy/02-build-images.md)
    * [Tạo cluster k3d, cài Agones, nạp image](examples/infra-demo/deploy/03-cluster-and-agones.md)
    * [Namespace và Secrets](examples/infra-demo/deploy/04-secrets.md)
    * [Apply manifest theo thứ tự](examples/infra-demo/deploy/05-apply-manifests.md)
    * [Kiểm tra toàn cụm và kiểm tra từ phía client](examples/infra-demo/deploy/06-verify-cluster.md)
    * [Test Nakama bằng curl](examples/infra-demo/deploy/07-test-nakama.md)
    * [Test bằng client Unity và dọn dẹp](examples/infra-demo/deploy/08-test-client-and-cleanup.md)
    * [Đọc các file manifest trong `deploy/k8s/`](examples/infra-demo/deploy/manifest-walkthrough.md)
    * [Đường đi của lưu lượng và nơi cấu hình TLS](examples/infra-demo/deploy/traffic-and-tls.md)
  * [Client Unity: mở project, dựng scene, build, chạy](examples/infra-demo/unity-client.md)
  * [Vận hành cụm](examples/infra-demo/operations/README.md)
    * [Trạng thái, log, scale, restart, cập nhật image](examples/infra-demo/operations/01-status-and-updates.md)
    * [Tắt game server an toàn (drain) và tài khoản người chơi](examples/infra-demo/operations/02-drain-and-accounts.md)
    * [TLS và khoá Nakama](examples/infra-demo/operations/03-tls-and-keys.md)
    * [Giám sát](examples/infra-demo/operations/04-monitoring.md)
    * [Autoscaling, NetworkPolicy, sao lưu, địa chỉ công khai](examples/infra-demo/operations/05-scaling-security-backup.md)
  * [Kiến trúc](examples/infra-demo/architecture/overview.md)
    * [Backend](examples/infra-demo/architecture/backend.md)
    * [Module Nakama](examples/infra-demo/architecture/nakama-module.md)
    * [Game server (pod)](examples/infra-demo/architecture/game-server.md)
    * [Mã client Unity](examples/infra-demo/architecture/client-code.md)
    * [Giao diện RPC](examples/infra-demo/architecture/rpc-api.md)
    * [Dùng fRPC](examples/infra-demo/architecture/using-frpc.md)
    * [Thêm một phương thức fRPC](examples/infra-demo/architecture/frpc-add-a-method.md)
    * [Hướng dẫn phát triển](examples/infra-demo/architecture/development.md)
  * [Kiểm thử](examples/infra-demo/testing.md)
  * [Xử lý sự cố](examples/infra-demo/troubleshooting.md)
  * [Tham khảo](examples/infra-demo/reference.md)

## Tham chiếu

* [Danh mục API](reference/api.md)
* [NetworkManager](reference/network-manager.md)
* [ServerManager](reference/server-manager.md)
* [ClientManager](reference/client-manager.md)
* [TimeManager](reference/time-manager.md)
* [NetworkObject và NetworkBehaviour](reference/network-object.md)
* [Component](reference/components.md)
* [Physics API](reference/physics.md)
* [Messaging API](reference/messaging.md)
* [Cấu hình](reference/configuration.md)
* [Attribute](reference/attributes.md)
* [Event và callback](reference/callbacks.md)
* [Lỗi và lý do dừng](reference/errors.md)
* [Thuật ngữ](reference/glossary.md)

## Đóng góp

* [Phát triển](contributing/development.md)
* [Tài liệu](contributing/documentation.md)
