import sys
import logging
logging.basicConfig(level=logging.INFO)

print("Loading modules...")
from memory import save_memory, retrieve_memories
from ai import generate_response

print("Modules loaded.")

print("Saving memory...")
save_memory("Remember that my interview is Friday")
print("Memory saved.")

print("Retrieving memories...")
memories = retrieve_memories("What did I say about interview?")
print("Retrieved memories:", memories)

print("Generating response...")
response = generate_response("What did I say about interview?", memories)
print("Response:", response)
