# Run producer server
run-producer:
  uvicorn src.examples.producer_example.main:app --reload --port 8000

# Run consumer server
run-consumer:
  uvicorn src.examples.consumer_example.main:app --reload --port 8001

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
  curl -s -X POST "http://localhost:8000/producers/person?number_of_people={{NUMBER_OF_PEOPLE}}" \
    -H "accept: application/json" | jq .
