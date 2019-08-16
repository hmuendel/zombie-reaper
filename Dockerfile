FROM python:alpine
RUN pip install requests
USER reaper

COPY reaper.py .
CMD ["/reaper.py"]



