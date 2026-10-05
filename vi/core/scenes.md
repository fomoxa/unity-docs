# Network scene

Network scene là scene mà server load theo kiểu additive, cả trên chính nó lẫn trên các client được chọn. Một scene có thể là global, tức được load cho mọi client, hoặc chỉ được load cho một số peer, như những người chơi bên trong một dungeon. Object trong network scene, kể cả object được spawn vào đó, chỉ tới các peer đã load scene.

Scene mà game khởi động cùng không phải network scene. Hai bên mở nó theo cách thông thường, và các scene object của nó hiển thị với mọi peer thỏa observer rule.

## Scene id <a href="#scene-ids" id="scene-ids"></a>

Server và client nhận diện một network scene bằng scene id, một hash 32 bit của asset GUID của scene. Editor ghi các id vào hai file. `FomoxaSceneList.asset` chứa id và đường dẫn của mọi scene trong Scene List của Build Profiles và được làm mới mỗi khi danh sách đó hoặc một scene asset thay đổi. `FomoxaScenes.cs` chứa một hằng số `<SceneName>Id` cho mọi scene asset dưới `Assets`, kể cả scene nằm ngoài danh sách build.

Gán `FomoxaSceneList.asset` vào Collected Scenes trên `NetworkManager`. Manager sau đó đăng ký mỗi scene trong danh sách với một loader gọi `SceneManager.LoadSceneAsync(path, LoadSceneMode.Additive)` và `UnloadSceneAsync`, và `NetworkManager.Scenes.IdOf("Assets/Scenes/Arena.unity")` trả về id của một scene trong danh sách, hoặc 0 nếu scene không có trong đó.

## Load scene cho mọi người <a href="#load-a-scene-for-everyone" id="load-a-scene-for-everyone"></a>

```csharp
manager.ServerManager.Scenes.LoadGlobal(new[] { FomoxaScenes.ArenaId });
```

Server load scene trước rồi báo mọi peer đã khởi động load nó, và peer kết nối sau sẽ load mọi global scene khi khởi động. `LoadGlobal(sceneIds, replace: true)` unload các global scene hiện tại trước khi load scene mới.

`UnloadGlobal(sceneIds)` unload các global scene và ném exception với id không phải global scene.

## Load scene cho một số peer <a href="#load-a-scene-for-some-peers" id="load-a-scene-for-some-peers"></a>

```csharp
int added = manager.ServerManager.Scenes.LoadForPeers(FomoxaScenes.DungeonId, new[] { peerA, peerB });
```

`LoadForPeers` trả về số peer nó đã thêm, bỏ qua các peer chưa khởi động hoặc đã có scene. Server tự load scene cho chính nó ở lần đầu tiên có peer nhận scene đó.

`UnloadForPeers(sceneId, peerIds)` gỡ scene khỏi các peer đó, và khi peer cuối cùng bị gỡ, server despawn các object của scene rồi unload nó. `Unload(sceneId)` gỡ một scene theo peer khỏi mọi peer cùng lúc.

Một scene hoặc là global, hoặc là theo peer, không bao giờ cả hai. `LoadForPeers` ném exception với global scene, và `LoadGlobal` với một scene theo peer sẽ biến nó thành global.

## Object trong network scene <a href="#objects-in-network-scenes" id="objects-in-network-scenes"></a>

Khi server load xong một network scene, nó spawn các scene object trong đó, và khi unload scene, nó despawn mọi object trong scene.

Object mà server spawn vào một network scene, bằng cách chuyển nó vào đó trước khi gọi `Spawn`, chỉ tới các peer đã load scene, như trong [spawn](spawning.md#spawning-into-a-network-scene). Một peer chỉ bắt đầu observe object như vậy sau khi client của nó báo đã load xong scene.

## Event và truy vấn trên server <a href="#server-events-and-queries" id="server-events-and-queries"></a>

| Member                                            | Ý nghĩa                                               |
| ------------------------------------------------- | ----------------------------------------------------- |
| `OnLoaded(uint sceneId)`                          | Server đã load xong một network scene                 |
| `OnLoadFailed(uint sceneId, Exception exception)` | Server không load được scene; exception cũng được log |
| `Global`                                          | Các global scene id                                   |
| `Contains(sceneId)`                               | Scene là global hoặc đã load cho một peer nào đó      |
| `IsGlobal(sceneId)`                               | Scene là global                                       |
| `HasLoaded(peerId, sceneId)`                      | Client của peer đã báo load xong scene                |
| `PeersOf(sceneId)`                                | Các peer có scene                                     |
| `TryGetScene(sceneId, out Scene scene)`           | `Scene` của Unity mà server đã load                   |

Mọi member này nằm trên `ServerManager.Scenes`.

## Trên client <a href="#on-the-client" id="on-the-client"></a>

Client load và unload từng scene một, theo thứ tự server yêu cầu, và báo cho server mỗi lần load xong. Nếu một lần load thất bại, client log exception và dừng với `PrefabMismatch`, phát `OnObjectMismatch` với loại `UnknownScene`. Khi kết nối dừng, client giữ lại các scene đã load.

Client của host dùng các scene server đã load thay vì load lại.

## Loader tùy chỉnh <a href="#custom-loaders" id="custom-loaders"></a>

Scene không có trong danh sách build, như một scene Addressables, cần loader riêng, đăng ký trên server và trên mọi client:

```csharp
using System;
using Fomoxa.Unity;
using Generated;
using UnityEngine.SceneManagement;

public sealed class ArenaLoader : ISceneLoader
{
    public void Load(Action<Scene> loaded, Action<Exception> failed)
    {
        var operation = SceneManager.LoadSceneAsync("Arena", LoadSceneMode.Additive);
        operation.completed += _ => loaded(SceneManager.GetSceneByName("Arena"));
    }

    public void Unload(Scene scene, Action unloaded)
    {
        SceneManager.UnloadSceneAsync(scene).completed += _ => unloaded();
    }
}
```

```csharp
manager.Scenes.Register(FomoxaScenes.ArenaId, new ArenaLoader());
```

Loader gọi `loaded` với scene đã load hoặc `failed` với một exception, và gọi `unloaded` khi unload xong. Hãy đăng ký nó trước khi server hoặc client cần scene, vì `LoadGlobal` và `LoadForPeers` ném `scene 0x... is not in the scene registry` với id chưa đăng ký. Scene id 0 không đăng ký được.

## Giới hạn <a href="#limitations" id="limitations"></a>

Mỗi phía load một scene asset nhiều nhất một lần tại một thời điểm. Mọi lần load scene đều là additive, và package không đổi active scene cũng không unload scene khởi động.

Network scene tham gia vào việc quyết định [observer](observers.md) và vào việc [spawn](spawning.md), còn [tham chiếu ServerManager](../tham-chieu/server-manager.md) liệt kê các member về scene.
