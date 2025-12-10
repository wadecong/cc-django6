"""
Django 6 Background Tasks for content processing.
Uses the new built-in tasks framework.
"""

from django.tasks import task, Task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@task()
def process_media_description(content_id: int) -> dict:
    """
    Background task to generate AI descriptions for media content.
    Uses Django 6's new Background Tasks feature.
    """
    from .models import Content, MediaDescription

    try:
        content = Content.objects.get(pk=content_id)
        content.processing_status = Content.ProcessingStatus.PROCESSING
        content.save(update_fields=["processing_status"])

        results = []

        # Process based on content type
        if content.content_type == Content.ContentType.IMAGE:
            # Generate image caption
            caption = _generate_image_caption(content)
            if caption:
                MediaDescription.objects.create(
                    content=content,
                    description_type=MediaDescription.DescriptionType.CAPTION,
                    text=caption["text"],
                    confidence=caption.get("confidence", 0.8),
                )
                results.append(caption)

            # Extract OCR text if applicable
            ocr_text = _extract_ocr_text(content)
            if ocr_text:
                MediaDescription.objects.create(
                    content=content,
                    description_type=MediaDescription.DescriptionType.OCR,
                    text=ocr_text["text"],
                    confidence=ocr_text.get("confidence", 0.9),
                )
                results.append(ocr_text)

            # Analyze if it's a meme
            meme_analysis = _analyze_meme(content)
            if meme_analysis:
                MediaDescription.objects.create(
                    content=content,
                    description_type=MediaDescription.DescriptionType.MEME,
                    text=meme_analysis["text"],
                    confidence=meme_analysis.get("confidence", 0.7),
                    metadata=meme_analysis.get("metadata", {}),
                )
                results.append(meme_analysis)

        elif content.content_type == Content.ContentType.VIDEO:
            # Generate video transcript
            transcript = _generate_video_transcript(content)
            if transcript:
                MediaDescription.objects.create(
                    content=content,
                    description_type=MediaDescription.DescriptionType.TRANSCRIPT,
                    text=transcript["text"],
                    confidence=transcript.get("confidence", 0.85),
                )
                results.append(transcript)

            # Generate scene descriptions
            scenes = _describe_video_scenes(content)
            if scenes:
                MediaDescription.objects.create(
                    content=content,
                    description_type=MediaDescription.DescriptionType.SCENE,
                    text=scenes["text"],
                    confidence=scenes.get("confidence", 0.75),
                    metadata=scenes.get("metadata", {}),
                )
                results.append(scenes)

        # Update AI description and summary
        all_descriptions = [r["text"] for r in results if r]
        if all_descriptions:
            content.ai_description = "\n\n".join(all_descriptions)
            content.ai_summary = _generate_summary(all_descriptions)

        content.processing_status = Content.ProcessingStatus.COMPLETED
        content.save()

        logger.info(f"Successfully processed content {content_id}")
        return {"status": "success", "content_id": content_id, "descriptions": len(results)}

    except Content.DoesNotExist:
        logger.error(f"Content {content_id} not found")
        return {"status": "error", "message": "Content not found"}
    except Exception as e:
        logger.exception(f"Error processing content {content_id}")
        try:
            content = Content.objects.get(pk=content_id)
            content.processing_status = Content.ProcessingStatus.FAILED
            content.save(update_fields=["processing_status"])
        except Content.DoesNotExist:
            pass
        return {"status": "error", "message": str(e)}


@task()
def generate_embedding(content_id: int) -> dict:
    """
    Generate vector embedding for semantic search.
    """
    from .models import Content

    try:
        content = Content.objects.get(pk=content_id)

        # Combine all text for embedding
        text_to_embed = " ".join(filter(None, [
            content.title,
            content.original_text,
            content.ai_description,
            content.ai_summary,
        ]))

        if text_to_embed:
            embedding = _generate_text_embedding(text_to_embed)
            content.embedding = embedding
            content.save(update_fields=["embedding"])
            logger.info(f"Generated embedding for content {content_id}")
            return {"status": "success", "content_id": content_id}

        return {"status": "skipped", "message": "No text to embed"}

    except Content.DoesNotExist:
        return {"status": "error", "message": "Content not found"}
    except Exception as e:
        logger.exception(f"Error generating embedding for {content_id}")
        return {"status": "error", "message": str(e)}


@task()
def auto_tag_content(content_id: int) -> dict:
    """
    Automatically generate tags for content using AI.
    """
    from .models import Content, Tag

    try:
        content = Content.objects.get(pk=content_id)

        text_for_tagging = " ".join(filter(None, [
            content.title,
            content.original_text,
            content.ai_description,
        ]))

        if not text_for_tagging:
            return {"status": "skipped", "message": "No text for tagging"}

        suggested_tags = _suggest_tags(text_for_tagging)

        created_tags = []
        for tag_name in suggested_tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.lower(),
                user=content.user,
                defaults={
                    "slug": tag_name.lower().replace(" ", "-"),
                    "is_auto_generated": True,
                }
            )
            content.tags.add(tag)
            if created:
                created_tags.append(tag_name)

        logger.info(f"Auto-tagged content {content_id} with {len(suggested_tags)} tags")
        return {
            "status": "success",
            "content_id": content_id,
            "tags": suggested_tags,
            "new_tags": created_tags,
        }

    except Content.DoesNotExist:
        return {"status": "error", "message": "Content not found"}
    except Exception as e:
        logger.exception(f"Error auto-tagging content {content_id}")
        return {"status": "error", "message": str(e)}


# Helper functions (placeholder implementations - integrate with real AI services)

def _generate_image_caption(content) -> dict | None:
    """Generate a caption for an image using AI vision model."""
    # TODO: Integrate with OpenAI Vision, Claude, or other vision APIs
    # Placeholder implementation
    if content.media_file or content.media_url:
        return {
            "text": f"[AI Caption] Image content from {content.platform.name if content.platform else 'unknown source'}",
            "confidence": 0.8,
        }
    return None


def _extract_ocr_text(content) -> dict | None:
    """Extract text from images using OCR."""
    # TODO: Integrate with Tesseract, Google Vision, or other OCR services
    if content.media_file or content.media_url:
        return {
            "text": "[OCR Text] Extracted text will appear here",
            "confidence": 0.9,
        }
    return None


def _analyze_meme(content) -> dict | None:
    """Analyze meme content for searchability."""
    # TODO: Integrate with AI for meme analysis
    if content.media_file or content.media_url:
        return {
            "text": "[Meme Analysis] This appears to be a meme image",
            "confidence": 0.7,
            "metadata": {
                "is_meme": True,
                "humor_type": "unknown",
            }
        }
    return None


def _generate_video_transcript(content) -> dict | None:
    """Generate transcript from video audio."""
    # TODO: Integrate with Whisper or other speech-to-text services
    if content.content_type == "video" and (content.media_file or content.media_url):
        return {
            "text": "[Transcript] Video transcript will appear here",
            "confidence": 0.85,
        }
    return None


def _describe_video_scenes(content) -> dict | None:
    """Generate descriptions of video scenes."""
    # TODO: Integrate with video analysis AI
    if content.content_type == "video" and (content.media_file or content.media_url):
        return {
            "text": "[Scene Description] Video scene analysis will appear here",
            "confidence": 0.75,
            "metadata": {
                "scene_count": 0,
                "duration": 0,
            }
        }
    return None


def _generate_summary(texts: list[str]) -> str:
    """Generate a summary from multiple text descriptions."""
    # TODO: Integrate with LLM for summarization
    combined = " ".join(texts)
    return combined[:500] if len(combined) > 500 else combined


def _generate_text_embedding(text: str) -> list[float]:
    """Generate vector embedding for text."""
    # TODO: Integrate with OpenAI embeddings or other embedding services
    # Placeholder: return dummy embedding
    import hashlib
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    # Generate a deterministic placeholder embedding
    return [(hash_val >> i) % 256 / 255.0 for i in range(settings.SEARCH_VECTOR_DIMENSIONS)]


def _suggest_tags(text: str) -> list[str]:
    """Suggest tags based on content text."""
    # TODO: Integrate with AI for tag suggestion
    # Placeholder: extract simple keywords
    common_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
    words = text.lower().split()
    tags = []
    for word in words:
        word = word.strip(".,!?\"'()[]{}").lower()
        if len(word) > 3 and word not in common_words and word not in tags:
            tags.append(word)
        if len(tags) >= 5:
            break
    return tags
