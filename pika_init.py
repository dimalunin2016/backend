
from flask import g
import pika
from web_app import app

def connect_queue():  
    if not hasattr(g, 'rabbitmq'):                                                                    
        g.rabbitmq = pika.BlockingConnection(                                                         
            pika.ConnectionParameters(app.config['RABBITMQ_HOST'], 5672)                                    
        )                                                                                             
    return g.rabbitmq                                                                                 

def get_welcome_queue():  
    if not hasattr(g, 'welcome_queue'):                                                               
        conn = connect_queue()                                                                        
        channel = conn.channel()                                                                      
        channel.queue_declare(queue='email-queue', durable=True)                                                                 
        g.welcome_queue = channel                                                                     
    return g.welcome_queue                                                                            

@app.teardown_appcontext                                                                              
def close_queue(error): 
    if hasattr(g, 'rabbitmq'):                                                                        
        g.rabbitmq.close()
