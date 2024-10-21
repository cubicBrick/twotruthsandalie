import index
from waitress import serve

serve(index.app, port="5000")
