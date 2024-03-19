# Verwenden des offiziellen Python 3.10 Alpine-Images als Basis
FROM python:3.11

# Installieren von Docker, GCC, G++ und anderen notwendigen Entwicklungswerkzeugen
#RUN apk update && \
#    apk add --no-cache gcc g++ musl-dev libffi-dev openssl-dev git

# Setzen des Arbeitsverzeichnisses im Container auf das Wurzelverzeichnis
WORKDIR /

# Kopieren der app.py, requirements.txt und des utils-Ordners in das Wurzelverzeichnis des Containers
COPY app.py requirements.txt run_app.sh / 
COPY config_task /config_task/
COPY config_model /config_model/
COPY model_wrapper /model_wrapper/
COPY data /data/
COPY utils /utils/

# Installieren der Python-Pakete aus der requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Herunterladen der Modelle und Speichern in einem Ordner namens "models"
RUN mkdir models
RUN mkdir -p models/flair/ner-german-large
RUN wget https://huggingface.co/TheBloke/SauerkrautLM-7B-v1-mistral-GGUF/resolve/main/sauerkrautlm-7b-v1-mistral.Q4_0.gguf -P models
RUN wget https://huggingface.co/flair/ner-german/resolve/main/pytorch_model.bin -P models/flair/ner-german-large

# Gewähren von Ausführungsrechten für das Start-Script
RUN chmod +x /run_app.sh

# Festlegen des Start-Scripts als Startpunkt des Containers
CMD ["/run_app.sh"]
