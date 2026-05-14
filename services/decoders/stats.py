from services.decoders.common import ResponseDecoder

decode_skill_stats = ResponseDecoder.decode_skill_stats
decode_stats = ResponseDecoder.decode_stats

__all__ = ["decode_skill_stats", "decode_stats"]
