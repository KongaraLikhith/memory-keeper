FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Set up a non-root user for security (required by HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

# Start the FastAPI app on port 7860
CMD ["uvicorn", "app:fast_app", "--host", "0.0.0.0", "--port", "7860"]
