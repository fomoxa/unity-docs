from registry import diagram, pick
from svg import Canvas, KINDS, LINE, MUTED, STROKES


@diagram('deploy-topology')
def deploy_topology(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('A server that takes desktop and browser clients',
                                'Một server nhận cả client desktop lẫn client trình duyệt'))
    green, blue, accent = STROKES['client'], STROKES['server'], STROKES['accent']

    canvas.box(30, 50, 210, 64, 'client', t('Desktop client', 'Client desktop'), ['UdpNetworkTransport'], mono_body=True)
    canvas.box(30, 196, 210, 64, 'client', t('Browser client', 'Client trình duyệt'),
               [t('page served over HTTPS', 'trang phục vụ qua HTTPS')])

    canvas.box(340, 196, 200, 64, 'accent', t('Reverse proxy', 'Reverse proxy'),
               [t('terminates TLS', 'kết thúc TLS')])
    canvas.rect(640, 30, 250, 250, *KINDS['server'][:2], radius=14)
    canvas.text(660, 56, t('Server host', 'Máy server'), 13, 700, color=KINDS['server'][2])
    canvas.box(660, 70, 210, 60, 'plain', t('UDP :7777', 'UDP :7777'), [t('entry 0, StartConnection port', 'entry 0, port của StartConnection')],
               title_mono=True)
    canvas.box(660, 196, 210, 60, 'plain', t('ws:// :8080/play', 'ws:// :8080/play'), [t('entry 1, Path /play', 'entry 1, Path /play')],
               title_mono=True)

    canvas.arrow([(240, 82), (660, 100)], green, start=True, label=t('UDP, open inbound 7777', 'UDP, mở inbound 7777'),
                 label_offset=(0, -8))
    canvas.arrow([(240, 228), (340, 228)], green, start=True, label='wss://', label_mono=True, label_offset=(0, -8))
    canvas.arrow([(540, 228), (660, 226)], accent, start=True, label='ws://', label_mono=True, label_offset=(0, -8))
    canvas.text(30, 300, t('Clients reach the server over IPv4. Allowed Origins on the server lists the origins that serve the page.',
                           'Client tới server qua IPv4. Allowed Origins trên server liệt kê các origin phục vụ trang game.'), 12, color=MUTED)
    canvas.text(30, 318, t('Server and clients must be built from the same models, prefabs and scenes.',
                           'Server và client phải được build từ cùng model, prefab và scene.'), 12, color=MUTED)
    return canvas


@diagram('console-stack')
def console_stack(language):
    t = lambda english, vietnamese: pick(language, english, vietnamese)
    canvas = Canvas(920, 330, t('What a console server is made of', 'Console server gồm những gì'))
    rows = [
        ('code', t('Your console program', 'Chương trình console của bạn'), t('Main, game rules as EntityBehaviour classes', 'Main, luật game dạng class EntityBehaviour'), ''),
        ('host', t('Console backend', 'Console backend'), 'StandaloneRuntime, StandaloneEntity', 'Standalone~ (source)'),
        ('server', t('Layer 1', 'Tầng 1'), 'Fomoxa.Networking', 'Runtime/Core (source)'),
        ('neutral', t('Libraries', 'Thư viện'), 'Fomoxa.Net, Fomoxa.Attributes', 'Runtime/Plugins'),
    ]
    for index, (kind, title, body, where) in enumerate(rows):
        y = 30 + index * 66
        fill, stroke, ink = KINDS[kind]
        canvas.rect(30, y, 600, 50, fill, stroke, 10)
        canvas.text(50, y + 22, title, 13.5, 700, color=ink)
        canvas.text(50, y + 40, body, 12, 500, color=MUTED, mono=index > 0)
        if where:
            canvas.text(650, y + 30, where, 12, 500, color=MUTED, mono=True)
        if index:
            canvas.arrow([(330, y - 16), (330, y)], LINE)
    canvas.text(650, 18 + 66, 'com.fomoxa.networking/', 11, 600, color=MUTED, mono=True)
    canvas.text(30, 300, t('The Unity project stays the source of the models, the prefab ids and fingerprints, and the scene files.',
                           'Project Unity vẫn là nguồn của model, prefab id, fingerprint và scene file.'), 12, color=MUTED)
    canvas.text(30, 318, t('A console project compiles all of this together with the generated code of the Unity project.',
                           'Project console biên dịch tất cả những thứ này cùng code sinh ra của project Unity.'), 12, color=MUTED)
    return canvas
