FROM python:3.11.10-slim
RUN pip install PyYAML==6.0.2
RUN pip install jsonschema==4.23.0
ENV PYTHONPATH="/app"
