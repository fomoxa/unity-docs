# Spawn

Spawn làm cho một object tồn tại trên mạng. Server spawn một instance, mỗi client observe nó tạo instance riêng từ cùng prefab, và despawn sẽ gỡ object khỏi mọi nơi. Object đặt sẵn trong scene cũng được spawn, chỉ là không cần instantiate gì.

## Prefab id và prefab registry <a href="#prefab-ids-and-the-prefab-registry" id="prefab-ids-and-the-prefab-registry"></a>

Server và client nhận diện một prefab bằng prefab id, một số 32 bit lưu trong `NetworkObject` của nó. Editor tính id từ asset GUID của prefab mỗi khi prefab được lưu, khi bạn chọn Tools > Fomoxa > Assign Prefab Ids, và trước mỗi lần build player, và báo lỗi khi hai prefab có cùng id.

Để giữ một id cố định, ví dụ khi GUID của prefab sắp thay đổi, hãy bật Explicit Prefab Id và tự nhập id. Prefab id 0 không được phép.

Cùng với id, Editor ghi `FomoxaPrefabList.asset`, danh sách mọi prefab có `NetworkObject` dưới `Assets`, và `FomoxaPrefabs.cs`, chứa một cặp hằng số cho mỗi prefab, như `PlayerId` và `PlayerFingerprint`.

`NetworkManager` chỉ spawn được các prefab đã đăng ký trong registry `Prefabs` của nó. Trong `Awake`, nó đăng ký các prefab trong danh sách Prefabs, và các prefab của Collected Prefabs khi Collect Prefabs đang bật. Bạn cũng có thể đăng ký một prefab lúc chạy, trước lần spawn đầu tiên của nó:

```csharp
manager.Prefabs.Register(bulletPrefab);
```

Đăng ký cùng một prefab hai lần không có tác dụng gì, nhưng đăng ký một prefab khác dưới một id đã có chủ sẽ ném exception.

## Spawn <a href="#spawn" id="spawn"></a>

Việc spawn diễn ra trên server:

```csharp
NetworkObject player = Instantiate(playerPrefab, spawnPoint, Quaternion.identity);
manager.ServerManager.Spawn(player, peerId);
```

`Spawn(networkObject, ownerId = 0)` cần server đã khởi động, nếu không nó ném `the server is not started`. Object phải là instance trong scene chứ không phải asset prefab, chưa được spawn, và có prefab id đã đăng ký. Owner phải là 0 hoặc một peer đang kết nối ở trạng thái `Started`.

Message spawn mang vị trí và góc xoay world, tỉ lệ local và state ban đầu của mỗi behaviour đúng như lúc gọi `Spawn`, nên hãy đặt vị trí và state cho object trước khi gọi. Client instantiate prefab tại vị trí và góc xoay đó, đặt tỉ lệ và gọi `OnStartClient`.

## Despawn <a href="#despawn" id="despawn"></a>

```csharp
manager.ServerManager.Despawn(player);
```

`Despawn` gọi `OnStopServer`, báo cho các observer và hủy instance, hoặc trả về false khi server này không spawn object đó. Hủy một `GameObject` đã spawn trên server cũng despawn nó.

Server còn tự despawn object trong các trường hợp: object thuộc về client vừa ngắt kết nối, trừ khi Despawn With Owner tắt; object trong network scene mà server unload; và tất cả object khi server dừng.

## Scene object <a href="#scene-objects" id="scene-objects"></a>

`NetworkObject` đặt trực tiếp trong scene là scene object. Editor gán cho nó một scene object id khi scene được lưu và kiểm tra các id trước khi build. Trong Play Mode, scene object chưa được lưu sẽ nhận id tạm và package log một cảnh báo, nên hãy lưu scene để mọi bản build dùng cùng các id.

Server tự động spawn scene object: các object trong scene đã load khi server khởi động, và các object trong một [network scene](scenes.md) khi scene đó load xong. Trên client, scene object bị tắt khi kết nối bắt đầu và được bật khi message spawn của chúng tới. Despawn tắt scene object thay vì hủy nó, và `ServerManager.Spawn` nhận một scene object đã despawn để spawn lại.

Client phải mở cùng scene đó, với các scene object có cùng id và cùng behaviour. Nếu không, nó dừng với `PrefabMismatch` (`UnknownSceneObject` hoặc `IncompatibleSceneObject`).

## Spawn vào một network scene <a href="#spawning-into-a-network-scene" id="spawning-into-a-network-scene"></a>

Object spawn trong một network scene chỉ tới các peer đã load scene đó. Để spawn vào đó, hãy chuyển instance vào scene trước khi gọi `Spawn`:

```csharp
if (manager.ServerManager.Scenes.TryGetScene(FomoxaScenes.ArenaId, out Scene arena))
{
    NetworkObject enemy = Instantiate(enemyPrefab, position, Quaternion.identity);
    SceneManager.MoveGameObjectToScene(enemy.gameObject, arena);
    manager.ServerManager.Spawn(enemy);
}
```

Mỗi client sau đó đặt instance của nó vào bản copy scene của riêng mình.

## Factory và pooling <a href="#factories-and-pooling" id="factories-and-pooling"></a>

Một prefab id cũng có thể được đăng ký kèm factory thay cho prefab. Factory tạo và trả lại instance trên client, cho phép dùng pooling:

```csharp
using System.Collections.Generic;
using Fomoxa.Unity;
using Generated;
using UnityEngine;

public sealed class BulletPool : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private NetworkObject bulletPrefab;

    private readonly Stack<NetworkObject> idle = new Stack<NetworkObject>();

    private void Start()
    {
        manager.Prefabs.Register(FomoxaPrefabs.BulletId, FomoxaPrefabs.BulletFingerprint, Take, Return);
    }

    private NetworkObject Take(Vector3 position, Quaternion rotation)
    {
        NetworkObject bullet = idle.Count > 0 ? idle.Pop() : Instantiate(bulletPrefab);
        bullet.transform.SetPositionAndRotation(position, rotation);
        bullet.gameObject.SetActive(true);
        return bullet;
    }

    private void Return(NetworkObject bullet)
    {
        bullet.gameObject.SetActive(false);
        idle.Push(bullet);
    }
}
```

Client gọi `Take` khi một message spawn của prefab id đó tới và `Return` khi object bị despawn. Hằng số fingerprint lấy từ `FomoxaPrefabs.cs` và phải khớp với prefab mà server spawn, và `Take` phải trả về một instance chưa được spawn.

Factory chỉ áp dụng trên client. Trên server, `Spawn` vẫn nhận instance do bạn tạo, và `Despawn` hủy nó.

Mỗi prefab id chỉ đăng ký được một lần, nên factory cho một prefab cũng có trong Collected Prefabs sẽ ném `prefab id 0x... is already registered`. Khi đó, hãy tắt Collect Prefabs và liệt kê các prefab còn lại trong field Prefabs, hoặc đăng ký factory trên một manager mà danh sách của nó không chứa prefab đó.

## Giới hạn <a href="#limitations" id="limitations"></a>

`NetworkObject` lồng nhau không được hỗ trợ, và mỗi `NetworkManager` có prefab registry riêng. Client không thể spawn object; nó yêu cầu server spawn bằng một RPC.

Về object được spawn, xem [NetworkObject](network-object.md), [ownership](ownership.md) và [observer](observers.md). [Tham chiếu ServerManager](../tham-chieu/server-manager.md) liệt kê các member liên quan tới spawn, và [tích hợp Editor](../unity/editor-integration.md) mô tả cách Editor gán id.
