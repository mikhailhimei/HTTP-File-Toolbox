# HTTP File Toolbox

A custom Home Assistant integration that allows automations and scripts to send HTTP requests and work with local files.

## Features

* Supports `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, and `OPTIONS`
* Custom headers
* JSON and text request bodies
* Returns the HTTP response to a variable
* Automatic JSON parsing when the response content type is `application/json`
* Creates or overwrites files from automation data
* Reads files into a response variable as either plain text or parsed JSON

## Installation

Copy the `custom_components/HTTP_File_Toolbox` folder into your Home Assistant `custom_components` directory and restart Home Assistant.

## Examples

### Send an HTTP request

```yaml
action:
  - service: http_file_toolbox.request
    data:
      method: POST
      url: https://example.com/api
      headers:
        Content-Type: application/json
        Authorization: Bearer token
      body:
        foo: bar
    response_variable: http_result
```

If the response has a JSON content type, the service returns parsed JSON in `http_result.body`.

You can also access:

* `http_result.status`
* `http_result.headers`
* `http_result.body`

### Create or update a file

```yaml
action:
  - service: http_file_toolbox.write_file
    data:
      file_path: /config/sa.json
      data:
        hello: world
```

If the file already exists, it will be overwritten. If it does not exist, it will be created.

### Read a file into a variable

Read a text file:

```yaml
action:
  - service: http_file_toolbox.read_file
    data:
      file_path: /config/message.txt
      format: txt
    response_variable: file_result
```

Read and parse a JSON file:

```yaml
action:
  - service: http_file_toolbox.read_file
    data:
      file_path: /config/sa.json
      format: json
    response_variable: file_result
```

The file content is available in `file_result.data`. The service also returns `file_result.path` and `file_result.format`.

## Use Cases

* Trigger webhooks
* Control external devices
* Send notifications to third-party services
* Integrate with REST APIs
* Exchange data with custom applications
* Store and reuse file data in Home Assistant automations

## License

MIT License.
