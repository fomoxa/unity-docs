from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES, INK


@diagram('behaviour-index')
def behaviour_index(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 344, t('How behaviour indexes and the fingerprint come from the hierarchy',
                                'Behaviour index và fingerprint được lấy từ hierarchy thế nào'))
    accent = STROKES['accent']

    canvas.text(30, 38, t('Prefab hierarchy', 'Hierarchy của prefab'), 15, 700)
    rows = [
        (0, 'Player', ['NetworkObject', 'NetworkTransform', 'PlayerMovement']),
        (1, 'Weapon', ['WeaponBehaviour']),
        (1, 'Model', ['MeshRenderer']),
    ]
    y = 62
    for depth, name, components in rows:
        x = 30 + depth * 26
        if depth:
            canvas.line(43, y - 14, 43, y + 10, '#D1D5DB', 1.2)
            canvas.line(43, y + 10, x - 4, y + 10, '#D1D5DB', 1.2)
        canvas.rect(x, y, 250 - depth * 26, 22 + len(components) * 22, '#FFFFFF', '#D1D5DB', 8)
        canvas.text(x + 12, y + 16, name, 13, 700)
        for index, component in enumerate(components):
            networked = component not in ('NetworkObject', 'MeshRenderer')
            color = INK if networked else MUTED
            canvas.text(x + 22, y + 38 + index * 22, component, 12, 500 if networked else 400, color=color, mono=True)
        y += 22 + len(components) * 22 + 16

    canvas.text(330, 38, 'GetComponentsInChildren', 15, 700, mono=True)
    canvas.text(330, 58, t('NetworkBehaviours in order, inactive ones included',
                           'Các NetworkBehaviour theo thứ tự, kể cả cái đang tắt'), 12, color=MUTED)
    entries = ['NetworkTransform', 'PlayerMovement', 'WeaponBehaviour']
    for index, name in enumerate(entries):
        top = 76 + index * 52
        canvas.rect(330, top, 240, 40, *KINDS['accent'][:2], radius=8)
        canvas.circle(354, top + 20, 12, accent)
        canvas.text(354, top + 25, str(index), 13, 700, 'middle', '#FFFFFF')
        canvas.text(378, top + 25, name, 12.5, 600, color=KINDS['accent'][2], mono=True)
    canvas.arrow([(282, 130), (326, 130)], LINE)

    canvas.text(620, 38, t('What the index is used for', 'Index được dùng vào đâu'), 15, 700)
    canvas.box(620, 62, 270, 92, 'neutral', t('Messages to a behaviour', 'Message tới một behaviour'),
               [t('carry the object id and', 'mang object id và'),
                t('the behaviour index, e.g. 17 / 1', 'behaviour index, ví dụ 17 / 1')])
    canvas.box(620, 172, 270, 110, 'neutral', t('Fingerprint', 'Fingerprint'),
               [t('FNV-1a hash of the full type', 'Hash FNV-1a của tên type'),
                t('names, joined in this order.', 'đầy đủ, nối theo thứ tự này.'),
                t('Sent with every spawn.', 'Gửi kèm mỗi lần spawn.')])
    canvas.arrow([(570, 96), (620, 108)], LINE)
    canvas.arrow([(570, 200), (620, 222)], LINE)

    canvas.rect(30, 300, 860, 30, *KINDS['danger'][:2], radius=8)
    canvas.text(460, 320, t('A client whose prefab gives a different list stops with PrefabMismatch.',
                            'Client có prefab cho ra danh sách khác sẽ dừng với PrefabMismatch.'),
                12.5, 600, 'middle', KINDS['danger'][2])
    return canvas


@diagram('spawn-flow')
def spawn_flow(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 400, t('From a saved prefab to an object on every observer',
                                'Từ prefab đã lưu tới object trên mọi observer'))
    blue, green = STROKES['server'], STROKES['client']
    columns = [
        (30, t('Editor', 'Editor'), 'neutral', [
            (t('Prefab saved', 'Prefab được lưu'), [t('Prefab Id from the GUID', 'Prefab Id lấy từ GUID')]),
            (t('Lists written', 'Ghi danh sách'), ['FomoxaPrefabList.asset', 'FomoxaPrefabs.cs']),
        ]),
        (330, t('Server', 'Server'), 'server', [
            ('Awake', [t('registers the prefabs', 'đăng ký các prefab')]),
            ('Instantiate', [t('place it, set its state', 'đặt vị trí, gán state')]),
            ('Spawn(instance, owner)', [t('object id, OnStartServer', 'object id, OnStartServer')]),
        ]),
        (630, t('Each observing client', 'Mỗi client đang observe'), 'client', [
            ('Awake', [t('registers the same prefabs', 'đăng ký cùng các prefab')]),
            (t('Look up the prefab id', 'Tìm theo prefab id'), [t('compare the fingerprint', 'so fingerprint')]),
            ('Instantiate', [t('apply state, OnStartClient', 'áp state, OnStartClient')]),
        ]),
    ]
    for x, title, kind, steps in columns:
        canvas.text(x, 38, title, 15, 700)
        for index, (heading, body) in enumerate(steps):
            top = 56 + index * 92
            canvas.box(x, top, 260, 70, kind, heading, body, title_mono=heading in ('Awake', 'Instantiate', 'Spawn(instance, owner)'))
            if index:
                canvas.arrow([(x + 130, top - 22), (x + 130, top)], LINE)

    canvas.arrow([(290, 91), (330, 91)], LINE, dashed=True, label=t('same list', 'cùng danh sách'), label_offset=(0, -8))
    canvas.arrow([(590, 276), (610, 276), (610, 183), (630, 183)], blue, width=2)
    canvas.rect(330, 336, 560, 50, '#FFFFFF', blue, 10)
    canvas.text(346, 356, t('Spawn message, reliable and ordered', 'Message spawn, tin cậy và có thứ tự'), 12.5, 700, color=blue)
    canvas.text(346, 375, t('object id, prefab id, fingerprint, owner, position, rotation, scale, state',
                            'object id, prefab id, fingerprint, owner, vị trí, góc xoay, tỉ lệ, state'), 12, color=MUTED)
    canvas.line(610, 276, 610, 336, blue, 1.2, dashed=True)
    return canvas


@diagram('distance-rule')
def distance_rule(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 400, t('Which objects a DistanceRule lets a peer observe',
                                'DistanceRule cho một peer observe những object nào'))
    green, muted = STROKES['client'], STROKES['muted']
    accent = STROKES['accent']

    canvas.rect(30, 30, 520, 340, '#F9FAFB', '#E5E7EB', 12)
    player = (190, 270)
    tower = (300, 190)
    canvas.add(f'<circle cx="{tower[0]}" cy="{tower[1]}" r="150" fill="{KINDS["accent"][0]}" fill-opacity="0.45" '
               f'stroke="{accent}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    canvas.add(f'<circle cx="{player[0]}" cy="{player[1]}" r="80" fill="{KINDS["client"][0]}" fill-opacity="0.8" '
               f'stroke="{green}" stroke-width="1.5" stroke-dasharray="6 4"/>')
    canvas.circle(*player, 11, green)
    canvas.text(player[0], player[1] + 30, t('player of peer A', 'player của peer A'), 12, 600, 'middle', KINDS['client'][2])
    canvas.line(player[0], player[1], player[0] + 80, player[1], green, 1.2)
    canvas.text(player[0] + 40, player[1] - 6, 'Radius', 11, 600, 'middle', green, mono=True)

    crate = (230, 222)
    canvas.rect(crate[0] - 9, crate[1] - 9, 18, 18, green, green, 3)
    canvas.text(crate[0] + 16, crate[1] + 4, t('crate', 'thùng'), 12, 600, color=KINDS['client'][2])

    canvas.rect(tower[0] - 9, tower[1] - 16, 18, 32, accent, accent, 3)
    canvas.text(tower[0] + 16, tower[1] + 4, t('tower', 'tháp'), 12, 600, color=KINDS['accent'][2])
    canvas.text(tower[0], tower[1] - 128, 'ObserverRange', 11, 600, 'middle', accent, mono=True)

    enemy = (480, 320)
    canvas.circle(*enemy, 9, muted)
    canvas.text(enemy[0] - 16, enemy[1] + 4, t('enemy', 'kẻ địch'), 12, 600, 'end', MUTED)

    rows = [
        (green, t('Crate: inside Radius of the player.', 'Thùng: nằm trong Radius của player.'),
         t('Peer A observes it.', 'Peer A observe nó.')),
        (accent, t('Tower: outside Radius, but its own', 'Tháp: ngoài Radius, nhưng ObserverRange'),
         t('ObserverRange reaches the player.', 'của chính nó với tới player.')),
        (muted, t('Enemy: too far from every object', 'Kẻ địch: quá xa mọi object'),
         t('peer A owns. Not observed.', 'peer A sở hữu. Không được observe.')),
    ]
    for index, (color, first, second) in enumerate(rows):
        top = 58 + index * 78
        canvas.circle(590, top + 4, 7, color)
        canvas.text(608, top + 9, first, 12.5, 600)
        canvas.text(608, top + 29, second, 12.5, 400, color=MUTED)
    canvas.text(580, 300, t('Distance is measured between world positions,', 'Khoảng cách đo giữa vị trí thế giới,'), 12, color=MUTED)
    canvas.text(580, 320, t('from any object the peer owns. A peer that', 'từ bất kỳ object nào peer sở hữu. Peer'), 12, color=MUTED)
    canvas.text(580, 340, t('owns nothing observes nothing.', 'không sở hữu gì thì không observe gì.'), 12, color=MUTED)
    return canvas
