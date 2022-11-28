FROM python:3.7-slim
RUN mkdir /app
### for local ###
#COPY requirements.txt /app
### for online ###
COPY ./backend/requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
### for local ###
#COPY apps/ /app
### for online ###
COPY ./backend/apps/ /app
WORKDIR /app
CMD ["gunicorn", "apps.wsgi:application", "--bind", "0:8000"]
