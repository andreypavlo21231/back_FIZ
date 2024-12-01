from sentence_transformers import SentenceTransformer, util

def assess_candidate_with_ai(resume_text, job_description):

    model = SentenceTransformer('all-MiniLM-L6-v2')

    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)

    similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding)[0][0].item()

    return similarity_score
    #
