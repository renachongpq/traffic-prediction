FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install
RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]