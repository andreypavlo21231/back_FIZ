from transformers import pipeline
import re

# Модели для извлечения данных
qa_model = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2")
ner_pipeline = pipeline("ner", model="timpal0l/mdeberta-v3-base-squad2", grouped_entities=True)


def preprocess_text(resume_text):
    """
    Очищает и форматирует текст резюме для обработки.
    """
    clean_text = resume_text.replace("\n", " ").strip()
    clean_text = re.sub(r"\s+", " ", clean_text)  # Убираем лишние пробелы
    return clean_text


def extract_entities(resume_text):
    """
    Извлекает сущности из текста с использованием NER-модели.
    """
    entities = ner_pipeline(resume_text)
    extracted_data = {"name": [], "skills": [], "contacts": []}

    for entity in entities:
        if entity['entity_group'] == 'PER':  # Личные имена
            extracted_data['name'].append(entity['word'])
        elif entity['entity_group'] == 'ORG' or entity['entity_group'] == 'SKILL':  # Навыки, компании
            extracted_data['skills'].append(entity['word'])
        elif entity['entity_group'] == 'EMAIL':  # Контакты
            extracted_data['contacts'].append(entity['word'])

    return extracted_data


def extract_fields(resume_text, questions):
    """
    Отвечает на заданные вопросы по тексту резюме.
    """
    resume_text = preprocess_text(resume_text)  # Предобработка текста
    # print(resume_text)
    extracted_fields = {}

    for question in questions:
        try:
            result = qa_model({
                'context': resume_text,
                'question': question
            })
            extracted_fields[question] = result['answer']
        except Exception as e:
            extracted_fields[question] = f"Ошибка: {str(e)}"

    return extracted_fields
def assess_candidate(resume_text, job_requirements):
    """
    Оценивает соответствие кандидата требованиям вакансии.
    """
    # Распаковка требований вакансии
    required_position = job_requirements.get("position", "").lower()
    required_stack = set([tech.lower() for tech in job_requirements.get("stack", [])])
    min_experience = job_requirements.get("experience", 0)

    # Извлечение информации из резюме
    resume_info = extract_entities(resume_text)
    resume_fields = extract_fields(
        resume_text, 
        ["Какую должность ищет человек?", "Сколько лет опыта работы у человека?", "Какие технологии указаны в резюме?"]
    )

    # Преобразование данных
    candidate_position = resume_fields.get("Какую должность ищет человек?", "").lower()
    candidate_experience = resume_fields.get("Сколько лет опыта работы у человека?", "0").split()
    candidate_experience_years = (
        int(candidate_experience[0]) if candidate_experience and candidate_experience[0].isdigit() else 0
    )
    candidate_stack = set([tech.lower() for tech in resume_info.get("skills", [])])

    # Оценка соответствия
    position_match = required_position in candidate_position
    experience_match = candidate_experience_years >= min_experience
    stack_match = required_stack.issubset(candidate_stack)

    # Финальная оценка
    score = sum([position_match, experience_match, stack_match]) / 3 * 100

    # Подробное объяснение
    explanation = {
        "Position match": "Да" if position_match else "Нет",
        "Experience match": f"{candidate_experience_years} лет (требуется {min_experience})",
        "Stack match": f"{', '.join(required_stack)} (совпадает: {', '.join(required_stack & candidate_stack)})",
    }

    return {
        "score": score,
        "explanation": explanation
    }
