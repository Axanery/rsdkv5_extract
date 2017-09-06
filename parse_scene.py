from construct import *
import sys

String = PascalString(Byte)
Word = Int16ul
Dword = Int32ul

def CompressedZlib(subcon):
    # Compressed zlib, prefixed with a dword for the size of the compressed data (including the big endian dword with the size of the uncompressed data)
    return Prefixed(Dword, FocusedSeq(1,
        "uncompressed_length" / Int32ub,
        "compressed_data" / Compressed(subcon, "zlib"),
    ))

SCN = Struct(
    "magic" / Const("SCN\0"),

    # Ignored
    "skipped_header" / Bytes(16),
    # Name of some bin file
    "skipped_bin_name" / String,
    "skipped_byte" / Byte,

    "Views" / PrefixedArray(Byte, Struct(
        # This is read as part as the length of next string, and ignored
        "ignored_byte" / Byte,
        "Name" / String,

        "unknown_byte_1" / Byte,
        "unknown_byte_2" / Byte,

        "Width" / Word,
        "Height" / Word,

        "unknown_word_5" / Word,
        "unknown_word_6" / Word,

        "some_array" / PrefixedArray(Word, Struct(
            "unknown_word_1" / Word,
            "unknown_word_2" / Word,
            "unknown_byte_1" / Byte,
            "unknown_byte_2" / Byte,
        )),

        "some_array" / CompressedZlib(Bytes(this.Height * 0x10)),

        "Tiles" / CompressedZlib(Array(this.Width * this.Height, Word))
    )),

    "bytecode_things" / PrefixedArray(Byte, Struct(
        # TODO
    ))

)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_scene.py SceneX.bin")
        sys.exit(-1)

    if not sys.argv[1].endswith(".bin"):
        print("Expected .bin file")
        sys.exit(-1)

    scene = SCN.parse(open(sys.argv[1], "rb").read())
    print(scene)