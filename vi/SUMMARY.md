# Table of contents

* [Fomoxa for Unity](README.md)

## Bắt đầu

* [Giới thiệu](bat-dau/introduction.md)
* [Cài đặt](bat-dau/installation.md)
* [Project đầu tiên](bat-dau/first-project.md)
* [Server đầu tiên](bat-dau/first-server.md)
* [Client đầu tiên](bat-dau/first-client.md)
* [Xử lý sự cố](bat-dau/troubleshooting.md)

## Khái niệm

* [Kiến trúc](khai-niem/architecture.md)
* [Mô hình networking](khai-niem/networking-model.md)
* [Tick và thời gian](khai-niem/tick.md)
* [Authority](khai-niem/authority.md)
* [Replication](khai-niem/replication.md)
* [Prediction](khai-niem/prediction.md)
* [Mô phỏng tất định](khai-niem/deterministic-simulation.md)
* [Vòng đời](khai-niem/lifecycle.md)

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

* [State](dong-bo/state.md)
* [NetworkTransform](dong-bo/transform.md)
* [NetworkAnimator](dong-bo/animator.md)

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

* [Tổng quan](transport/overview.md)
* [UDP](transport/udp.md)
* [TCP](transport/tcp.md)
* [WebSocket](transport/websocket.md)
* [Nhiều transport](transport/multi-transport.md)
* [Loopback](transport/loopback.md)
* [Transport tùy chỉnh](transport/custom-transport.md)

## Server

* [Dedicated server](server/dedicated-server.md)
* [Triển khai](server/deployment.md)
* [Server console](server/server-console.md)

## Unity

* [Tích hợp Editor](unity/editor-integration.md)
* [WebGL](unity/webgl.md)

## Nâng cao

* [Codec tùy chỉnh và type của Unity](nang-cao/custom-codecs.md)
* [Hiệu năng](nang-cao/performance.md)
* [Debug](nang-cao/debugging.md)

## Ví dụ

* [Red Runner](vi-du/redrunner/README.md)
  * [Bản offline ban đầu](vi-du/redrunner/offline-baseline.md)
  * [Từ offline lên online](vi-du/redrunner/offline-to-online/README.md)
    * [Bước 01: Nền tảng network](vi-du/redrunner/offline-to-online/step-01-network-foundation.md)
    * [Bước 02: Level dùng chung](vi-du/redrunner/offline-to-online/step-02-shared-level.md)
    * [Bước 03: Spawn người chơi](vi-du/redrunner/offline-to-online/step-03-player-spawning.md)
    * [Bước 04: Input của người chơi](vi-du/redrunner/offline-to-online/step-04-player-input.md)
    * [Bước 05: Prediction và reconciliation](vi-du/redrunner/offline-to-online/step-05-prediction-and-reconciliation.md)
    * [Bước 06: Chết và hồi sinh](vi-du/redrunner/offline-to-online/step-06-death-and-respawn.md)
    * [Bước 07: Chướng ngại di chuyển](vi-du/redrunner/offline-to-online/step-07-moving-hazards.md)
    * [Bước 08: Hai client](vi-du/redrunner/offline-to-online/step-08-two-clients.md)
    * [Bước 09: Game online hoàn chỉnh](vi-du/redrunner/offline-to-online/step-09-final-online-game.md)
  * [Kiến trúc bản online](vi-du/redrunner/architecture.md)
  * [Xử lý sự cố](vi-du/redrunner/troubleshooting.md)

## Tham chiếu

* [Danh mục API](tham-chieu/api.md)
* [NetworkManager](tham-chieu/network-manager.md)
* [ServerManager](tham-chieu/server-manager.md)
* [ClientManager](tham-chieu/client-manager.md)
* [TimeManager](tham-chieu/time-manager.md)
* [NetworkObject và NetworkBehaviour](tham-chieu/network-object.md)
* [Component](tham-chieu/components.md)
* [Physics API](tham-chieu/physics.md)
* [Messaging API](tham-chieu/messaging.md)
* [Cấu hình](tham-chieu/configuration.md)
* [Attribute](tham-chieu/attributes.md)
* [Event và callback](tham-chieu/callbacks.md)
* [Lỗi và lý do dừng](tham-chieu/errors.md)
* [Thuật ngữ](tham-chieu/glossary.md)

## Đóng góp

* [Phát triển](dong-gop/development.md)
* [Tài liệu](dong-gop/documentation.md)
