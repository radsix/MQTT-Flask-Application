from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# MQTT Broker details
broker_address = "192.168.1.110"  # IP address of the MQTT broker
broker_port = 1883  # Default MQTT port
publish_topic = "conveyor"  # Topic to publish messages to
subscribe_topic = "conveyor"  # Topic to subscribe to for conveyor status

# Flag to store conveyor status
conveyor_status = "Off"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to conveyor topic when connected
    client.subscribe(subscribe_topic)

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))

def on_message(client, userdata, msg):
    global conveyor_status
    print("Received message: "+msg.payload.decode())
    # Update conveyor status based on received message
    if msg.payload.decode() == "resp go":
        conveyor_status = "On" 
    elif msg.payload.decode() == "resp stop":
        conveyor_status = "Off"

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(broker_address, broker_port, 60)

@app.route('/')
def index():
    return render_template('index.html', conveyor_status=conveyor_status)

@app.route('/conveyor_status')
def get_conveyor_status():
    return jsonify({'conveyor_status': conveyor_status})

@app.route('/publish', methods=['POST'])
def publish():
    message = request.form['message']
    if message.lower() == 'go' or message.lower() == 'stop':
        client.publish(publish_topic, message)
        return "Message published successfully: " + message
    else:
        return "Invalid input. Please try again."

if __name__ == '__main__':
    client.loop_start()  # Start MQTT client loop
    app.run(host='0.0.0.0', port=5000, debug=True)