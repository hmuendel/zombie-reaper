FROM python
RUN pip install requests prometheus_client

COPY reaper.py .
COPY log_utils.py .
COPY startup.sh .

CMD ["/startup.sh"]



