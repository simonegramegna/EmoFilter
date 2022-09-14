FROM python:3.10

WORKDIR /app
COPY . .

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]