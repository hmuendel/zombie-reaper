FROM python:alpine
RUN pip install requests

COPY reaper.py .
COPY log_utils.py .
CMD ["python",  "-u", "./reaper.py"]



