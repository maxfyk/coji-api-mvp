style_module = {}

style_module['style-info'] = {
    'name': 'geom-original',
    'size': 600,
    'rows': 4,
    'pieces-row': 4,
    'background-color': (26, 26, 26),
    'border': {
        'border-size': 15,
        'border-color': (255, 191, 0),  # 'yellow',
    },
    'template': {
        'add-template': True,
        'template-offset': (30, 30),
    }
}

style_module['style-info']['total-length'] = \
    style_module['style-info']['rows'] * style_module['style-info']['pieces-row']

style_module['name-to-key'] = {
    'circle': 'a',
    'd-arrow': 'b',
    'e-circle': 'c',
    'e-rhombus': 'd',
    'e-square': 'e',
    'e-triangle': 'f',
    'l-arrow': 'g',
    'minus': 'h',
    'plus': 'i',
    'r-arrow': 'j',
    'rhombus': 'k',
    'square': 'l',
    'triangle': 'm',
    'u-arrow': 'n',
    'v-bar': 'o',
    'x': 'p'
}
style_module['key-to-name'] = {v: k for k, v in style_module['name-to-key'].items()}

style_module['names'] = list(style_module['name-to-key'].keys())
style_module['keys'] = list(style_module['key-to-name'].keys())

style_module['object-detection-model'] = {
    'supported': True,
    'num-items': 18,
    'name-to-key': {'circle': 0, 'd-arrow': 1, 'e-circle': 2, 'e-rhombus': 3, 'e-square': 4, 'e-triangle': 5,
                    'l-arrow': 6, 'minus': 7, 'plus': 8, 'r-arrow': 9, 'rhombus': 10, 'square': 11, 'triangle': 12,
                    'u-arrow': 13, 'v-bar': 14, 'x': 15, 'coji-code': 16, 'coji-frame': 17}
}
style_module['object-detection-model']['key-to-name'] = {v: k for k, v in
                                                         style_module['object-detection-model']['name-to-key'].items()}
