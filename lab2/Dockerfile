FROM python:3.9.0

WORKDIR .
COPY find_min_mtu.py .

COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "find_min_mtu.py"]
