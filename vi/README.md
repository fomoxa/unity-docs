# Fomoxa for Unity

Fomoxa for Unity (`com.fomoxa.networking`) là package networking theo mô hình server-authoritative cho game Unity, xây trên giao thức Fomoxa và runtime C# của nó, Fomoxa.Net. Game khai báo các message của mình bằng class C# thông thường, package sinh codec cho chúng, rồi các component như `NetworkManager`, `NetworkObject` và `NetworkBehaviour` lo phần kết nối, spawn, RPC, state, transform và client-side prediction.

| | |
|---|---|
| Package | `com.fomoxa.networking` 0.1.0 |
| Unity | 6000.5 trở lên |
| Giấy phép | Apache-2.0 |
| Công cụ sinh code đi kèm | `fomoxac` v0.2.2, Windows x64 và Linux x64 |

## Bắt đầu từ đâu <a href="#where-to-start" id="where-to-start"></a>

Nếu mới làm quen với package, hãy đọc [giới thiệu](getting-started/introduction.md) trước, rồi làm theo trang [cài đặt](getting-started/installation.md) và ba trang hướng dẫn sau đó, nơi bạn xây một game nhỏ có server, host và client. Phần [khái niệm](concepts/architecture.md) giải thích package hoạt động bên dưới ra sao: các tầng, tick, authority, replication và prediction.

Khi cần thêm một tính năng cụ thể, hãy xem các hướng dẫn trong Core, Messaging, Synchronization, Prediction, Physics và Transports; mỗi trang nói về một tính năng kèm code chạy được. Nếu đang chuyển một game có sẵn lên online, [ví dụ Red Runner](examples/redrunner/README.md) đưa một game platformer một người chơi lên online qua chín bước, kèm code và commit thật. Để tra một member cụ thể, dùng phần [tham chiếu](reference/api.md), nơi liệt kê public API theo type.

## Package làm được gì <a href="#what-the-package-covers" id="what-the-package-covers"></a>

Package kết nối các peer qua UDP, TCP hoặc WebSocket. Một server có thể lắng nghe trên nhiều transport cùng lúc, còn host mode dùng kết nối trong cùng tiến trình thay cho socket. Network object được spawn từ prefab hoặc đặt sẵn trong scene, và mỗi object có thể có owner cùng khả năng hiển thị khác nhau với từng peer.

Client gọi server và server gọi client qua các RPC khai báo bằng attribute. Mỗi behaviour có thể giữ một state được gửi bằng delta encoding, `NetworkTransform` replicate transform kèm interpolation và teleport, còn `NetworkAnimator` replicate Animator. Network scene có thể được load cho mọi người hoặc chỉ cho một số peer được chọn.

Package còn hỗ trợ client-side prediction với input, reconciliation và replay, bao gồm cả rollback physics 3D và 2D của Unity. Client WebGL kết nối qua WebSocket của trình duyệt.

Trang [giới thiệu](getting-started/introduction.md#what-is-not-included) liệt kê những gì package không làm.

## Ngoài physics của Unity và server Unity <a href="#beyond-unitys-physics-and-unity-servers" id="beyond-unitys-physics-and-unity-servers"></a>

Có hai phần tùy chọn xây trên cùng package, dùng khi game đã chạy được trong Unity. [Rapier physics](rapier/overview.md) là một package riêng thay physics của Unity bằng Rapier, để rollback phát lại physics của server chính xác. [Server console](console-server/overview.md) chạy server của game như một chương trình .NET không cần Unity. Phần còn lại của tài liệu không phụ thuộc vào hai phần này, và phần hai của [ví dụ Red Runner](examples/redrunner/rapier-and-console/README.md) dùng cả hai.
