FROM python:3.8

RUN mkdir -p /usr/src/currencyMonitor
WORKDIR /usr/src/currencyMonitor

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./run_in_container.py" ]