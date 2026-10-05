# Xử lý sự cố Red Runner

Trang này nói về các vấn đề riêng của bản port Red Runner. Mỗi mục trước tiên link tới mục tương ứng của trang [xử lý sự cố](../../getting-started/troubleshooting.md) chung rồi liệt kê các bước kiểm tra áp dụng cho game này.

## Client quay về màn hình bắt đầu sau khi bấm Play <a href="#the-client-returns-to-the-start-screen-after-play" id="the-client-returns-to-the-start-screen-after-play"></a>

Các bước kiểm tra chung nằm ở [client không kết nối được](../../getting-started/troubleshooting.md#client-cannot-connect).

- Server đang chạy, và log của nó hiện `[RedRunner] server listening on UDP port 7777`.
- Ô địa chỉ chứa địa chỉ của server, và server dùng port 7777, port mà client kết nối tới. Server khởi động với `-port` khác sẽ không kết nối được từ màn hình bắt đầu, vì màn hình bắt đầu luôn dùng field Port của `NetworkGame`.
- Max Reconnect Retries là 3, nên client không tới được server sẽ dừng sau ba lần thử lại và màn hình bắt đầu hiện lại.

## Người chơi không được spawn <a href="#the-player-does-not-spawn" id="the-player-does-not-spawn"></a>

Các bước kiểm tra chung nằm ở [object không được spawn](../../getting-started/troubleshooting.md#object-does-not-spawn), và [spawn](../../core/spawning.md) giải thích cơ chế.

- Nếu Console hiện `prefab id 0x... of RedRunner(Clone) is not registered`, hãy kéo `Generated/FomoxaPrefabList.asset` vào Collected Prefabs và `Generated/FomoxaSceneList.asset` vào Collected Scenes trên `NetworkManager` trong `Play.unity`. Trong Editor, package chỉ gán các danh sách này sau `NetworkManager.Awake`, như [bước 03](offline-to-online/step-03-player-spawning.md#configure-the-networkmanager) giải thích.
- `RedRunner.prefab` có `NetworkObject` và prefab id. Chọn Tools > Fomoxa > Assign Prefab Ids sau khi sửa nó.
- `NetworkGame` có `RedRunner.prefab` trong Player Prefab và `NetworkManager` của scene trong Manager.
- Log của server hiện `[RedRunner] spawned a player for peer ...`. Nếu không, client chưa bao giờ tới được `ConnectionState.Started`.

## Level trống hoặc khác nhau giữa các client <a href="#the-level-is-empty-or-differs-between-clients" id="the-level-is-empty-or-differs-between-clients"></a>

Các bước kiểm tra chung nằm ở [state không cập nhật](../../getting-started/troubleshooting.md#state-does-not-update).

- Object `Network Level` có `NetworkObject` và đã được lưu sau khi thêm nó, để nó có scene object id. Scene object giữ trạng thái tắt cho tới khi server spawn chúng.
- `Generation Settings.asset` có Start, Middle và End Blocks Count dương, vì nếu không `Layout` sẽ ném exception, như mô tả trong [bước 02](offline-to-online/step-02-shared-level.md#make-the-level-finite).
- Đồi, mây và các khối nền khác ngẫu nhiên trên mỗi client theo thiết kế, và chỉ phần tiền cảnh đến từ seed.

## Nhân vật của người chơi khác không di chuyển hoặc trượt trong tư thế đứng <a href="#another-players-character-does-not-move-or-slides-in-its-idle-pose" id="another-players-character-does-not-move-or-slides-in-its-idle-pose"></a>

Các bước kiểm tra chung nằm ở [object từ xa bị giật, trễ hoặc không di chuyển](../../getting-started/troubleshooting.md#remote-objects-jitter-lag-or-do-not-move), với nền tảng trong [NetworkTransform](../../synchronization/transform.md) và [authority](../../concepts/authority.md).

- `RedRunner.prefab` có `NetworkTransform` với Sync Scale bật; nếu không, nhân vật không quay đầu.
- Simulate Physics đang bật. Khi bật, body mà client không dự đoán là kinematic và đi theo `NetworkTransform` của nó, còn khi tắt, physics của client tự di chuyển body.
- Nhân vật di chuyển nhưng phát animation đứng yên cần nhánh kinematic trong `RedCharacter.LateUpdate`, nhánh tính tốc độ từ quãng đường đã đi, như trong [bước 05](offline-to-online/step-05-prediction-and-reconciliation.md#animate-characters-you-do-not-control).

## Nhân vật của bạn có cảm giác sai <a href="#your-own-character-feels-wrong" id="your-own-character-feels-wrong"></a>

Các bước kiểm tra chung nằm ở [prediction liên tục bị sửa](../../getting-started/troubleshooting.md#prediction-keeps-correcting), với nền tảng trong [prediction](../../concepts/prediction.md), [tick và thời gian](../../concepts/tick.md) và [reconciliation](../../prediction/reconciliation.md).

- Tick Rate là 50, khớp với fixed timestep 0.02 giây của project.
- `PlayerMotion` có `RunSmoothVelocity`. Nếu thiếu, mỗi lần replay bắt đầu tăng tốc từ một giá trị khác và nhân vật trôi đi sau mỗi lần sửa.
- `RedCharacter.Jump` kiểm tra mặt đất bằng `GroundCheck.Check ()` chứ không phải `IsGrounded`, giá trị cũ một frame trong lúc replay.
- Nếu âm thanh hoặc particle khi nhảy phát hai lần, hãy kiểm tra `Apply` truyền `!context.Replaying` làm `effects`.
- Ở host mode, nhân vật của chính host không được dự đoán và không bao giờ bị sửa, nên hãy test prediction với một server riêng.

## Người chơi bị giật hoặc trượt khi hồi sinh <a href="#a-player-snaps-or-slides-during-a-respawn" id="a-player-snaps-or-slides-during-a-respawn"></a>

Các cơ chế liên quan được mô tả trong [teleport](../../synchronization/transform.md#teleporting), [teleport một PhysicsBody](../../physics/physics-body.md#teleporting) và [reconciliation](../../prediction/reconciliation.md#correction-and-replay).

- Nếu các client khác thấy nhân vật trượt từ chỗ chết về điểm bắt đầu, `NetworkPlayer.Respawn` phải gọi `NetworkTransform.Teleport()` sau khi di chuyển body. Code sinh ra cũng phải khớp với phiên bản package, vì teleport generation đi trong các system model của transform.
- Nếu animator trên các client khác chạy với tốc độ cực lớn trong chốc lát, `RedCharacter.LateUpdate` phải coi một lần di chuyển quá `m_TeleportDistance` là teleport, như trong [bước 08](offline-to-online/step-08-two-clients.md#animate-a-character-that-teleports).
- Nếu nhân vật của owner nhảy về điểm bắt đầu trong một frame, đó là lần sửa đúng như mong đợi. Owner dự đoán nhân vật và coi việc hồi sinh là một reconcile mismatch, và vì Red Runner không dùng field Visual của `NetworkTransform`, lần sửa không được làm mượt.

## Chùy ở chỗ khác nhau trên mỗi client <a href="#the-mace-is-in-a-different-place-on-each-client" id="the-mace-is-in-a-different-place-on-each-client"></a>

`NetworkLevel` phải di chuyển các follower trong `TimeManager.OnPreTick` bằng `PredictionTick`, không phải `Tick`, vì trên client `Tick` đếm tick cục bộ và không phải số của server. [Tick và thời gian](../../concepts/tick.md#three-tick-numbers) giải thích ba số tick.

## Người chơi đã rời vẫn tiếp tục chạy <a href="#a-player-who-left-keeps-running" id="a-player-who-left-keeps-running"></a>

Các cơ chế liên quan được mô tả trong [client](../../core/client.md#connect-and-disconnect) và [input](../../prediction/input.md#on-the-server).

- Nếu người chơi thoát bằng Home hoặc đóng game, client gửi `PeerLeave` và nhân vật phải bị despawn ngay. Nếu không, hãy sinh lại code bằng Tools > Fomoxa > Generate để `PeerLeave` được đăng ký.
- Nếu client bị crash, server chờ heartbeat, khoảng 20 giây với giá trị mặc định. Nhân vật vẫn phải đứng yên sau 10 tick bị lặp; nếu không, hãy kiểm tra quy tắc `RepeatedTicks` trong `NetworkPlayer.Apply` mô tả ở [bước 08](offline-to-online/step-08-two-clients.md#stop-a-character-whose-player-vanished).

## Ô địa chỉ không hiện chữ <a href="#the-address-field-shows-no-text" id="the-address-field-shows-no-text"></a>

Trong bản build player, font của game, `Baloo-Regular`, không vừa với một legacy input field mặc định. Đặt Vertical Overflow thành Overflow trên text và placeholder của ô, như mô tả trong [bước 03](offline-to-online/step-03-player-spawning.md#add-the-address-field).
