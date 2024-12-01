import fitz 
# from neuro import extract_fields,assess_candidate,extract_entities
# from neuro_test_2 import assess_candidate_with_ai
def get_text_from_pathfile(filepath):
    doc = fitz.open(filepath)
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num) 
        full_text += page.get_text()  

    return(full_text)
# resume_text = """
# Денис Кологреев, 34 года, программист. 
# Опыт работы: Python (4 года), Selenium (автоматизация), MySQL, Docker. 
# Контакты: email@example.com, +79123456789.
# """
# job_description = (
    # "Python разработчик, требования: владение Python, Selenium, Requests, Docker, SQL, MySQL, BeautifulSoup, "
    # "Опыт работы — 5."
# )
# questions = [
        # "Как зовут человека?",
        # "Какие навыки указаны в резюме?",
        # "Какие контактные данные есть в резюме?",
        # "Сколько лет опыта работы?", 
        # "Какую должность ищет человек?",
        # "Какие технологии упоминаются в тексте?",
       # "Насколько от 1 до 100 человек подходит на вакансию с требованиями Python, Selenium, от 6 лет работы? В ответе только число"
    # ]
# print(extract_entities(get_text_from_pathfile('1.pdf')))
# print(assess_candidate(get_text_from_pathfile('1.pdf'),job_requirements))
# print(extract_fields(resume_text,questions))
# assessment = assess_candidate_with_ai(get_text_from_pathfile('2.pdf'), job_description)
# print("Оценка соответствия кандидата:")
# print(assessment)
