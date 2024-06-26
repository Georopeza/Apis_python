import threading
import time


class PubSub:
    """
    __init__: Inicializa una lista vacía de suscriptores.
    subscribe: Añade una función de suscriptor a la lista de suscriptores.
    publish: Llama a cada función suscriptora con el mensaje publicado.
    """
    def __init__(self):
        self.subscribers = []
    """
    callback: es una función que se pasa a otra función como un argumento, 
    que luego se invoca dentro de la función externa para completar algún 
    tipo de rutina o acción
    """
    def subscribe(self, callback):
        self.subscribers.append(callback)
        print(f"Subscribed: {callback}")

    def publish(self, message):
        for subscriber in self.subscribers:
            subscriber(message)
        print(f"Published: {message}")

# Función para simular un productor
def producer(pubsub):
    """
    Publica una serie de mensajes con un retraso de un segundo entre cada mensaje.
    """
    messages = ["Hola", "Mundo", "desde", "el patrón","PubSub"]
    for message in messages:
        pubsub.publish(message)
        time.sleep(1)

# Funciones para simular consumidores
# Imprimen el mensaje recibido, simulando la recepción 
# de eventos por parte de los suscriptores.
def consumer_1(message):
    print(f"Consumer 1 received: {message}")

def consumer_2(message):
    print(f"Consumer 2 received: {message}")

# Crear una instancia de PubSub
pubsub = PubSub()

# Suscribir consumidores
pubsub.subscribe(consumer_1)
pubsub.subscribe(consumer_2)

# Crear un hilo para el productor
producer_thread = threading.Thread(target=producer, args=(pubsub,))
producer_thread.start()
producer_thread.join()
