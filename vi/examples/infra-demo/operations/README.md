# 05: Vận hành cụm

Các việc hằng ngày và các tính năng vận hành: xem log, scale, cập nhật, tắt an toàn (drain), tài khoản, TLS, khoá Nakama, giám sát, autoscaling, NetworkPolicy, sao lưu.
Giả định bạn đã có cụm chạy theo [03](../deploy/README.md) và đang đứng ở `~/fomoxa-infra-demo` với `kubectl config use-context k3d-fomoxa`.

[Restart](01-status-and-updates.md#4-restarting-a-service) · [Cập nhật image](01-status-and-updates.md#updating-after-rebuilding-an-image) · [Drain](02-drain-and-accounts.md#6-shutting-down-a-game-server-safely-drain) · [Tài khoản](02-drain-and-accounts.md#7-accounts-and-player-data) ·
[TLS](03-tls-and-keys.md#tls-between-client-and-backend) · [Khoá Nakama](03-tls-and-keys.md#9-nakama-keys-and-passwords) · [Giám sát](04-monitoring.md#monitoring) · [Autoscaling](05-scaling-security-backup.md#autoscaling) · [NetworkPolicy](05-scaling-security-backup.md#networkpolicy-optional) ·
[Sao lưu](05-scaling-security-backup.md#13-backing-up-and-restoring-postgres) · [Đổi địa chỉ công khai](05-scaling-security-backup.md#14-changing-the-public-address-publicaddress)

## Các phần <a href="#parts" id="parts"></a>

- [01-trang-thai-va-cap-nhat.md](01-status-and-updates.md): Trạng thái và log, truy cập dịch vụ nội bộ, scale tay, restart, cập nhật image
- [02-drain-va-tai-khoan.md](02-drain-and-accounts.md): Tắt game server an toàn (drain), tài khoản và dữ liệu người chơi
- [03-tls-va-khoa.md](03-tls-and-keys.md): TLS giữa client và backend, khoá và mật khẩu Nakama
- [04-giam-sat.md](04-monitoring.md): Prometheus, Grafana, Alertmanager, Loki: cài đặt, chỉ số, cảnh báo
- [05-scale-bao-mat-sao-luu.md](05-scaling-security-backup.md): Autoscaling, NetworkPolicy, sao lưu Postgres, đổi `public_address`

## Ai nên đọc phần nào <a href="#who-should-read-what" id="who-should-read-what"></a>

- Người trực cụm hằng ngày: phần 1 (trạng thái, log, cập nhật) và phần 4 (giám sát).
- Người phụ trách bảo mật: phần 3 (TLS, khoá Nakama) và phần 2 (tài khoản người chơi).
- Người lo hiệu năng và chi phí: phần 4 (giám sát) và phần 5 (autoscaling).
- Trước khi mở ra ngoài mạng nội bộ: phần 3 và phần 5 (NetworkPolicy, `public_address`).

## Checklist vận hành <a href="#checklist" id="checklist"></a>

- [ ] Biết xem log từng dịch vụ và log mọi game server cùng lúc
- [ ] Biết cập nhật image: build → `k3d image import` → `rollout restart` (backend) / xoá + apply Fleet (game server)
- [ ] Thử drain: `kubectl delete gs ...` trên pod `Allocated` thấy `xin drain`, rồi `het nguoi choi, thoat`
- [ ] Đã quyết định TLS: chứng chỉ, pin trong client, `TLS_ONLY` hay không
- [ ] Đã sao lưu `deploy/secrets/` và có lịch `pg_dump`
- [ ] Giám sát: Prometheus Targets đều `UP`; Alertmanager đã có nơi nhận thông báo
- [ ] Autoscaler bật nếu cần; hiểu trần 16 pod/16 phòng
- [ ] `public_address` đúng với địa chỉ client thấy gateway
