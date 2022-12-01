import importlib
import sys

argv = sys.argv
print('START WORKER ' + str(argv[1]))

# GET DATA FROM CONSOLE
module_name = argv[1]
class_name = argv[2]
full_path = 'scripts.' + module_name if module_name == 'consumer' else 'scripts.' + module_name + '.' + class_name

module = importlib.import_module(full_path)
service = getattr(module, class_name)

# Init class
service_instance = service()
#
# # Run
service_instance.run()
