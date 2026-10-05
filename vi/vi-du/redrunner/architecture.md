# Kiến trúc bản online

Trang này mô tả bản port hoàn chỉnh trên branch `master` của [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner), với code game tính tới commit [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf). Quá trình [chuyển đổi](offline-to-online/) giải thích từng phần đã đi tới đây như thế nào.

```
                         Red Runner (one player build)
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
             Client                                   Server
               │                                         │
     Start screen: address               NetworkGame: -server, -port
               │                                         │
     NetworkPlayer.Gather              OnRemoteConnectionState → Spawn
     (keys → PlayerInput)                                │
               │                          NetworkPlayer.Apply at the tick
     Apply (prediction)                     (RedCharacter.Simulate)
     RedCharacter.Simulate                               │
               │                           2D physics step, enemy contacts
     Reconcile with PlayerMotion                         │
     (restore, replay)                     ServerTick: death, fall, end block
               │                                         │
     ShowState: death effects             PlayerState, NetworkTransform
     NetworkTransform: other players                     │
     Camera, background, coins                           │
               │                                         │
               └────────────── Fomoxa over UDP ──────────┘
                     input frames  →
                     ←  spawn, state, transforms, reconcile states

     Both sides: NetworkLevel builds the level from LevelState.Seed
                 and moves path followers by tick number
```

## Scene và prefab <a href="#scene-and-prefab" id="scene-and-prefab"></a>

`Assets/Scenes/Play.unity` chứa các object networking bên cạnh các object gốc của game:

| Object              | Component                                              | Vai trò                                                               |
| ------------------- | ------------------------------------------------------ | --------------------------------------------------------------------- |
| Network Manager     | `NetworkManager`, `UdpNetworkTransport`, `NetworkGame` | Kết nối và tick; logic khởi động, spawn và người chơi cục bộ của game |
| Network Level       | `NetworkObject`, `NetworkLevel`                        | Scene object chứa seed của level; di chuyển các path follower         |
| Terrain Generator   | `TerrainGenerator`                                     | Dựng level từ seed; nền quanh người chơi cục bộ                       |
| Canvas/Start Screen | `StartScreen`, Address Field                           | Kết nối tới địa chỉ                                                   |
| Canvas/Pause Screen | `PauseScreen`                                          | Rời server                                                            |

`NetworkManager` dùng Tick Rate 50, Timing Mode Tick, Simulate Physics bật và Max Reconnect Retries 3, với Collected Prefabs và Collected Scenes đặt thành các danh sách đã sinh. Mọi thứ khác giữ mặc định.

`Assets/Prefabs/RedRunner.prefab` là người chơi trên mạng. Nó có `RedCharacter`, `Rigidbody2D`, `NetworkObject`, `NetworkTransform` (Sync Rotation tắt và Sync Scale bật) và `NetworkPlayer`.

## Model <a href="#models" id="models"></a>

Mọi model nằm trong `Assets/Scripts/RedRunner/Networking/Models`, và code sinh ra nằm trong `Networking/Generated` dưới namespace `Generated`.

| Model          | Dùng làm        | Đăng ký bởi     | Mang                                 |
| -------------- | --------------- | --------------- | ------------------------------------ |
| `LevelState`   | State           | `NetworkLevel`  | `Seed`                               |
| `PlayerState`  | State           | `NetworkPlayer` | `Dead`, `Cause`                      |
| `PlayerInput`  | Input           | `NetworkPlayer` | `Move`, `Jump`, `Roll`               |
| `PlayerMotion` | Reconcile state | `NetworkPlayer` | Vị trí, vận tốc, `RunSmoothVelocity` |

Game không dùng RPC hay raw message, và vị trí của người chơi khác đi qua `NetworkTransform`.

## Server <a href="#server" id="server"></a>

Server có authority với mọi thứ ảnh hưởng tới nhiều hơn một người chơi. Nó chọn seed của level trong `NetworkLevel.OnStartServer`, và quyết định nhân vật nào tồn tại bằng cách spawn chúng trong `NetworkGame.OnRemoteConnectionState` và despawn chúng cùng owner. Nó di chuyển mọi nhân vật bằng cách chạy `Apply` với input đã tới cho tick đó.

Cái chết cũng được quyết định trên server, từ contact với kẻ địch trong bước physics và từ phép kiểm tra rơi trong `NetworkPlayer.ServerTick`, và việc hồi sinh cũng vậy, diễn ra 100 tick sau khi chết hoặc khi nhân vật vượt qua `TerrainGenerator.EndX`. Server bỏ qua đồng xu và rương. Dedicated server giới hạn frame rate ở 60 bằng `Application.targetFrameRate`.

## Client <a href="#client" id="client"></a>

Client dựng level từ seed, dự đoán nhân vật của mình và hiển thị mọi thứ khác theo những gì server gửi. Nó thu thập input mỗi tick một lần trong `NetworkPlayer.Gather` và dự đoán nhân vật của mình, được `PlayerMotion` từ server sửa lại. Nhân vật khác được `NetworkTransform` interpolate dưới dạng body kinematic, và `ShowState` hiển thị hiệu ứng chết và hồi sinh khi `PlayerState` thay đổi. Camera, nền và đồng xu chỉ ở cục bộ, vì chỉ người chơi cục bộ ảnh hưởng tới chúng.

Không nhân vật nào tự quyết định cái chết của mình trên client, nên kẻ địch bị một nhân vật được dự đoán hoặc interpolate chạm vào sẽ không làm gì ở đó.

## Một tick <a href="#one-tick" id="one-tick"></a>

Bảng sau đi theo [thứ tự một tick](../../khai-niem/tick.md#order-of-one-tick) của package và cho thấy code của Red Runner ở từng bước:

| Bước        | Server                                                                 | Client của owner                                         |
| ----------- | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| `OnPreTick` | `NetworkLevel` đưa các path follower tới tick của server               | `NetworkLevel` đưa các path follower tới prediction tick |
| Input       | `NetworkPlayer.Apply` cho mỗi nhân vật với input của tick này          | Reconcile, rồi `Gather` và `Apply` cho nhân vật của mình |
| Physics     | Một bước physics 2D; kẻ địch gọi `Die` trên nhân vật có `DecidesDeath` | Một bước physics 2D                                      |
| Sau physics | Reconcile state (`PlayerMotion`) tới mỗi owner                         | Ghi lại `PlayerMotion` và lưu physics cho tick           |
| `OnTick`    | `NetworkPlayer.ServerTick`: chết, rơi, hồi sinh, khối kết thúc         |                                                          |
| Gửi         | `PlayerState`, `LevelState` và transform đã thay đổi                   | Input frame                                              |

## Gián đoạn <a href="#discontinuities" id="discontinuities"></a>

Hồi sinh đưa một nhân vật đi ngang qua cả level trong một tick, và mỗi phần của game thấy cú nhảy đó xử lý nó theo cách riêng:

| Ai thấy                           | Xử lý bởi                                                                          |
| --------------------------------- | ---------------------------------------------------------------------------------- |
| Interpolation của các client khác | `NetworkTransform.Teleport()` trong `Respawn`, bắt đầu một teleport generation mới |
| Prediction của owner              | Một reconcile mismatch thông thường và replay                                      |
| Animator trên các client khác     | `RedCharacter.LateUpdate` coi một lần di chuyển quá 2 đơn vị là teleport           |

## Người chơi rời đi <a href="#players-who-leave" id="players-who-leave"></a>

| Trường hợp                     | Điều gì xảy ra                                                                                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Người chơi bấm Home hoặc thoát | `ClientManager.StopConnection` gửi `PeerLeave`; server kết thúc peer và despawn nhân vật ngay                                                                       |
| Client bị crash hoặc mất mạng  | Server lặp lại input cuối; sau 10 tick bị lặp, `Apply` bỏ trục di chuyển và nhân vật đứng yên; heartbeat kết thúc session khoảng 20 giây sau và nhân vật bị despawn |

## Không có trong bản online <a href="#not-in-the-online-game" id="not-in-the-online-game"></a>

Bản online bỏ điểm số, điểm cao và màn hình kết thúc, cùng với đồng xu và thiết lập lưu bằng SaveGameFree và hành động đỡ và đấm. Người chơi không va chạm với nhau, vì layer `Characters` không va chạm với chính nó. Không có lobby, phòng hay matchmaking, và màn hình tạm dừng không còn dừng game; nó chỉ làm trống input của người chơi.
