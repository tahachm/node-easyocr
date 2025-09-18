import sys
import json
import easyocr
import base64
from io import BytesIO
from PIL import Image
import numpy as np

reader = None

def init_reader(languages):
    global reader
    reader = easyocr.Reader(languages)
    return json.dumps({"status": "success", "message": "Reader initialized"})

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False

def read_text(image):
    if reader is None:
        return json.dumps({"status": "error", "message": "Reader not initialized"})
    
    if (is_base64(image)):
        image_data = base64.b64decode(image)
        image = Image.open(BytesIO(image_data)).convert('RGB')
    
    result = reader.readtext(image)
    return json.dumps({
        "status": "success",
        "data": [{
            'bbox': [[int(coord) for coord in point] for point in bbox],
            'text': text,
            'confidence': float(conf)
        } for (bbox, text, conf) in result]
    })

def process_command(command, args):
    if command == 'init':
        return init_reader(args)
    elif command == 'read_text':
        return read_text(args[0])
    elif command == 'close':
        return json.dumps({"status": "success", "message": "Closing process"})
    else:
        return json.dumps({"status": "error", "message": "Invalid command"})

if __name__ == '__main__':
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:
                break
            
            command, *args = line.split()
            result = process_command(command, args)
            
            sys.stdout.write(result + '\n')
            sys.stdout.flush()
            
            if command == 'close':
                break
        except Exception as e:
            sys.stdout.write(json.dumps({"status": "error", "message": str(e)}) + '\n')
            sys.stdout.flush()