import heapq
import json
from collections import Counter


class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(text: str) -> HuffmanNode:
    frequency = Counter(text)

    heap = [
        HuffmanNode(char, freq)
        for char, freq in frequency.items()
    ]

    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}

    if node.char is not None:
        codes[node.char] = prefix or "0"
        return codes

    build_codes(node.left, prefix + "0", codes)
    build_codes(node.right, prefix + "1", codes)

    return codes


def compress_text(text: str) -> bytes:
    tree = build_tree(text)

    codes = build_codes(tree)

    encoded = "".join(codes[ch] for ch in text)

    payload = {
        "codes": codes,
        "data": encoded,
    }

    return json.dumps(payload).encode("utf-8")


def decompress_text(data: bytes) -> str:
    payload = json.loads(data.decode("utf-8"))

    codes = payload["codes"]
    encoded = payload["data"]

    reverse = {
        value: key
        for key, value in codes.items()
    }

    current = ""
    decoded = []

    for bit in encoded:
        current += bit

        if current in reverse:
            decoded.append(reverse[current])
            current = ""

    return "".join(decoded)