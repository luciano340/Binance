from prometheus_client import Counter, Gauge, Summary, Histogram

#Binance Metrics
function_counter = Counter('function_call_counter', 'Check the number of time that a function was called', ['function_name'])
function_error_counter = Counter('function_error_counter', 'Check the number of time that a function was called and raise an error')
broker_timer = Histogram('broker_time', 'Check the brokers total response time', ['endpoint'])