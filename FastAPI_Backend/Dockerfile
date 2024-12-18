# backend/Dockerfile

FROM python:3.10.8

RUN mkdir -p app/backend

COPY FastAPI_Backend/requirements.txt app/backend/requirements.txt
COPY Data app/Data

COPY FastAPI_Backend app/backend

WORKDIR /app/backend

ENV GEMINI_API_KEY=AIzaSyB1MmZbCp3D9RkinB_Res1Dly_ps1OsY-g

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080","--reload"]