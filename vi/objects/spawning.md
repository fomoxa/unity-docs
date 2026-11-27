# Spawn

Spawn làm cho một object tồn tại trên mạng. Server spawn một instance, mỗi client observe nó tạo instance riêng từ cùng prefab, và despawn sẽ gỡ object khỏi mọi nơi. Object đặt sẵn trong scene cũng được spawn, chỉ là không cần instantiate gì.

<figure><img src="../.gitbook/assets/diagrams/spawn-flow.svg" alt="Ba cột. Trong Editor, lưu một prefab cho nó một Prefab Id lấy từ GUID, và Editor ghi FomoxaPrefabList.asset và FomoxaPrefabs.cs. Trên server, Awake đăng ký các prefab trong danh sách đó, code của bạn instantiate prefab, đặt vị trí và gán state, rồi Spawn(instance, owner) cấp object id và gọi OnStartServer. Server gửi một message spawn tin cậy, có thứ tự, mang object id, prefab id, fingerprint, owner, vị trí, góc xoay, tỉ lệ và state. Mỗi client đang observe đã đăng ký cùng các prefab trong Awake, tìm theo prefab id, so fingerprint, instantiate prefab, áp state và gọi OnStartClient."><figcaption><p>Đường đi của một prefab từ Editor tới mọi client observe nó.</p></figcaption></figure>

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

Object spawn trong một network scene chỉ tới các peer đã load bản đó của scene. Để spawn vào đó, hãy chuyển object vào `Scene` của bản trước khi gọi `Spawn`. `arenaInstance` là `NetworkScene` mà `LoadGlobal` hoặc `Load` trả về:

```csharp
if (manager.ServerManager.Scenes.TryGetScene(arenaInstance, out Scene arena))
{
    NetworkObject enemy = Instantiate(enemyPrefab, position, Quaternion.identity);
    SceneManager.MoveGameObjectToScene(enemy.gameObject, arena);
    manager.ServerManager.Spawn(enemy);
}
```

Mỗi client sau đó đặt object của nó vào bản scene đó ở phía mình. Sau khi spawn, hãy chuyển object sang bản khác bằng [`MoveToScene`](scenes.md#move-an-object-to-another-instance); lời gọi này báo cho cả client.

## Factory và pooling <a href="#factories-and-pooling" id="factories-and-pooling"></a>

Một prefab có thể có factory tạo và trả lại instance của nó trên client, cho phép dùng pooling:

```csharp
using System.Collections.Generic;
using Fomoxa.Unity;
using UnityEngine;

public sealed class BulletPool : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private NetworkObject bulletPrefab;

    private readonly Stack<NetworkObject> idle = new Stack<NetworkObject>();

    private void Start()
    {
        manager.Prefabs.SetFactory(bulletPrefab, Take, Return);
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

Client gọi `Take` khi một message spawn của prefab viên đạn tới và `Return` khi object bị despawn. `Take` phải trả về một instance chưa được spawn.

`SetFactory` đọc prefab id và fingerprint từ chính prefab. Prefab có thể đã nằm trong Collected Prefabs hoặc field Prefabs, và `SetFactory` chạy trước hay sau `Awake` của `NetworkManager` đều cho cùng kết quả. Mỗi prefab có nhiều nhất một factory: gọi `SetFactory` lần nữa với factory khác sẽ ném `<prefab> already has a factory`.

Factory chỉ áp dụng trên client. Trên server, `Spawn` vẫn nhận instance do bạn tạo, và `Despawn` hủy nó.

Nếu client không có tham chiếu tới prefab, ví dụ vì nó nạp prefab sau từ Addressables, hãy đăng ký factory theo id: `manager.Prefabs.Register(FomoxaPrefabs.BulletId, FomoxaPrefabs.BulletFingerprint, Take, Return)`. Các hằng số lấy từ `FomoxaPrefabs.cs`, và fingerprint phải khớp với prefab mà server spawn. Prefab đăng ký theo id như vậy không được nằm thêm trong Collected Prefabs hay field Prefabs.

## Giới hạn <a href="#limitations" id="limitations"></a>

`NetworkObject` lồng nhau không được hỗ trợ, và mỗi `NetworkManager` có prefab registry riêng. Client không thể spawn object; nó yêu cầu server spawn bằng một RPC.

Về object được spawn, xem [NetworkObject](network-object.md), [ownership](ownership.md) và [observer](observers.md). [Tham chiếu ServerManager](../reference/server-manager.md) liệt kê các member liên quan tới spawn, và [tích hợp Editor](../advanced/editor-integration.md) mô tả cách Editor gán id.
