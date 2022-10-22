import io
import os
from base64 import encodebytes

from PIL import Image, ImageOps


def pieces_generator(code_id: str):
    """Yield code_id char by char"""
    for char in code_id:
        yield char


def generate_visual_code(style_module: dict, code_id: str, style_path: str):
    """Visualize string code"""
    style_info = style_module['style-info']
    key_to_name = style_module['key_to_name']

    coji_code = Image.new('RGB', (style_info['size'], style_info['size']), tuple(style_info['background-color']))
    piece_size = int(style_info['size'] / style_info['pieces-row'])

    piece_id = pieces_generator(code_id)
    for cur_row in range(style_info['rows']):
        for cur_col in range(style_info['pieces-row']):
            piece = Image.open(
                os.path.join(style_path, 'pieces', f'{key_to_name[next(piece_id)]}.png')
            )
            piece = piece.resize((piece_size, piece_size), Image.ANTIALIAS)
            coji_code.paste(piece, (piece_size * cur_col, piece_size * cur_row), piece)
            piece.close()

    coji_code = ImageOps.expand(coji_code, border=style_info['border']['border-size'],
                                fill=tuple(style_info['border']['border-color']))
    with io.BytesIO() as out:
        coji_code.save(out, format='JPEG', quality=100, optimize=True)
        return encodebytes(out.getvalue()).decode()
