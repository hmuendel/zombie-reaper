FROM python:alpine
RUN pip install requests

COPY reaper.py .
CMD ["python",  "-u", "./reaper.py"]



