from model.model import Customers

class ProducerKafka():
    def run(self):
       for i in range(0, 100):
            for j in range(1001, 1005):
                Customers.update(first_name=str(i)).where(Customers.id == j).execute()
                print("Update first_name of customer " + str(j) + " to " + str(i))

producer = ProducerKafka()
producer.run()