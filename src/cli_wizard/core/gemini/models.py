from enum import StrEnum


class GeminiModels(StrEnum):
    """
    Supported Gemini model IDs.

    Note:
        Gemini model availability changes over time. For a live list, use the
        Gemini API models endpoint.
    """

    # Gemini 3.5
    GEMINI_3_5_FLASH = "gemini-3.5-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"

    # Gemini 3
    # GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"
    # GEMINI_3_PRO_IMAGE_PREVIEW = "gemini-3-pro-image-preview"
    # GEMINI_3_FLASH_IMAGE_PREVIEW = "gemini-3-flash-image-preview"
    #
    # # Gemini 2.5
    # GEMINI_2_5_PRO = "gemini-2.5-pro"
    # GEMINI_2_5_FLASH = "gemini-2.5-flash"
    # GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
    # GEMINI_2_5_FLASH_IMAGE_PREVIEW = "gemini-2.5-flash-image-preview"
    # GEMINI_2_5_FLASH_PREVIEW_TTS = "gemini-2.5-flash-preview-tts"
    # GEMINI_2_5_PRO_PREVIEW_TTS = "gemini-2.5-pro-preview-tts"
    # GEMINI_2_5_FLASH_LIVE = "gemini-2.5-flash-live"
    # GEMINI_2_5_FLASH_NATIVE_AUDIO_PREVIEW = "gemini-2.5-flash-native-audio-preview"
    # GEMINI_2_5_FLASH_EXP_NATIVE_AUDIO_THINKING_DIALOG = (
    #     "gemini-2.5-flash-exp-native-audio-thinking-dialog"
    # )
    #
    # # Gemini 2.0
    # GEMINI_2_0_FLASH = "gemini-2.0-flash"
    # GEMINI_2_0_FLASH_001 = "gemini-2.0-flash-001"
    # GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    # GEMINI_2_0_FLASH_LITE_001 = "gemini-2.0-flash-lite-001"
    # GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION = (
    #     "gemini-2.0-flash-preview-image-generation"
    # )
    # GEMINI_2_0_FLASH_LIVE = "gemini-2.0-flash-live"
    # GEMINI_2_0_FLASH_LIVE_001 = "gemini-2.0-flash-live-001"
    # GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
    #
    # # Gemini 1.5
    # GEMINI_1_5_PRO = "gemini-1.5-pro"
    # GEMINI_1_5_PRO_001 = "gemini-1.5-pro-001"
    # GEMINI_1_5_PRO_002 = "gemini-1.5-pro-002"
    # GEMINI_1_5_FLASH = "gemini-1.5-flash"
    # GEMINI_1_5_FLASH_001 = "gemini-1.5-flash-001"
    # GEMINI_1_5_FLASH_002 = "gemini-1.5-flash-002"
    # GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    # GEMINI_1_5_FLASH_8B_001 = "gemini-1.5-flash-8b-001"
    #
    # # Embeddings
    # GEMINI_EMBEDDING_001 = "gemini-embedding-001"
    # TEXT_EMBEDDING_004 = "text-embedding-004"
    #
    # # Imagen
    # IMAGEN_4_0_GENERATE_001 = "imagen-4.0-generate-001"
    # IMAGEN_4_0_ULTRA_GENERATE_001 = "imagen-4.0-ultra-generate-001"
    # IMAGEN_4_0_FAST_GENERATE_001 = "imagen-4.0-fast-generate-001"
    # IMAGEN_3_0_GENERATE_002 = "imagen-3.0-generate-002"
    #
    # # Veo
    # VEO_3_1_GENERATE_PREVIEW = "veo-3.1-generate-preview"
    # VEO_3_1_FAST_GENERATE_PREVIEW = "veo-3.1-fast-generate-preview"
    # VEO_3_0_GENERATE_PREVIEW = "veo-3.0-generate-preview"
    # VEO_3_0_FAST_GENERATE_PREVIEW = "veo-3.0-fast-generate-preview"
    # VEO_2_0_GENERATE_001 = "veo-2.0-generate-001"
    #
    # # Lyria
    # LYRIA_REALTIME_EXP = "lyria-realtime-exp"