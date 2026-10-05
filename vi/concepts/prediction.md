# Prediction

Không có prediction, client thấy kết quả input của chính mình chậm một vòng round trip, vì input phải đi tới server, được áp dụng ở đó rồi quay về. Client-side prediction bỏ độ trễ này cho các object mà client sở hữu: client áp dụng input ngay và tự sửa khi kết quả của server khác đi.

## Vòng lặp <a href="#the-loop" id="the-loop"></a>

```text
Input            the owner's client gathers input for its prediction tick
  ↓
Predict          the client applies the input right away and records the result
  ↓
Simulate         the server applies the same input when its tick comes
  ↓
Receive          the server sends its result for that tick to the owner
  ↓
Reconcile        the client compares the server's result with its record
  ↓
Rollback         on a mismatch, the client restores the server's result
  ↓
Replay inputs    and applies its recorded input again for every later tick
```

## Năm khái niệm hay bị nhầm <a href="#five-terms-that-are-often-confused" id="five-terms-that-are-often-confused"></a>

| Khái niệm | Chạy ở đâu | Là gì |
|---|---|---|
| Server simulation | Server | Server áp dụng input của mỗi client tại tick mà input thuộc về. Kết quả của nó là authoritative state. |
| Client prediction | Client của owner | Client áp dụng input của chính mình trước khi server xác nhận. |
| Authoritative state | Server, gửi tới owner | Kết quả của server cho một tick, được chụp bằng reconcile model. |
| Reconciliation | Client của owner | So sánh authoritative state với dự đoán của cùng tick, và sửa khi không khớp bằng rollback rồi replay. |
| Interpolation | Mọi client, cho các object nó không dự đoán | Hiển thị object ở xa nằm giữa hai vị trí đã nhận, chậm vài tick so với hiện tại. Nó không đoán tương lai và không dùng input. |

Prediction và interpolation áp dụng cho các object khác nhau. Client dự đoán các object mà nó sở hữu và có input model, còn mọi object khác được interpolate qua `NetworkTransform`. Object thôi được dự đoán, ví dụ sau khi đổi owner, sẽ quay về interpolation.

## Yêu cầu <a href="#requirements" id="requirements"></a>

Prediction cần `NetworkManager` dùng timing mode Tick, và object cần một `NetworkBehaviour` đăng ký input model bằng `NetworkInput.Use`. Để dự đoán, behaviour còn cần một reconcile model; nếu không có, client chỉ gửi input.

Callback `apply` phải tính ra cùng kết quả trên server và trên client từ cùng input và cùng state ban đầu, nghĩa là nó chỉ đọc input, state của chính behaviour và `TimeManager.TickDelta`. Tuy vậy kết quả không cần đúng tới từng bit. Hàm `matches` quyết định thế nào là đủ gần, và khác biệt nhỏ chỉ đơn giản được sửa, như [mô phỏng tất định](deterministic-simulation.md) giải thích.

## Hướng dẫn <a href="#guides" id="guides"></a>

[Tổng quan prediction](../prediction/overview.md) xây một nhân vật được dự đoán hoàn chỉnh. [Input](../prediction/input.md) nói về việc thu thập, gửi và áp dụng input, [reconciliation](../prediction/reconciliation.md) nói về việc chụp, khôi phục, so sánh và replay, còn [rollback với physics](../prediction/rollback.md) cho thấy cách rollback các physics world của Unity.
