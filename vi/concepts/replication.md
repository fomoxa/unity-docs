# Replication

Replication là cách các object của server và dữ liệu của chúng tới được client. Mọi thứ đều được gửi từ server, và mỗi client chỉ nhận các object mà nó observe.

## Client nhận gì về một object <a href="#what-a-client-receives-about-an-object" id="what-a-client-receives-about-an-object"></a>

| Sự kiện trên server | Message gửi tới observer | Channel |
|---|---|---|
| `ServerManager.Spawn` | Message spawn: object id, prefab id hoặc scene object id, prefab fingerprint, owner, vị trí, góc xoay và tỉ lệ, state ban đầu của mọi behaviour, và network scene | Reliable ordered |
| Một state model thay đổi | State mới, dưới dạng bản đầy đủ hoặc delta | Reliable ordered |
| Một `NetworkTransform` di chuyển | Cập nhật transform kèm tick | Unreliable |
| Một `NetworkTransform` dừng, được spawn hoặc teleport | Message settle chứa transform cuối cùng | Reliable ordered |
| Parameter của `NetworkAnimator` thay đổi | State của animator, qua cơ chế state | Reliable ordered |
| Một RPC tới các observer | Chính RPC đó | Channel của RPC |
| `ServerManager.ChangeOwner` | Thông báo đổi owner | Reliable ordered |
| `ServerManager.Despawn`, hoặc client thôi observe | Despawn | Reliable ordered |

Message reliable tới theo đúng thứ tự server gửi, nên client luôn có object trước mọi thay đổi state của nó và không bao giờ nhận thay đổi state sau khi despawn. Message unreliable cho một object mà client không có sẽ bị bỏ qua.

## Spawn trên client <a href="#spawning-on-the-client" id="spawning-on-the-client"></a>

Khi một message spawn tới, client đi qua ba bước.

1. Nó tìm prefab theo prefab id, hoặc scene object theo scene object id, và so sánh fingerprint, thứ mô tả danh sách các type `NetworkBehaviour`. Prefab bị thiếu hoặc khác sẽ khiến client dừng với `PrefabMismatch`.
2. Nó instantiate prefab tại vị trí và góc xoay của message spawn và đặt tỉ lệ, hoặc kích hoạt scene object rồi đặt nó vào chỗ.
3. Nó gọi các callback đăng ký của mọi `NetworkBehaviour`, áp dụng state ban đầu rồi gọi `OnStartClient`.

Trên host, client không tạo instance thứ hai mà dùng luôn instance của server, như mô tả trong [host mode](../core/host-mode.md).

## Client vào muộn <a href="#clients-that-join-late" id="clients-that-join-late"></a>

Client kết nối sau khi các object đã được spawn sẽ nhận một message spawn cho mỗi object nó observe ngay khi tới `Started`. Message đó mang transform hiện tại của object và state cuối cùng server đã chụp, nên client vào muộn bắt đầu từ giá trị hiện tại chứ không phải giá trị lúc spawn ban đầu.

## Observer quyết định ai được nhận <a href="#observers-decide-who-receives" id="observers-decide-who-receives"></a>

Với mỗi object, server giữ tập các peer observe nó. Peer vào tập sẽ nhận spawn, peer rời tập sẽ nhận despawn, còn state, transform và RPC tới observer chỉ đi tới các peer trong tập. Owner của object luôn observe nó, trừ khi object nằm trong một network scene mà owner chưa load. [Observer](../core/observers.md) giải thích cách xây tập này.

## Những gì không được replicate <a href="#what-is-not-replicated" id="what-is-not-replicated"></a>

Chỉ những gì các component của package và model của bạn gửi đi mới được replicate. Component khác, field của MonoBehaviour thông thường, object con tạo lúc chạy và material đều chỉ ở cục bộ, nên hãy đặt dữ liệu client cần vào một [state model](../synchronization/state.md) hoặc gửi nó bằng [RPC](../messaging/rpc.md).

Một `NetworkObject` có thể có các component `NetworkBehaviour` trên object con, kể cả `NetworkTransform`, và mỗi `NetworkTransform` replicate vị trí, góc xoay và tỉ lệ local của GameObject chứa nó.

Các hướng dẫn về [spawn](../core/spawning.md), [state](../synchronization/state.md) và [NetworkTransform](../synchronization/transform.md) đi vào chi tiết từng loại message, còn [authority](authority.md) giải thích vì sao mọi thứ đều đi từ server.
