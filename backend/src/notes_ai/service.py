from groq import AsyncGroq

from src.utils.settings import settings


client = AsyncGroq(
    api_key=settings.GROQ_API_KEY
)

MAX_CHUNK_CHARACTERS = 12000


def split_text(text: str, max_characters: int = MAX_CHUNK_CHARACTERS) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks = []
    current_parts = []
    current_length = 0

    for paragraph in paragraphs:
        if len(paragraph) > max_characters:
            if current_parts:
                chunks.append("\n\n".join(current_parts))
                current_parts = []
                current_length = 0

            words = paragraph.split()
            word_parts = []
            word_length = 0
            for word in words:
                if word_parts and word_length + len(word) + 1 > max_characters:
                    chunks.append(" ".join(word_parts))
                    word_parts = []
                    word_length = 0
                word_parts.append(word)
                word_length += len(word) + 1
            if word_parts:
                current_parts = [" ".join(word_parts)]
                current_length = len(current_parts[0])
            continue

        separator_length = 2 if current_parts else 0
        if current_parts and current_length + separator_length + len(paragraph) > max_characters:
            chunks.append("\n\n".join(current_parts))
            current_parts = []
            current_length = 0

        current_parts.append(paragraph)
        current_length += separator_length + len(paragraph)

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks or [text]


async def _generate_notes_for_chunk(text: str) -> str:

    prompt = f"""
You are an AI study assistant.

Convert the following educational document into study notes in a
Question-and-Answer format.

For every important concept, create:

### Question
Write a clear question about the concept.

**Answer:**
Explain the answer in a clear paragraph using simple,
student-friendly language.

**Key Points:**
Provide 3-6 important points in bullet form.

Requirements:
- Cover all important concepts from the document.
- Do not invent information.
- Use only information available in the document.
- Answers should be explanatory paragraphs, not just one-line answers.
- Use bullet points only for the Key Points section.
- Include examples and code when they are important.
- Use Markdown headings.
- Make questions suitable for students preparing for exams.
- Avoid unnecessary repetition.
- Keep the content detailed but easy to understand.
- Do not create questions for trivial information.

Format the output exactly like this:

### 1. What is ...?

**Answer:**
[Paragraph explaining the answer]

**Key Points:**
- Point 1
- Point 2
- Point 3

### 2. What are ...?

**Answer:**
[Paragraph explaining the answer]

**Key Points:**
- Point 1
- Point 2
- Point 3

Document:

{text}
"""

    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert educational content and study-notes writer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_completion_tokens=4000
    )

    return response.choices[0].message.content


async def generate_notes(text: str) -> str:
    note_chunks = []
    for text_chunk in split_text(text):
        note_chunks.append(await _generate_notes_for_chunk(text_chunk))

    return "\n\n".join(note_chunks)