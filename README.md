# HTTP Request

Custom Home Assistant integration for calling HTTP endpoints from automations and scripts.

## Usage

### Send an HTTP request

```yaml
action:
  - service: http_request.request
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

### Create or update a file

```yaml
action:
  - service: http_request.write_file
    data:
      file_path: /config/sa.json
      data: '{"hello": "world"}'
```

If the file already exists, it will be overwritten. If it does not exist, it will be created.
