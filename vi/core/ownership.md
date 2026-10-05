# Ownership

Mọi object đã spawn đều có một owner, là peer id của một client hoặc 0 khi server sở hữu object. Owner là client mà object thuộc về, thường là người chơi điều khiển nhân vật đó. Ownership không chuyển authority sang client đó, như [authority](../concepts/authority.md) giải thích.

## Owner được gì <a href="#what-the-owner-gets" id="what-the-owner-gets"></a>

Owner được gọi server RPC của object, còn client khác chỉ được gọi những RPC khai báo `RequireOwnership = false`. Nếu object có input model, owner dự đoán nó, và server chỉ chấp nhận input cho object từ owner.

Owner cũng luôn observe object, bất kể observer rule nói gì, miễn là nó đã load network scene chứa object. Với [`DistanceRule`](observers.md#distancerule), các object mà một peer sở hữu là những điểm từ đó nó observe mọi thứ khác.

## Đặt owner <a href="#setting-the-owner" id="setting-the-owner"></a>

Bạn truyền owner khi spawn:

```csharp
manager.ServerManager.Spawn(player, peerId);
```

Để đổi owner sau đó, gọi `ChangeOwner` trên server:

```csharp
bool changed = manager.ServerManager.ChangeOwner(car, driverPeerId);
```

`ChangeOwner` trả về false khi server này không spawn object đó hoặc khi owner mới không phải một peer đang kết nối ở trạng thái `Started`. Truyền 0 sẽ trao object cho server.

Sau khi đổi, server gọi `OnOwnerChangedServer(previousOwnerId)` và mọi client đang observe gọi `OnOwnerChangedClient(previousOwnerId)`. Owner mới bắt đầu observe object nếu trước đó chưa observe, và owner cũ không còn thỏa observer rule sẽ thôi observe.

Đổi owner cũng đặt lại prediction. Server bỏ input đã đệm cho object, owner cũ thôi dự đoán nó, và owner mới bắt đầu dự đoán khi server đã gửi cho nó state đầu tiên.

## Đọc owner <a href="#reading-the-owner" id="reading-the-owner"></a>

| Member | Ở đâu | Ý nghĩa |
|---|---|---|
| `NetworkObject.OwnerId` | Server và client | Peer id của owner, 0 với server |
| `NetworkObject.IsOwner` | Client | True trên client của owner, kể cả client của host |

## Khi owner ngắt kết nối <a href="#when-the-owner-disconnects" id="when-the-owner-disconnects"></a>

Mặc định server despawn mọi object thuộc về peer vừa ngắt kết nối. Để giữ object lại, hãy tắt Despawn With Owner trên `NetworkObject` hoặc đặt `DespawnWithOwner = false` từ code. Object khi đó chuyển sang do server sở hữu, và `OnOwnerChangedServer` chạy với owner cũ làm `previousOwnerId`.

```csharp
public override void OnOwnerChangedServer(ulong previousOwnerId)
{
    if (NetworkObject.OwnerId == 0)
    {
        Debug.Log($"{name} lost its owner {previousOwnerId} and stays in the world");
    }
}
```

Ownership là một thuộc tính của [NetworkObject](network-object.md), và các hướng dẫn [RPC](../messaging/rpc.md) và [input](../prediction/input.md) mô tả chi tiết hơn các phép kiểm tra ownership.
