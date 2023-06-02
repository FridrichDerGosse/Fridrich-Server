FROM python:3.11
LABEL authors="Lukas3000"

ADD main.py .

RUN pip install scikit-learn

CMD ["python", "./main.py"]
