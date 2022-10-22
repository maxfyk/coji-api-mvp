p = 6364136223846793005
s = 1442695040888963407


def generate_code_id(index: int, symbols: dict, style_info: dict):
    """Generate random code id"""
    n, m = style_info['rows'], style_info['pieces-row']  # dimension of key - n*n
    num_keys = (2 ** m) ** (n * n)  # total number of keys

    sh_idx = (index * p + s) % num_keys  # map to pseudo-random target
    values = [(sh_idx >> (i * m)) & ((1 << m) - 1)
              for i in range(n * n)]  # split into m-bit words
    return ''.join([symbols[i] for i in values])
