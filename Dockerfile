FROM python:alpine
RUN pip install requests prometheus_client

COPY reaper.py .
COPY log_utils.py .
CMD ["python",  "-u", "./reaper.py"]



