# Project đầu tiên

Hướng dẫn này xây một game nhỏ qua ba trang. Ở trang này bạn chuẩn bị scene, một model và một prefab người chơi. Sau đó [server đầu tiên](first-server.md) khởi động một server spawn người chơi cho mỗi client, và [client đầu tiên](first-client.md) kết nối tới server đó.

Trong game hoàn chỉnh, mỗi người chơi đã kết nối là một khối capsule. Owner của capsule bấm nút Jump, server đẩy capsule lên và đếm số lần nhảy, và mọi client đều thấy capsule di chuyển và con số thay đổi.

Trước khi bắt đầu, hãy hoàn thành [cài đặt](installation.md) với thư mục model `Assets/Network/Models` và thư mục code sinh ra `Assets/Network/Generated`.

## 1. Thêm NetworkManager vào scene <a href="#1-add-a-networkmanager-to-the-scene" id="1-add-a-networkmanager-to-the-scene"></a>

1. Tạo một scene, `Assets/Scenes/Game.unity`, và mở nó.
2. Mở File > Build Profiles và thêm scene vào Scene List. Bản build player cần scene có mặt ở đó, và package lấy danh sách scene từ danh sách này.
3. Tạo một GameObject trống ở gốc scene và đặt tên là `Network Manager`.
4. Thêm component `UdpNetworkTransport` vào nó.
5. Thêm component `NetworkManager` và kéo component `UdpNetworkTransport` vào field Transport của nó.

Giữ các field khác của `NetworkManager` ở giá trị mặc định, Tick Rate 30 và Timing Mode Tick; [NetworkManager](../core/network-manager.md) mô tả từng field. Một `NetworkManager` không có transport sẽ tự thêm `UdpNetworkTransport` khi khởi động, nhưng gán transport ngay trong scene giúp lựa chọn này hiện rõ.

## 2. Viết một model <a href="#2-write-a-model" id="2-write-a-model"></a>

Model là một class C# mà package có thể gửi đi. Ở đây state của người chơi chỉ là một bộ đếm. Tạo `Assets/Network/Models/PlayerStats.cs`:

```csharp
using Fomoxa;
using Fomoxa.Unity;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class PlayerStats
    {
        [Network("u32")]
        [Codec("net")]
        public uint Jumps { get; set; }
    }
}
```

`[Network]` và `[Codec("net")]` trên class biến nó thành một model có codec tên `net`. Mỗi property mang wire type của nó, ở đây là `u32`, và codec mà nó thuộc về. `[NetworkChannel]` đặt model lên channel reliable có thứ tự, điều mà state model bắt buộc phải có. [Model và codec](../messaging/models.md) giải thích chi tiết các attribute này.

Lưu file và để Unity biên dịch. Package sinh `PlayerStatsNetAdapter` trong `Assets/Network/Generated`, và vì code ở bước tiếp theo dùng tới nó, hãy chờ file này xuất hiện rồi mới làm tiếp.

## 3. Viết behaviour cho người chơi <a href="#3-write-the-player-behaviour" id="3-write-the-player-behaviour"></a>

Tạo `Assets/Network/Player.cs`:

```csharp
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

namespace MyGame.Network
{
    public sealed partial class Player : NetworkBehaviour
    {
        private readonly PlayerStats stats = new PlayerStats();

        protected override void OnRegisterState(NetworkState state)
        {
            state.Use(PlayerStatsNetAdapter.Instance, stats, OnStatsChanged);
        }

        public override void OnStartClient()
        {
            Debug.Log($"player {NetworkObject.ObjectId} spawned, owner {NetworkObject.OwnerId}, mine: {NetworkObject.IsOwner}, jumps: {stats.Jumps}");
        }

        private void OnGUI()
        {
            if (NetworkObject != null && NetworkObject.IsOwner && GUILayout.Button("Jump"))
            {
                SendServerRpc(nameof(Jump));
            }
        }

        [ServerRpc]
        private void Jump()
        {
            transform.position += Vector3.up;
            stats.Jumps++;
        }

        private void OnStatsChanged(PlayerStats previous)
        {
            Debug.Log($"player {NetworkObject.ObjectId} jumps: {previous.Jumps} -> {stats.Jumps}");
        }
    }
}
```

`OnRegisterState` đăng ký `stats` làm state của behaviour. Server gửi nó mỗi khi nó thay đổi, và mỗi client decode nó vào cùng field đó rồi gọi `OnStatsChanged` với giá trị trước đó. `OnStartClient` chạy trên client khi object xuất hiện ở đó, và lúc đó state đã chứa giá trị của server.

Nút Jump chỉ được vẽ trên client của owner. Bấm vào nó sẽ gọi `SendServerRpc(nameof(Jump))`, yêu cầu server chạy `Jump`. Attribute `[ServerRpc]` đánh dấu `Jump` là method server chạy khi một client gọi nó, và mặc định chỉ owner được gọi. Class là `partial` vì package sinh code đăng ký RPC.

Bản thân `Jump` chạy trên server. Nó di chuyển transform, thứ được `NetworkTransform` gửi tới client, và thay đổi state, thứ được package gửi đi vào cuối tick.

Khi Unity biên dịch file này, package sinh một model cho RPC không tham số tại `Assets/Network/Generated/RpcModels/PlayerJump.cs` và đăng ký nó, sau đó Unity biên dịch lần thứ hai với các file mới.

## 4. Tạo prefab người chơi <a href="#4-make-the-player-prefab" id="4-make-the-player-prefab"></a>

1. Trong scene, tạo một Capsule (GameObject > 3D Object > Capsule) và đặt tên là `Player`.
2. Thêm ba component vào nó: `NetworkObject`, `NetworkTransform` và `Player`.
3. Kéo nó vào `Assets/Prefabs` để tạo prefab, rồi xóa nó khỏi scene.
4. Chọn Tools > Fomoxa > Assign Prefab Ids.

Bước cuối gán cho prefab một prefab id, thứ server và client dùng để thống nhất cần spawn gì, và ghi `Assets/Network/Generated/FomoxaPrefabList.asset`. Chọn prefab và kiểm tra field Prefab Id của `NetworkObject` khác 0. Package cũng tự chạy bước này mỗi khi một prefab được lưu trong Editor và trước mỗi lần build player.

`NetworkObject` phải nằm ở gốc prefab, và prefab không được chứa `NetworkObject` thứ hai.

## 5. Gán các danh sách đã sinh cho NetworkManager <a href="#5-give-the-networkmanager-the-generated-lists" id="5-give-the-networkmanager-the-generated-lists"></a>

Chọn `Network Manager` và kéo hai asset đã sinh vào:

- `Assets/Network/Generated/FomoxaPrefabList.asset` vào Collected Prefabs.
- `Assets/Network/Generated/FomoxaSceneList.asset` vào Collected Scenes.

`NetworkManager` đăng ký mọi prefab trong danh sách khi khởi động. Bản build player tự gán cả hai danh sách trong lúc build, nhưng trong Editor việc gán đó xảy ra sau khi `NetworkManager` đã khởi động, nên hãy gán chúng trong scene. Nếu thiếu, việc spawn sẽ thất bại với `prefab id 0x... of Player(Clone) is not registered`.

Lưu scene.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Project biên dịch không lỗi.
- `Assets/Network/Generated` chứa `PlayerStatsNetAdapter.cs`, `PlayerJumpNetAdapter.cs`, `RpcModels/PlayerJump.cs`, `FomoxaPrefabList.asset` và `FomoxaPrefabs.cs`.
- `FomoxaPrefabs.cs` có các hằng số `PlayerId` và `PlayerFingerprint`.
- Vào Play Mode chưa thấy gì xảy ra, vì `NetworkManager` đứng yên cho tới khi code khởi động server hoặc client.

Tiếp theo là [server đầu tiên](first-server.md).
