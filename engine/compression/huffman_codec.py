import heapq
import json

from collections import Counter
from typing import Any


# ===== HUFFMAN NODE =====
class HuffmanNode:
    def __init__(self, symbol: str | None = None, weight: int = 0) -> None:
        # ===== NODE DATA =====
        self.symbol: str | None = (
            symbol
        )

        self.weight: int = (
            weight
        )

        # ===== CHILDREN =====
        self.left_branch: HuffmanNode | None = None
        self.right_branch: HuffmanNode | None = None

    # ===== PRIORITY ORDERING =====
    def __lt__(self, other: "HuffmanNode") -> bool:

        return (
            self.weight < other.weight
        )


# ===== TREE CONSTRUCTION =====
def build_tree(text: str) -> HuffmanNode:

    # ===== SYMBOL FREQUENCY =====
    symbol_frequency: Counter[str] = (
        Counter(text)
    )

    # ===== PRIORITY QUEUE =====
    node_queue: list[HuffmanNode] = [
        HuffmanNode(
            symbol,
            weight,
        )
        for symbol, weight
        in symbol_frequency.items()
    ]

    heapq.heapify(
        node_queue
    )

    # ===== TREE MERGING =====
    while len(node_queue) > 1:

        # ===== LOWEST FREQUENCY NODES =====
        left_branch: HuffmanNode = (
            heapq.heappop(
                node_queue
            )
        )

        right_branch: HuffmanNode = (
            heapq.heappop(
                node_queue
            )
        )

        # ===== MERGED NODE =====
        parent_node: HuffmanNode = (
            HuffmanNode(
                weight=(
                    left_branch.weight + right_branch.weight
                )
            )
        )

        parent_node.left_branch = left_branch
        parent_node.right_branch = right_branch

        # ===== QUEUE UPDATE =====
        heapq.heappush(
            node_queue,
            parent_node,
        )

    # ===== ROOT NODE =====
    return node_queue[0]


# ===== CODE GENERATION =====
def build_codes(node: HuffmanNode, prefix: str = "", codebook: dict[str, str] | None = None) -> dict[str, str]:

    # ===== CODE CONTAINER =====
    if codebook is None:
        codebook = {}

    # ===== LEAF NODE =====
    if node.symbol is not None:

        codebook[node.symbol] = (
            prefix or "0"
        )

        return codebook

    # ===== LEFT PATH =====
    if node.left_branch is not None:
        build_codes(
            node.left_branch,
            prefix + "0",
            codebook,
        )

    # ===== RIGHT PATH =====
    if node.right_branch is not None:
        build_codes(
            node.right_branch,
            prefix + "1",
            codebook,
        )

    # ===== RESULT =====
    return codebook


# ===== TEXT COMPRESSION =====
def compress_text(text: str) -> bytes:

    # ===== HUFFMAN TREE =====
    huffman_tree: HuffmanNode = (
        build_tree(text)
    )

    # ===== HUFFMAN CODES =====
    codebook: dict[str, str] = (
        build_codes(
            huffman_tree
        )
    )

    # ===== BITSTREAM ENCODING =====
    encoded_bitstream: str = "".join(
        codebook[symbol]
        for symbol in text
    )

    # ===== COMPRESSED PAYLOAD =====
    compressed_payload: dict[str, object] = {
        "codes": codebook,
        "data": encoded_bitstream,
    }

    # ===== BYTE SERIALIZATION =====
    return json.dumps(
        compressed_payload
    ).encode("utf-8")


# ===== TEXT DECOMPRESSION =====
def decompress_text(data: bytes) -> str:

    # ===== PAYLOAD DESERIALIZATION =====
    compressed_payload: dict[str, Any] = (
        json.loads(
            data.decode("utf-8")
        )
    )

    # ===== COMPRESSED DATA =====
    codebook: dict[str, str] = (
        compressed_payload["codes"]
    )

    encoded_bitstream: str = (
        compressed_payload["data"]
    )

    # ===== REVERSE CODEBOOK =====
    reverse_codebook: dict[str, str] = {
        code: symbol
        for symbol, code
        in codebook.items()
    }

    # ===== DECODING STATE =====
    current_bits: str = ""
    decoded_symbols: list[str] = []

    # ===== BITSTREAM DECODING =====
    for bit in encoded_bitstream:

        current_bits += bit

        if current_bits in reverse_codebook:

            decoded_symbols.append(
                reverse_codebook[current_bits]
            )

            current_bits = ""

    # ===== TEXT RECONSTRUCTION =====
    return "".join(
        decoded_symbols
    )