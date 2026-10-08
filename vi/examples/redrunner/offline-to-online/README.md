# Từ offline lên online

Quá trình chuyển đổi gồm chín bước. Mỗi bước để lại một game biên dịch và chạy được, nên bạn có thể test và commit nó trước khi sang bước tiếp theo.

```
Offline game (2b675b5)
  ↓
01 Network foundation: package, settings, NetworkManager
  ↓
02 Shared level: a seed as state on a scene object
  ↓
03 Player spawning: server, host, client, one character per peer
  ↓
04 Player input: a tick step that the server runs
  ↓
05 Prediction and reconciliation: the owner moves at once
  ↓
06 Death and respawn: the server decides
  ↓
07 Moving hazards: maces on the server's tick
  ↓
08 Two clients: what other players see, leaving and crashing
  ↓
09 Final online game
```

## Các bước <a href="#steps" id="steps"></a>

| Bước | Thay đổi gì | Trang Fomoxa |
|---|---|---|
| [01 Nền tảng network](step-01-network-foundation.md) | Unity 6000.5, package, sinh code, một `NetworkManager` trong `Play.unity` | [Cài đặt](../../../getting-started/installation.md), [NetworkManager](../../../core/network-manager.md) |
| [02 Level dùng chung](step-02-shared-level.md) | Một level hữu hạn dựng từ seed mà server giữ trong một state | [State](../../../synchronization/state.md), [Spawn](../../../core/spawning.md#scene-objects) |
| [03 Spawn người chơi](step-03-player-spawning.md) | Nhân vật trở thành network prefab; game khởi động dưới dạng server, host hoặc client | [Spawn](../../../core/spawning.md), [Server](../../../core/server.md), [Client](../../../core/client.md) |
| [04 Input của người chơi](step-04-player-input.md) | Input model và bước tick mà server áp dụng | [Input](../../../prediction/input.md), [Authority](../../../concepts/authority.md) |
| [05 Prediction và reconciliation](step-05-prediction-and-reconciliation.md) | Motion model, rollback physics 2D, camera theo người chơi cục bộ | [Reconciliation](../../../prediction/reconciliation.md), [Rollback với physics](../../../prediction/rollback.md) |
| [06 Chết và hồi sinh](step-06-death-and-respawn.md) | Cái chết quyết định trên server, state của người chơi, hồi sinh bằng teleport | [State](../../../synchronization/state.md), [Teleport](../../../synchronization/transform.md#teleporting) |
| [07 Chướng ngại di chuyển](step-07-moving-hazards.md) | Path follower được đặt theo số tick | [Tick và thời gian](../../../concepts/tick.md) |
| [08 Hai client](step-08-two-clients.md) | Animation của nhân vật ở xa, người chơi rời đi hoặc bị crash | [NetworkTransform](../../../synchronization/transform.md), [Input](../../../prediction/input.md) |
| [09 Game online hoàn chỉnh](step-09-final-online-game.md) | Bản build player, dedicated server, ảnh chụp màn hình | [Dedicated server](../../../server/dedicated-server.md) |

## Commit <a href="#commits" id="commits"></a>

Các bước được thực hiện thành các commit trên branch `master` của [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner), bắt đầu từ commit gốc `2b675b5`. Mỗi trang bước kết thúc bằng mục Commit nêu commit theo short hash và message của nó kèm link.

| Bước | Commit |
|---|---|
| 01 | [`8983a5a`](https://github.com/fomoxa/RedRunner/commit/8983a5ae2105e4ce79b8b127c9e5564147707eb1) |
| 02 | [`0b9d85f`](https://github.com/fomoxa/RedRunner/commit/0b9d85fb089698c82ec0bcfccede2d7b59028482) |
| 03 | [`1b65628`](https://github.com/fomoxa/RedRunner/commit/1b656285a486c6be727309e48d6612a3e483da80) |
| 04 và 05 | [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) |
| 06 | [`a148ea7`](https://github.com/fomoxa/RedRunner/commit/a148ea70ca4eea0ec407c9cd85af57ca1acdf589) |
| 07 | [`f277dad`](https://github.com/fomoxa/RedRunner/commit/f277dad4cc29eccef696158280185c9117a270ae) |
| 08 | [`52e1696`](https://github.com/fomoxa/RedRunner/commit/52e1696b2e5b8db09e0178f827febf9ae712a02f), [`0edd3a4`](https://github.com/fomoxa/RedRunner/commit/0edd3a46a0f5bf48a76786e6242ea2f523e1ec21), [`c75cebd`](https://github.com/fomoxa/RedRunner/commit/c75cebdee36f6edfc3869964157bd45093eae543), [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf) |
| 09 | [`7396f92`](https://github.com/fomoxa/RedRunner/commit/7396f9279b5796ffb35d97765cbe5cb1794d5357) |

Bước 04 và 05 dùng chung một commit, còn bước 08 trải trên bốn commit. Trong lịch sử, `7396f92` của bước 09 nằm giữa `52e1696` và `0edd3a4` của bước 08.

## Làm theo <a href="#following-along" id="following-along"></a>

Để làm theo các bước trong project của riêng bạn, hãy làm việc trên một branch từ commit gốc, và so sánh kết quả với một bước bằng cách chạy `git diff` với commit của bước đó:

1. Clone [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner) và tạo một branch từ `2b675b5`: `git switch -c my-port 2b675b5`.
2. Làm bước 01, chạy test của nó, rồi commit.
3. Tiếp tục với bước tiếp theo theo cách đó.

Các trang hiển thị code như ở cuối quá trình chuyển đổi, trong commit [`f164d56`](https://github.com/fomoxa/RedRunner/commit/f164d5624f171b64c8bfc6f029b12be2cfe41e27), commit chuyển game hoàn chỉnh sang package hiện tại. Khi một bước sau thay đổi code mà bước trước đã thêm, bước trước hiển thị phiên bản của nó và bước sau hiển thị phần thay đổi.

Việc phát lại chính xác lịch sử có một số giới hạn:

- Bước 04 và 05 được làm trong một commit, nên game chỉ được test một lần, ở cuối bước 05.
- Bước 08 trải trên bốn commit. Hai trong số đó, `c75cebd` và `c239d2a`, dựa vào các thay đổi package thực hiện trong lúc port: teleport generation trong `NetworkTransform`, message `PeerLeave` và `InputContext.RepeatedTicks`. Package đã phát hành có tất cả những thay đổi này.
- Các commit của từng bước dùng package dưới tên cũ, `com.fomoxa.unity`, từ một bản copy cục bộ nằm cạnh project (`file:../../fomoxa-unity/com.fomoxa.unity`). Để build một commit trong số đó, hãy thay mục đó trong `Packages/manifest.json` bằng `"com.fomoxa.unity": "https://github.com/fomoxa/com.fomoxa.unity.git"`. Commit `f164d56` chuyển game sang `com.fomoxa.networking`: nó cài package từ Git URL trong trang [cài đặt](../../../getting-started/installation.md), đổi các chỉ thị `using` sang namespace `Fomoxa.Networking`, và bật mô phỏng physics qua một component `RigidbodyPhysics` trên `Network Manager`.
- Chưa ai kiểm tra từng commit xem một commit cũ có biên dịch được với package hiện tại sau khi sinh lại code hay không.
- `Play.unity`, `RedRunner.prefab` và `Generation Settings.asset` được lưu ở dạng mà `git diff` hiển thị là nhị phân, nên các bước mô tả thay đổi của chúng dưới dạng thiết lập Inspector.
- Mỗi commit còn thêm các bài kiểm tra tự động trong `Tools/PortChecks`, cùng một script, `Tools/unity-windows.sh`, chạy chúng từ WSL với một Editor Windows. Các bước mô tả mỗi bài kiểm tra xác minh điều gì để bạn có thể test thủ công.

Bắt đầu với [bước 01: nền tảng network](step-01-network-foundation.md).
