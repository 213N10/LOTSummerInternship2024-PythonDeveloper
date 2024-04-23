import sys,os,json,dicttoxml,time,logging as log,shutil as sh

#Setting up variables
#these values are big just for testing purposes
SLEEP_TIME = 3
TIME_FROM_LAST_MODIFIED = 10

#set up the logger to not log the dicttoxml logs to avoid cluttering the logs
log.basicConfig(filename='json2xml.log', level=log.INFO, format='%(asctime)s %(message)s')
log.getLogger('dicttoxml').setLevel(log.ERROR)

#read the source path and destination path from the command line
try:
  source_path = os.path.abspath(sys.argv[1])
  destination_path = os.path.abspath(sys.argv[2])
  
except (IndexError) as e:
  print("Please provide the source path and destination path")
  print("Usage: python json2xml.py <source_path> <destination_path>")
  print("Example: python json2xml.py /path/to/source /path/to/destination")
  print(e)
  sys.exit(1)
  

try:
  os.makedirs("error-files", exist_ok=True)
except OSError as e:
  log.error(f"Error creating error-files directory: {e}")
  sys.exit(1)


while True:
  time.sleep(SLEEP_TIME) 
  # read the files in the source path
  try:
    files = os.listdir(source_path)
  except OSError as e:
    log.error(f"Error reading source path {source_path}: {e}")
    break

  # iterate over the files and convert them to xml
  for file in files:
    file_path = os.path.join(source_path, file)
    # check if the file is a json file might change to rm files if needeed
    if not file.endswith(".json"):
      sh.move(file_path, "error-files")

    # check if the file is empty
    try:
      with open(file_path, 'r') as file1:
        file_content = file1.read().strip()
      if not file_content:  # returns True if empty or False if not empty
        log.error(f"File {file} is empty")
        sh.move(file_path, "error-files")
        continue
    except OSError as e:
      log.error(f"Error reading file {file}: {e}")
      continue
    
    last_modified = os.path.getmtime(file_path)
    current_time = time.time()
    """ alternatively might try to use os.rename(file, file)
    to check if file is used by other program.
    It was hard to manually test it because of the way linux buffors work.
    I tried it with opening and editing file in neovim but Ive got an error in nvim that the file was removed. 
    """
    
    if current_time - last_modified > TIME_FROM_LAST_MODIFIED:
      # if the file was modified more than TIME_FROM_LAST_MODIFIED seconds ago, convert it to xml
      try:
        parsed_json = json.loads(file_content)
      except json.JSONDecodeError as e:
        log.error(f"Error decoding json file {file}:\n {e}")
        continue
      try:
      # create the destination path if it does not exist 
        os.makedirs(destination_path, exist_ok=True) 
        xml_data = dicttoxml.dicttoxml(parsed_json)
        xml_path = os.path.join(destination_path, file.replace('.json', '.xml'))
        with open(xml_path, "wb") as f:
          f.write(xml_data)
          log.info(f"File {file} converted to {xml_path} successfully")

      except Exception as e:
        log.error(f"Error converting file {file}: {e}")
        continue
      try:
        os.remove(file_path)
      except OSError as e:
        log.error(f"Error removing file {file}: {e}")
        continue

