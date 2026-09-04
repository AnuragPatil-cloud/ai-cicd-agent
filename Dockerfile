FROM python:3.11-slim
WORKDIR /app
COPY README.md /app
CMD ["cat", "README.md"]
