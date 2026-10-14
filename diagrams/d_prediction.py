from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('input-redundancy')
def input_redundancy(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('Input Redundancy covers a lost input message',
                                'Input Redundancy bù cho một input message bị mất'))
    green, blue, red = STROKES['client'], STROKES['server'], STROKES['danger']
    client_y, server_y = 80, 250
    canvas.text(30, client_y + 4, t("Owner's client", 'Client của owner'), 13, 700)
    canvas.text(30, server_y + 4, 'Server', 13, 700)
    canvas.line(160, client_y, 890, client_y, '#D1D5DB', 1.5)
    canvas.line(160, server_y, 890, server_y, '#D1D5DB', 1.5)

    messages = [(22, 200, 'ok'), (23, 400, 'lost'), (24, 600, 'ok')]
    for tick, x, fate in messages:
        canvas.circle(x, client_y, 5, green)
        canvas.text(x, client_y - 14, t(f'tick {tick}', f'tick {tick}'), 12, 700, 'middle', KINDS['client'][2])
        top = client_y + 18
        for row, carried in enumerate((tick, tick - 1, tick - 2)):
            kind = 'client' if row == 0 else 'plain'
            canvas.rect(x + 14, top + row * 22, 64, 20, *KINDS[kind][:2], radius=5)
            canvas.text(x + 46, top + row * 22 + 14, t(f'in {carried}', f'in {carried}'), 11, 600 if row == 0 else 400,
                        'middle', KINDS['client'][2] if row == 0 else MUTED, mono=True)
        if fate == 'lost':
            canvas.arrow([(x, client_y + 6), (x + 20, server_y - 70)], red, dashed=True, end=False)
            canvas.text(x + 22, server_y - 62, '✕', 18, 700, 'middle', red)
            continue
        canvas.arrow([(x, client_y + 6), (x + 40, server_y - 8)], green)

    canvas.rect(660, server_y + 16, 230, 46, *KINDS['server'][:2], radius=8)
    canvas.text(775, server_y + 36, t('in 23 still arrives,', 'in 23 vẫn tới,'), 12, 700, 'middle', KINDS['server'][2])
    canvas.text(775, server_y + 53, t('inside the message for tick 24', 'trong message của tick 24'), 11.5, 400, 'middle', MUTED)
    canvas.line(640, server_y, 680, server_y + 16, blue, 1, dashed=True)
    canvas.text(30, 316, t('Each unreliable input message holds the newest input and the ones before it, Input Redundancy (3) in total.',
                           'Mỗi input message unreliable chứa input mới nhất và các input trước nó, tổng cộng Input Redundancy (3) input.'),
                12, color=MUTED)
    return canvas


@diagram('reconcile-replay')
def reconcile_replay(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('A correction: restore the server state, then replay the later ticks',
                                'Một lần sửa: khôi phục state của server, rồi replay các tick sau'))
    green, blue, red, accent = STROKES['client'], STROKES['server'], STROKES['danger'], STROKES['accent']

    def x_of(tick):
        return 170 + (tick - 10) * 120

    canvas.text(30, 74, t('Predicted', 'Đã dự đoán'), 13, 700)
    for tick in range(10, 15):
        kind = 'danger' if tick == 11 else 'client'
        canvas.box(x_of(tick), 50, 100, 44, kind, f'T{tick}', title_mono=True)
    canvas.text(x_of(14) + 112, 64, t('client is', 'client đang'), 11.5, 400, color=MUTED)
    canvas.text(x_of(14) + 112, 80, t('at T14', 'ở T14'), 11.5, 600, color=MUTED)

    canvas.box(x_of(11) - 10, 130, 120, 50, 'server', t('Server state', 'State của server'), ['T11'], title_size=12.5)
    canvas.arrow([(x_of(11) + 50, 130), (x_of(11) + 50, 98)], blue)
    canvas.text(x_of(11) + 130, 152, t('arrives while the client is at T14,', 'tới khi client đang ở T14,'), 12, 600, color=red)
    canvas.text(x_of(11) + 130, 170, t('matches() returns false', 'matches() trả về false'), 12, 400, color=MUTED, mono=False)

    canvas.text(30, 240, t('Corrected', 'Sau khi sửa'), 13, 700)
    canvas.box(x_of(11), 216, 100, 44, 'server', 'restore', title_mono=True)
    for tick in range(12, 15):
        canvas.box(x_of(tick), 216, 100, 44, 'accent', f'T{tick}', ['replay'], title_mono=True)
    for tick in range(11, 14):
        canvas.arrow([(x_of(tick) + 100, 238), (x_of(tick + 1), 238)], accent)
    canvas.arrow([(x_of(11) + 50, 180), (x_of(11) + 50, 216)], blue)
    canvas.text(30, 300, t('Each replayed tick calls apply(input, context) with context.Replaying = true, then capture.',
                           'Mỗi tick replay gọi apply(input, context) với context.Replaying = true, rồi capture.'), 12, color=MUTED)
    canvas.text(30, 318, t('Afterwards OnReconciled(11) runs and ReconcileCount goes up by one.',
                           'Sau đó OnReconciled(11) chạy và ReconcileCount tăng thêm một.'), 12, color=MUTED)
    return canvas


@diagram('physics-rollback')
def physics_rollback(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('Rolling the physics worlds back to a corrected tick',
                                'Đưa các physics world về một tick đã sửa'))
    blue, red, accent = STROKES['server'], STROKES['danger'], STROKES['accent']

    def x_of(tick):
        return 170 + tick * 135

    canvas.text(30, 74, t('First run', 'Lần chạy đầu'), 13, 700)
    for tick in range(5):
        kind = 'danger' if tick == 2 else 'client'
        canvas.box(x_of(tick), 50, 105, 44, kind, f'T{tick}', [t('world saved', 'đã lưu world')], title_mono=True, title_size=13, body_size=11)
        if tick:
            canvas.arrow([(x_of(tick) - 30, 72), (x_of(tick), 72)], LINE)
    canvas.text(x_of(2) + 52, 118, t('server state for T2 does not match', 'state của server cho T2 không khớp'),
                12, 600, 'middle', red)

    canvas.text(30, 204, t('Correction', 'Sửa'), 13, 700)
    canvas.box(x_of(2) - 20, 150, 145, 104, 'server', 'Load(T2)',
               [t('every world of the', 'mọi world của nhóm'), t('group goes back,', 'quay về T2,'),
                t('then restore()', 'rồi restore()')], title_mono=True, title_size=13, body_size=11)
    for tick in (3, 4):
        canvas.box(x_of(tick), 150, 105, 104, 'accent', f'T{tick}',
                   [t('apply input', 'apply input'), t('step worlds', 'step world'), t('capture, save', 'capture, lưu')],
                   title_mono=True, title_size=13, body_size=11)
    canvas.arrow([(x_of(2) + 125, 202), (x_of(3), 202)], accent)
    canvas.arrow([(x_of(3) + 105, 202), (x_of(4), 202)], accent)
    canvas.text(30, 290, t('A saved state holds position, rotation, velocity, angular velocity and sleep state of each dynamic body that is not a proxy.',
                           'State đã lưu gồm vị trí, góc xoay, vận tốc, vận tốc góc và trạng thái ngủ của mỗi dynamic body không phải proxy.'),
                12, color=MUTED)
    canvas.text(30, 310, t('Contact data is not saved, so a replay can differ from the first run.',
                           'Dữ liệu contact không được lưu, nên một lần replay có thể khác lần chạy đầu.'), 12, color=MUTED)
    return canvas


@diagram('rollback-groups')
def rollback_groups(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 280, t('Rollback groups', 'Rollback group'))
    accent = STROKES['accent']

    canvas.rect(30, 30, 540, 210, *KINDS['accent'][:2], radius=14)
    canvas.text(50, 56, t('Rollback group 1', 'Rollback group 1'), 13, 700, color=KINDS['accent'][2])
    canvas.box(50, 72, 240, 82, 'plain', t('3D world', 'World 3D'),
               [t('scenes A and B share one', 'scene A và B dùng chung một'), t('physics scene, so one world', 'physics scene, nên là một world')])
    canvas.box(310, 72, 240, 82, 'plain', t('2D world', 'World 2D'), [t('of scene A', 'của scene A')])
    canvas.text(50, 184, t('Corrected together: loading T2 loads both worlds,', 'Được sửa cùng nhau: load T2 là load cả hai world,'), 12, 600)
    canvas.text(50, 204, t('and every predicted object in them replays.', 'và mọi object được dự đoán trong đó đều replay.'), 12, 400, color=MUTED)

    canvas.rect(610, 30, 280, 210, *KINDS['neutral'][:2], radius=14)
    canvas.text(630, 56, t('Rollback group 2', 'Rollback group 2'), 13, 700)
    canvas.box(630, 72, 240, 82, 'plain', t('3D world', 'World 3D'), [t('of scene C', 'của scene C')])
    canvas.text(630, 184, t('Shares no world with group 1,', 'Không chung world nào với nhóm 1,'), 12, 600)
    canvas.text(630, 204, t('so it is corrected on its own.', 'nên được sửa riêng.'), 12, 400, color=MUTED)
    canvas.text(30, 268, t('A group is loaded only when every world in it has a saved state for the corrected tick.',
                           'Một nhóm chỉ được load khi mọi world trong đó có state đã lưu cho tick được sửa.'), 12, color=MUTED)
    return canvas
