FROM python:3.11.10-slim
RUN pip install PyYAML==6.0.2
ENV PYTHONPATH="/app"
