# Rollback với physics

Khi một object được dự đoán di chuyển bằng `Rigidbody` hoặc `Rigidbody2D`, kết quả của nó phụ thuộc vào cả physics world, gồm các body khác, contact và trọng lực. Vì vậy sửa nó nghĩa là rollback physics world về tick được sửa rồi step tiếp từ đó, việc package làm khi Simulate Physics đang bật.

## Yêu cầu <a href="#requirements" id="requirements"></a>

Simulate Physics phải bật, cả trên server lẫn client, để `NetworkManager` step physics mỗi tick một lần (xem [physics](../physics/overview.md)). Object được dự đoán phải có `Rigidbody` hoặc `Rigidbody2D` trên cùng GameObject với `NetworkObject` của nó. `apply` di chuyển body bằng lực, xung lực hoặc vận tốc, còn `capture` và `restore` đọc và ghi body qua `NetworkObject.Body` hoặc `Body2D`:

```csharp
private void Apply(MoveInput input, InputContext context)
{
    var push = new System.Numerics.Vector3(input.X, 0f, input.Z) * pushStrength;
    NetworkObject.Body.AddImpulse(push);
}

private void Capture(BodyMotion state)
{
    BodyState body = NetworkObject.Body.State;
    state.X = body.Position.X;
    state.Z = body.Position.Z;
    state.VelocityX = body.Velocity.X;
    state.VelocityZ = body.Velocity.Z;
}

private void Restore(BodyMotion state)
{
    PhysicsBody body = NetworkObject.Body;
    BodyState current = body.State;
    current.Position = new System.Numerics.Vector3(state.X, current.Position.Y, state.Z);
    current.Velocity = new System.Numerics.Vector3(state.VelocityX, current.Velocity.Y, state.VelocityZ);
    body.State = current;
}

private static bool Matches(BodyMotion server, BodyMotion predicted) =>
    Math.Abs(server.X - predicted.X) <= 0.01f
    && Math.Abs(server.Z - predicted.Z) <= 0.01f
    && Math.Abs(server.VelocityX - predicted.VelocityX) <= 0.05f
    && Math.Abs(server.VelocityZ - predicted.VelocityZ) <= 0.05f;
```

`BodyMotion` là một model có bốn property `f32`, `X`, `Z`, `VelocityX` và `VelocityZ`. `BodyState` và `PhysicsBody` nằm trong `Fomoxa.Unity.Simulation`, và `Math` là `System.Math`. Ví dụ di chuyển trên mặt phẳng nền và để trục dọc cho trọng lực.

## Dòng thời gian <a href="#timeline" id="timeline"></a>

Mỗi tick, sau khi step physics, client của owner lưu state của mỗi physics world chứa một object nó dự đoán và ghi lại state của mỗi behaviour được dự đoán. Lịch sử giữ Prediction History tick (mặc định 64).

```
T0 → T1 → T2 → T3 → T4                  client has predicted up to T4
             ↑
        server state for T2 does not match

Load(T2)                                 every world of the group goes back to T2
restore(server state for T2)
T2 → T3 → T4                             apply input, step every world, capture, save
```

Với mỗi tick của lần replay, từ T3 tới T4, `apply` chạy cho mọi object được dự đoán của nhóm rồi mỗi world step một lần.

## Rollback group <a href="#rollback-groups" id="rollback-groups"></a>

Một lần replay bao một rollback group, tức tập các physics world mà các object client dự đoán nằm trong đó.

```
Rollback group
 ├── 3D world of scene A
 ├── 3D world of scene B        scenes A and B share one physics scene, so they are one world
 └── 2D world of scene A
```

Mỗi scene có object được dự đoán đưa 3D world và 2D world của nó vào một nhóm. Hai scene dùng chung một physics scene của Unity cũng dùng chung một world, và các nhóm của chúng gộp lại, còn các nhóm không chung world nào được sửa độc lập với nhau.

Tick của một lần sửa là tick mới nhất có state của server trong số các behaviour của nhóm. Mọi object được dự đoán của nhóm đều replay, kể cả những object có state riêng đã khớp, vì chúng nằm trong các world bị đưa lùi lại.

## Không load một phần <a href="#no-partial-loads" id="no-partial-loads"></a>

Một nhóm chỉ được load khi mọi world trong đó có state đã lưu cho tick được sửa, vì load một số world mà không load các world khác sẽ đặt các object của cùng một mô phỏng ở những tick khác nhau. Nếu một world thiếu tick đó, ví dụ vì scene của nó được load sau, sẽ không world nào của nhóm được load. Client vẫn khôi phục state của server và replay input, bắt đầu từ state hiện tại của các world, nhưng không lưu các tick được replay.

## State đã lưu chứa gì <a href="#what-a-saved-state-contains" id="what-a-saved-state-contains"></a>

Với mỗi world, state đã lưu giữ vị trí, góc xoay, vận tốc, vận tốc góc và trạng thái ngủ của mọi body dynamic không phải proxy. Body kinematic không được lưu. Body của các object mà client không dự đoán là proxy: client biến chúng thành kinematic và đặt chúng vào vị trí `NetworkTransform` mỗi tick, nên chúng không bị rollback và giữ nguyên chỗ client đang hiển thị.

Spawn và despawn cũng không được replay. Body tạo sau một tick đã lưu giữ state hiện tại khi tick đó được load, và body bị hủy sau tick đó không được tạo lại.

Dữ liệu contact của physics engine không được lưu, nên một lần replay có thể khác lần chạy đầu dù input giống hệt. Hãy chấp nhận thỉnh thoảng có lần sửa, và dùng dung sai trong `matches`.

## Contact event trong lúc replay <a href="#contact-events-during-a-replay" id="contact-events-during-a-replay"></a>

[Các component contact](../physics/contacts.md) ghi lại contact của mỗi tick. Một lần replay khôi phục contact của tick được sửa và cập nhật chúng khi các world step. Chỉ sau khi replay xong nó mới phát event enter và exit, một lần, cho phần khác biệt so với những gì đã hiển thị, nên cùng một event không bao giờ được phát hai lần.

## Server và host <a href="#server-and-host" id="server-and-host"></a>

Server không lưu hay load physics mà chỉ step mỗi world một lần mỗi tick. Host không dự đoán object của chính nó nên không bao giờ rollback.

Rollback mở rộng [reconciliation](reconciliation.md) sang physics. [Tổng quan physics](../physics/overview.md) và [PhysicsBody](../physics/physics-body.md) mô tả các body liên quan, và [mô phỏng tất định](../khai-niem/deterministic-simulation.md) giải thích vì sao rollback physics của Unity chỉ gần đúng.
