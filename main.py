from asyncio.log import logger
from urllib import response
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from fastapi import BackgroundTasks
import utils
import time, asyncio
from fastapi.encoders import jsonable_encoder
import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(10)
#if utils.log_key == None:
#    print("Configure log please")
#else:
#    lv_intkey = 'InstrumentationKey={}'.format(utils.log_key)
#    print(lv_intkey)
#    logger.addHandler(AzureLogHandler(connection_string=lv_intkey))
logger.addHandler(AzureLogHandler())

class Course(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    author: Optional[str] = None

class TextFileModel(BaseModel):
    language: str
    id: int
    text: str 

class Model(BaseModel):
    text_to_analyze: list[TextFileModel]

app = FastAPI()

course_items = [{"course_name":"python"}, {"course_name":"NodeJS"}, {"course_name":"PMP"}, {"course_name":"Excel"}]

@app.post("/courses/")
def create_course(course: Course):
    course_items.append(course)
    return {"course":course,"message":"Successfully added the course"}

@app.get("/")
def root():
    return {"message": "Hello world"}


@app.get("/courses/{course_id}")
def read_course(course_id:int, q: Optional[str] = None ):
    if q is not None:
        return {"course_name": course_items[course_id], "Quest": q}
    return {"course_name": course_items[course_id]}


#setted default value for start and end
@app.get("/courses/")
def read_courses(start: int = 0, end: int = 1):
    return course_items[start: start+end]


# Define background tasks to be run after returning a response( acknowledgement or confirmation )
def write_notification(email:str, message=""):
    with open("log.txt",mode ="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
def send_notification(email:str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification,email,message="Some NOtificatoin")
    return {"message":"NOtification sent in the background"}


# Define concurrent tasks
@app.get("/concur")
async def home():
    tasks = []
    start = time.time()
    for i in range(2):
        tasks.append(asyncio.create_task(func1()))
        tasks.append(asyncio.create_task(func2()))

    # We gather all the tasks and wait for them to be completed
    response = await asyncio.gather(*tasks)
    end = time.time()

    return {"response": response, "time_taken": (end - start)}

async def func1():

    #Await says it is safe to switch to another coroutine in the event loop
    await asyncio.sleep(1)
    return "Func1 completed"

async def func2():
    await asyncio.sleep(2)
    return "Func2 completed"

@app.post("/analyze/")
async def analyze_text(text: Model):
    response = { "sentiment": [], "keyphrases":[]}

    list_docs = json_compatible_item_data = jsonable_encoder(text.text_to_analyze)
    no_of_text = len(text.text_to_analyze)

    
    document = {"documents": list_docs }
    
    tasks = []
    tasks.append(asyncio.create_task(utils.get_sentiment(document=document)))
    tasks.append(asyncio.create_task(utils.get_key_phrases(document=document)))

    # We gather all the tasks and wait for them to be completed
    doc_analysis = await asyncio.gather(*tasks)
    doc_senti = doc_analysis[0]
    doc_keyphrases = doc_analysis[1]

    #doc_senti = utils.get_sentiment(document=document)
    #doc_keyphrases = utils.get_key_phrases(document=document)
    
    for i in range(no_of_text):
        try:
            response["sentiment"].append(doc_senti[i]['sentiment'])
            response["keyphrases"].append(doc_keyphrases[i]['keyPhrases'])

            log_data = {
                "custom_dimensions":
                {
                    "text": text.text_to_analyze[i].text,
                    "text_sentiment": doc_senti[i]['sentiment'],
                    "text_keyphrases": doc_keyphrases[i]['keyPhrases']
                }
            }
            logger.info('Text Processed Succesfully', extra=log_data)
        except:
            print( "No response {1}",i)

    
    return response
