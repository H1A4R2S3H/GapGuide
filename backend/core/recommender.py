import pandas as pd
import os
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobRecommender:
    def __init__(self, data_path):
        """
        Initializes the recommender by loading data and training the model.
        This runs only once when the class is first created.
        """
        print("Initializing JobRecommender...")
        try:
            self.df = pd.read_csv(data_path)
            # preprocess
            self.df['skills_list'] = self.df['skills_list'].apply(ast.literal_eval)
            self.df['skills_text'] = self.df['skills_list'].apply(lambda skills: ' '.join(skills))

            # training
            self.tfidf_vectorizer = TfidfVectorizer(token_pattern=r"\b[a-zA-Z0-9#+-]+\b")
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['skills_text'])
            
            print("JobRecommender initialized successfully.")
        except FileNotFoundError:
            print(f"Error: Data file not found at {data_path}")
            self.df = None

    def get_recommendations(self, user_skills: list, top_n: int = 20) -> list:
        
        if self.df is None:
            return []

        user_skills_text = ' '.join(user_skills)
        user_vector = self.tfidf_vectorizer.transform([user_skills_text])
        cosine_similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        top_job_indices = cosine_similarities.argsort()[:-top_n-1:-1]
        recommendations = self.df.iloc[top_job_indices]
        return recommendations.to_dict('records')


    def analyze_role_skill_gap(self, user_skills: list, job_title: str, top_n: int = 10) -> list:
    
        if self.df is None:
            return [{"error": "Dataset not loaded."}]

        matching_jobs = self.df[self.df['job_title'].str.contains(job_title, case=False, na=False)]#na=False means NaN will be ignored or excluded

        if matching_jobs.empty:
            return [{"error": f"No jobs found matching the title: '{job_title}'"}]

        jobs_to_analyze = matching_jobs.head(top_n)
    
        detailed_job_gaps = []
        user_skill_set = set([skill.lower() for skill in user_skills])

        for index, job_row in jobs_to_analyze.iterrows():
            required_skills = set([skill.lower() for skill in job_row['skills_list']])
        
            matching = user_skill_set.intersection(required_skills)
            missing = required_skills - user_skill_set
        
            detailed_job_gaps.append({
                "job_title": job_row['job_title'],
                "company": job_row['company'],
                "job_link": job_row['job_link'],
                "matching_skills": sorted(list(matching)),
                "missing_skills": sorted(list(missing))
            })

        return detailed_job_gaps