# Mục lục

* [Fomoxa for Unity](README.md)

## Bắt đầu

* [Giới thiệu](getting-started/introduction.md)
* [Cài đặt](getting-started/installation.md)
* [Project đầu tiên](getting-started/first-project.md)
* [Server đầu tiên](getting-started/first-server.md)
* [Client đầu tiên](getting-started/first-client.md)
* [Xử lý sự cố](getting-started/troubleshooting.md)

## Khái niệm

* [Kiến trúc](concepts/architecture.md)
* [Mô hình networking](concepts/networking-model.md)
* [Tick và thời gian](concepts/tick.md)
* [Authority](concepts/authority.md)
* [Replication](concepts/replication.md)
* [Prediction](concepts/prediction.md)
* [Mô phỏng tất định](concepts/deterministic-simulation.md)
* [Vòng đời](concepts/lifecycle.md)

## Core

* [NetworkManager](core/network-manager.md)
* [Server](core/server.md)
* [Client](core/client.md)
* [Host mode](core/host-mode.md)
* [NetworkObject](core/network-object.md)
* [NetworkBehaviour](core/network-behaviour.md)
* [Spawn](core/spawning.md)
* [Ownership](core/ownership.md)
* [Observer](core/observers.md)
* [Network scene](core/scenes.md)

## Messaging

* [Model và codec](messaging/models.md)
* [RPC](messaging/rpc.md)
* [Channel và độ tin cậy](messaging/channels.md)
* [Raw message](messaging/messages.md)

## Đồng bộ

* [State](synchronization/state.md)
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
* [Contact event](physics/contacts.md)
* [Kiến trúc physics](physics/architecture.md)

## Transport

* [Tổng quan](transports/overview.md)
* [UDP](transports/udp.md)
* [TCP](transports/tcp.md)
* [WebSocket](transports/websocket.md)
* [Nhiều transport](transports/multi-transport.md)
* [Loopback](transports/loopback.md)
* [Transport tùy chỉnh](transports/custom-transport.md)

## Server

* [Dedicated server](server/dedicated-server.md)
* [Triển khai](server/deployment.md)
* [Server console](server/server-console.md)

## Unity

* [Tích hợp Editor](unity/editor-integration.md)
* [WebGL](unity/webgl.md)

## Nâng cao

* [Codec tùy chỉnh và type của Unity](advanced/custom-codecs.md)
* [Hiệu năng](advanced/performance.md)
* [Debug](advanced/debugging.md)

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
