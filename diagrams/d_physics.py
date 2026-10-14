from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('physics-stack')
def physics_stack(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 470, t('The physics layers, from game code down to Unity',
                                'Các tầng physics, từ code game xuống Unity'))
    rows = [
        ('code', t('Game code', 'Code game'), 'apply, capture, restore, OnTick'),
        ('client', t('Fomoxa physics API', 'API physics của Fomoxa'), 'PhysicsBody, PhysicsBody2D, PhysicsHistory'),
        ('server', 'IPhysicsSimulation', 'Step, CreateSnapshot, Save, Load'),
        ('server', 'IPhysicsWorld, IPhysicsWorld2D', t('bodies, forces, queries', 'body, lực, truy vấn')),
        ('host', t('Physics component', 'Component physics'), 'NetworkPhysics, RigidbodyPhysics'),
        ('host', t('World implementation', 'Hiện thực world'), 'UnityPhysicsWorld, UnityPhysicsWorld2D'),
        ('neutral', 'Unity', 'PhysicsScene, PhysicsScene2D'),
    ]
    top, height, gap = 30, 46, 14
    for index, (kind, title, body) in enumerate(rows):
        y = top + index * (height + gap)
        fill, stroke, ink = KINDS[kind]
        canvas.rect(160, y, 560, height, fill, stroke, 10)
        canvas.text(180, y + 28, title, 13.5, 700, color=ink, mono=title.startswith('IPhysics'))
        canvas.text(700, y + 28, body, 12, 500, 'end', MUTED, mono=True)
        if index:
            canvas.arrow([(440, y - gap), (440, y)], LINE)

    def bracket(first, last, label, sub):
        y1 = top + first * (height + gap)
        y2 = top + last * (height + gap) + height
        canvas.line(740, y1, 740, y2, '#9CA3AF', 1.5)
        canvas.line(734, y1, 740, y1, '#9CA3AF', 1.5)
        canvas.line(734, y2, 740, y2, '#9CA3AF', 1.5)
        canvas.text(754, (y1 + y2) / 2 - 2, label, 13, 700)
        canvas.text(754, (y1 + y2) / 2 + 16, sub, 11, 500, color=MUTED, mono=True)

    bracket(1, 3, t('Layer 1', 'Tầng 1'), 'Fomoxa.Networking')
    bracket(4, 5, t('Layer 2', 'Tầng 2'), 'Fomoxa.Unity')
    canvas.text(30, 458, t('Layer 1 does not reference Unity, so its vectors are System.Numerics types.',
                           'Tầng 1 không tham chiếu Unity, nên vector của nó là kiểu System.Numerics.'), 12, color=MUTED)
    return canvas


@diagram('world-rule')
def world_rule(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 150, t('The rule of a physics world', 'Quy tắc của một physics world'))
    steps = [
        (t('One world', 'Một world'), t('one PhysicsScene', 'một PhysicsScene')),
        (t('One state', 'Một state'), t('saved and loaded whole', 'lưu và load nguyên khối')),
        (t('One owner', 'Một owner'), t('the first manager to step it', 'manager đầu tiên step nó')),
        (t('One Step per tick', 'Một Step mỗi tick'), t('more only during a replay', 'thêm chỉ khi replay')),
    ]
    width, gap = 190, 30
    for index, (title, body) in enumerate(steps):
        x = 30 + index * (width + gap)
        canvas.box(x, 34, width, 76, 'server', title, [body])
        if index:
            canvas.arrow([(x - gap, 72), (x, 72)], LINE)
    canvas.text(30, 138, t('Rollback therefore works per world and per group of worlds, never per object.',
                           'Vì vậy rollback hoạt động theo world và theo nhóm world, không bao giờ theo từng object.'), 12, color=MUTED)
    return canvas


@diagram('body-roles')
def body_roles(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 300, t("Predicted and proxy bodies in one client's world",
                                'Body được dự đoán và body proxy trong world của một client'))
    green, muted, blue = STROKES['client'], STROKES['muted'], STROKES['server']

    canvas.rect(30, 30, 520, 240, '#F9FAFB', '#E5E7EB', 12)
    canvas.text(50, 56, t('Physics world on client A', 'Physics world trên client A'), 13, 700)
    canvas.circle(190, 170, 34, KINDS['client'][0], green, 2)
    canvas.text(190, 175, t('A', 'A'), 15, 700, 'middle', KINDS['client'][2])
    canvas.arrow([(226, 170), (300, 170)], green, width=2, label=t('collides with', 'va chạm với'), label_offset=(0, -8))
    canvas.circle(370, 170, 34, KINDS['neutral'][0], muted, 2)
    canvas.add('<circle cx="370" cy="170" r="42" fill="none" stroke="#9CA3AF" stroke-width="1.2" stroke-dasharray="5 4"/>')
    canvas.text(370, 175, 'B', 15, 700, 'middle', MUTED)
    canvas.text(370, 236, t('kinematic, placed at its', 'kinematic, đặt tại vị trí'), 11.5, 500, 'middle', MUTED)
    canvas.text(370, 252, t('NetworkTransform position', 'NetworkTransform của nó'), 11.5, 500, 'middle', MUTED)
    canvas.text(190, 236, t("A's own player", 'player của chính A'), 11.5, 600, 'middle', KINDS['client'][2])

    canvas.box(580, 40, 310, 104, 'client', t('Predicted', 'Được dự đoán'),
               [t('objects client A owns and predicts', 'object client A sở hữu và dự đoán'),
                t('simulated, saved every tick,', 'được mô phỏng, lưu mỗi tick,'),
                t('rolled back on corrections', 'rollback khi có lần sửa')])
    canvas.box(580, 160, 310, 104, 'neutral', 'Proxy',
               [t('every other networked body', 'mọi networked body khác'),
                t('kinematic, placed before each step,', 'kinematic, được đặt trước mỗi step,'),
                t('excluded from snapshots', 'không nằm trong snapshot')])
    return canvas


@diagram('contact-replay')
def contact_replay(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 300, t('Contact events around a replay', 'Contact event quanh một lần replay'))
    green, red, accent = STROKES['client'], STROKES['danger'], STROKES['accent']

    def x_of(tick):
        return 190 + (tick - 2) * 150

    canvas.text(30, 74, t('Shown so far', 'Đã hiển thị'), 13, 700)
    shown = {2: '{ }', 3: '{ B }', 4: '{ B }'}
    for tick, touching in shown.items():
        canvas.box(x_of(tick), 50, 120, 46, 'client', f'T{tick}', [touching], title_mono=True, mono_body=True, title_size=12.5)
    canvas.pill(x_of(3) + 60, 112, t('OnEnter(B) fired', 'OnEnter(B) đã chạy'), 'client', 10.5)

    canvas.text(30, 194, t('Replay from T2', 'Replay từ T2'), 13, 700)
    replay = {2: '{ }', 3: '{ }', 4: '{ C }'}
    for tick, touching in replay.items():
        kind = 'server' if tick == 2 else 'accent'
        canvas.box(x_of(tick), 170, 120, 46, kind, f'T{tick}', [touching], title_mono=True, mono_body=True, title_size=12.5)
        if tick > 2:
            canvas.arrow([(x_of(tick) - 30, 193), (x_of(tick), 193)], accent)
    canvas.text(x_of(2) + 60, 232, t('restored set', 'tập đã khôi phục'), 11, 500, 'middle', STROKES['server'])
    canvas.text(x_of(3) + 60, 232, t('no events yet', 'chưa có event'), 11, 500, 'middle', MUTED)

    canvas.rect(x_of(4) + 150, 150, 160, 86, '#FFFFFF', '#D1D5DB', 10)
    canvas.text(x_of(4) + 230, 172, t('After the replay,', 'Sau khi replay,'), 12, 700, 'middle')
    canvas.text(x_of(4) + 230, 190, t('once:', 'một lần:'), 12, 400, 'middle', MUTED)
    canvas.text(x_of(4) + 230, 208, 'OnExit(B)', 12, 700, 'middle', red, mono=True)
    canvas.text(x_of(4) + 230, 226, 'OnEnter(C)', 12, 700, 'middle', green, mono=True)
    canvas.arrow([(x_of(4) + 120, 193), (x_of(4) + 150, 193)], LINE)
    canvas.text(30, 284, t('The events are the difference between what was shown and the replayed result, so no event fires twice.',
                           'Event là phần khác nhau giữa những gì đã hiển thị và kết quả replay, nên không event nào chạy hai lần.'), 12, color=MUTED)
    return canvas


@diagram('rapier-stack')
def rapier_stack(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 400, t('Where Rapier sits, in Unity and in a console server',
                                'Rapier nằm ở đâu, trong Unity và trong console server'))
    canvas.text(30, 38, t('Unity client or server', 'Client hoặc server Unity'), 15, 700)
    left = [
        ('code', t('Game code', 'Code game'), 'apply, capture, restore, OnTick'),
        ('client', 'PhysicsBody, PhysicsBody2D', t('unchanged', 'không đổi')),
        ('host', 'RapierPhysics', t('one world per network scene and dimension', 'một world mỗi network scene và mỗi chiều')),
    ]
    for index, (kind, title, body) in enumerate(left):
        y = 56 + index * 76
        canvas.box(30, y, 400, 58, kind, title, [body], title_mono=index > 0)
        if index:
            canvas.arrow([(230, y - 18), (230, y)], LINE)

    canvas.text(490, 38, t('Console server, without Unity', 'Console server, không có Unity'), 15, 700)
    canvas.box(490, 56, 400, 58, 'code', t('Your console program', 'Chương trình console của bạn'), [t('EntityBehaviour classes, the same models', 'các class EntityBehaviour, cùng model')])
    canvas.box(490, 208, 400, 58, 'host', 'RapierScenes', [t('the same worlds, built from the same scene file', 'cùng world, dựng từ cùng scene file')], title_mono=True)
    canvas.arrow([(690, 114), (690, 208)], LINE)

    canvas.box(30, 300, 860, 64, 'neutral', 'fomoxa_rapier', ['rapier3d, rapier2d 0.36.0, enhanced-determinism'], title_mono=True, mono_body=True)
    canvas.arrow([(230, 266), (230, 300)], LINE)
    canvas.arrow([(690, 266), (690, 300)], LINE)
    canvas.text(30, 388, t('A snapshot holds the whole Rapier world, contacts included, so a replay gives the same ticks as the first run.',
                           'Snapshot chứa toàn bộ world Rapier, kể cả contact, nên replay cho ra đúng các tick như lần chạy đầu.'), 12, color=MUTED)
    return canvas
