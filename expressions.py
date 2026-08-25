"""
Expression presets optimized for Qwen-Image-Edit (instruction-based editing).

These prompts are written as *edit instructions* that preserve identity,
outfit, lighting and composition while changing only the expression / micro-pose.
"""

from typing import Dict, List

# Classic SillyTavern / Lumiverse expression set (28)
STANDARD_EXPRESSIONS: Dict[str, str] = {
    "joy": "Change her expression to a genuine happy smile with bright eyes, soft joyful look, keep everything else identical",
    "happiness": "Make her look happily content with a warm smile and relaxed eyes, keep face structure and outfit identical",
    "sadness": "Change expression to soft sadness, slightly downturned eyes and mouth, subtle melancholy, preserve identity",
    "sorrow": "Give her a sorrowful expression with wet eyes and a slight frown, keep all other details the same",
    "anger": "Change to an angry expression with furrowed brows and intense stare, keep identity and clothing identical",
    "rage": "Make her look furious with clenched jaw and fierce eyes, preserve exact face and outfit",
    "surprise": "Change expression to wide-eyed surprise with slightly open mouth, keep everything else the same",
    "shock": "Give her a shocked expression with raised eyebrows and open mouth, identity locked",
    "fear": "Change to a fearful look with wide worried eyes, keep face and body identical",
    "terror": "Make her look terrified with wide eyes and tense expression, preserve all other details",
    "disgust": "Change expression to mild disgust with wrinkled nose and slightly downturned mouth",
    "contempt": "Give her a contemptuous look with a slight sneer and narrowed eyes",
    "neutral": "Change to a completely neutral relaxed expression, soft natural face, keep identity",
    "calm": "Make her look calm and peaceful with soft eyes and relaxed mouth",
    "confused": "Change to a confused expression with slightly furrowed brows and tilted head feel",
    "curious": "Give her a curious interested look with raised brows and attentive eyes",
    "thinking": "Change expression to thoughtful, eyes looking slightly upward, soft contemplative look",
    "serious": "Make her look serious and focused with a firm neutral expression",
    "smug": "Change to a smug self-satisfied expression with a small confident smirk",
    "confident": "Give her a confident look with direct eye contact and slight smile",
    "embarrassed": "Change to an embarrassed expression with a soft blush and averted eyes",
    "shy": "Make her look shy with a gentle smile and slightly lowered gaze",
    "love": "Change expression to soft loving affection with warm eyes and gentle smile",
    "desire": "Give her a desirous expression with half-lidded eyes and parted lips, sensual but soft",
    "arousal": "Change to a subtly aroused look with flushed cheeks, soft open mouth and heavy lids",
    "pain": "Make her look like she is in mild pain with a slight grimace and tense brow",
    "tired": "Change expression to tired/weary with half-closed eyes and soft exhausted look",
    "bored": "Give her a bored expression with slightly downturned mouth and uninterested eyes",
}

# Extra NSFW / sensual expressions (great for your content pipeline)
NSFW_EXPRESSIONS: Dict[str, str] = {
    "flirty": "Change expression to a flirty teasing look with a playful smirk and direct eye contact, keep outfit and body identical",
    "seductive": "Make her expression seductive with half-lidded eyes, soft parted lips and a knowing smile",
    "teasing": "Change to a mischievous teasing expression, slight head tilt and playful eyes",
    "lustful": "Give her a lustful look with heavy lids, flushed cheeks and slightly open mouth",
    "bliss": "Change expression to eyes closed in soft pleasure with open mouth and relaxed face",
    "needy": "Make her look needy and pleading with soft eyes and parted lips",
    "dominant": "Change to a dominant confident stare with intense eyes and slight smirk",
    "submissive": "Give her a soft submissive look with lowered eyes and gentle open mouth",
    "ahegao_soft": "Change to a soft ahegao-style expression: eyes rolled up slightly, tongue tip out, flushed, keep realistic",
    "afterglow": "Make her look post-orgasm afterglow: soft satisfied eyes, flushed skin, relaxed mouth",
    "pout": "Change to a cute pout with slightly pursed lips and big eyes",
    "wink": "Give her a playful wink with one eye closed and a small smile",
}

# Combined for the UI
ALL_PRESETS = {
    "standard_28": STANDARD_EXPRESSIONS,
    "nsfw_extra": NSFW_EXPRESSIONS,
    "full_pack": {**STANDARD_EXPRESSIONS, **NSFW_EXPRESSIONS},
}

def get_expression_list(preset: str = "full_pack") -> List[str]:
    return list(ALL_PRESETS.get(preset, ALL_PRESETS["full_pack"]).keys())

def get_prompt(expression: str, preset: str = "full_pack") -> str:
    mapping = ALL_PRESETS.get(preset, ALL_PRESETS["full_pack"])
    return mapping.get(expression, f"Change her expression to {expression}, keep face structure, hair, outfit and lighting identical")
