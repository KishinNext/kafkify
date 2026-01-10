# Health check producer server
health-producer: 
  curl -s GET "http://localhost:8000/health-check" \
    -H "accept: application/json" | jq .

# Health check consumer server
health-consumer: 
  curl -s GET "http://localhost:8001/health-check" \
    -H "accept: application/json" | jq .

# Create people (send messages to topic)
create-people NUMBER_OF_PEOPLE:
  curl -s -X POST "http://localhost:8000/producers/basic_producer?number_of_people={{NUMBER_OF_PEOPLE}}" \
    -H "accept: application/json" | jq .

# Get consumer status
consumer-status: 
  curl -s GET "http://localhost:8001/consumers/status" \
    -H "accept: application/json" | jq .

# Get last consumed messages
consumer-messages LIMIT="10": 
  curl -s GET "http://localhost:8001/consumers/messages?limit={{LIMIT}}" \
    -H "accept: application/json" | jq .

# Stop consumer
consumer-stop: 
  curl -s -X POST "http://localhost:8001/consumers/stop" \
    -H "accept: application/json" | jq .

# Start consumer (if stopped)
consumer-start: 
  curl -s -X POST "http://localhost:8001/consumers/start" \
    -H "accept: application/json" | jq .
