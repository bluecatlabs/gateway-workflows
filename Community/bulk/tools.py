from flask import jsonify
from werkzeug.utils import secure_filename
from main_app import app
import uuid
import os
import json
class tools:

    @staticmethod
    def load_file_json_to_dict(file="tools.json"):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        json_data = open(dir_path + "/" +file).read()
        data = json.loads(json_data)
        return data

    @staticmethod
    def is_an_int(input):
        try:
            int(input)
        except:
            return False
        return True

    @staticmethod
    def make_status(status, output, error=""):
        config = tools.load_file_json_to_dict()
        if status == None:
            ret = {config['API_STATUS_NAME']:config['API_ERROR_NONFATAL_STATUS'],config['API_ERROR_FIELD']:error.replace('"', '')}
        elif status:
            ret = {config['API_STATUS_NAME']:config['API_SUCCESS_STATUS'],config['API_DATA_FIELD']:output}
        else:
            ret = {config['API_STATUS_NAME']:config['API_ERROR_STATUS'],config['API_ERROR_FIELD']:error.replace('"', '')}

        return jsonify(ret)

    @staticmethod
    def save_file(file, path='/tmp/'):
        filename = os.path.join(path, secure_filename(file.filename))
        file.save(filename)
        new_file_path = path + tools.get_random_string(20) + "-" + file.filename
        os.rename(filename, new_file_path)
        return new_file_path

    @staticmethod
    def get_random_string(string_length=10):
        random = str(uuid.uuid4())
        random = random.upper()
        random = random.replace("-", "")
        return random[0:string_length]

    @staticmethod
    def parse_csv_to_dict(file_contents, start=1, length=None):
        content = file_contents.strip()
        contents_as_rows = content.split("\n")
        if len(contents_as_rows) in (0, 1):
            app.logger.error("There's only a header row or no content at all")
            return False

        fields = contents_as_rows[0].split(',')

        file_contents_as_dict = {}
        try:
            x = contents_as_rows[start]
        except:
            app.logger.info('We hit the end of the file')
            raise IndexError('We hit the end of the file')

        for i in range(start, len(contents_as_rows) if length == None else length):
            try:
                current_row = contents_as_rows[i].split(',')
            except:
                app.logger.info("We hit the end of file during an iteration, next one will be done")
                break
            if len(current_row) != len(fields):
                app.logger.error("Mismatch in values")
                return False
            else:
                file_contents_as_dict[i] = {}
                for index in range(0, len(current_row)):
                    file_contents_as_dict[i][fields[index].rstrip()] = current_row[index].rstrip()
        return file_contents_as_dict
