pip install "mcp[cli]"

cline-win接入方式：
```json
{
  "mcpServers": {
    "station_operator": {
      "command": "python",
      "args": [
        "E:\\py_codes\\python-repo\\mcp-server\\operator.py"
      ]
    }
  }
}
```

根据上述请求体报文（json）分别使用json输出，并给出差异（第一个请求正常，第二个请求返回400）

Frame 27: 110 bytes on wire (880 bits), 110 bytes captured (880 bits) on interface \Device\NPF_Loopback, id 0
Null/Loopback
Internet Protocol Version 6, Src: ::1, Dst: ::1
Transmission Control Protocol, Src Port: 49989, Dst Port: 8080, Seq: 967, Ack: 591, Len: 46
[2 Reassembled TCP Segments (299 bytes): #25(253), #27(46)]
Hypertext Transfer Protocol
    POST /mcp/message?sessionID=64d00fc2-9745-4fbb-9b56-e3d9fd508587 HTTP/1.1\r\n
    Host: localhost:8080\r\n
    Accept: */*\r\n
    Accept-Encoding: gzip, deflate\r\n
    Connection: keep-alive\r\n
    User-Agent: python-httpx/0.28.1\r\n
    Content-Length: 46\r\n
    Content-Type: application/json\r\n
    \r\n
    [Response in frame: 30]
    [Full request URI: http://localhost:8080/mcp/message?sessionID=64d00fc2-9745-4fbb-9b56-e3d9fd508587]
    File Data: 46 bytes
JavaScript Object Notation: application/json
    Object
        Member: method
            [Path with value: /method:tools/list]
            [Member with value: method:tools/list]
            String value: tools/list
            Key: method
            [Path: /method]
        Member: jsonrpc
            [Path with value: /jsonrpc:2.0]
            [Member with value: jsonrpc:2.0]
            String value: 2.0
            Key: jsonrpc
            [Path: /jsonrpc]
        Member: id
            [Path with value: /id:1]
            [Member with value: id:1]
            Number value: 1
            Key: id
            [Path: /id]


------

Frame 56: 110 bytes on wire (880 bits), 110 bytes captured (880 bits) on interface \Device\NPF_Loopback, id 0
Null/Loopback
Internet Protocol Version 6, Src: ::1, Dst: ::1
Transmission Control Protocol, Src Port: 49992, Dst Port: 8080, Seq: 254, Ack: 1, Len: 46
[2 Reassembled TCP Segments (299 bytes): #54(253), #56(46)]
Hypertext Transfer Protocol
    POST /mcp/message?sessionID=64d00fc2-9745-4fbb-9b56-e3d9fd508587 HTTP/1.1\r\n
    Host: localhost:8080\r\n
    Accept: */*\r\n
    Accept-Encoding: gzip, deflate\r\n
    Connection: keep-alive\r\n
    User-Agent: python-httpx/0.28.1\r\n
    Content-Length: 46\r\n
    Content-Type: application/json\r\n
    \r\n
    [Response in frame: 58]
    [Full request URI: http://localhost:8080/mcp/message?sessionID=64d00fc2-9745-4fbb-9b56-e3d9fd508587]
    File Data: 46 bytes
JavaScript Object Notation: application/json
    Object
        Member: method
            [Path with value: /method:tools/list]
            [Member with value: method:tools/list]
            String value: tools/list
            Key: method
            [Path: /method]
        Member: jsonrpc
            [Path with value: /jsonrpc:2.0]
            [Member with value: jsonrpc:2.0]
            String value: 2.0
            Key: jsonrpc
            [Path: /jsonrpc]
        Member: id
            [Path with value: /id:2]
            [Member with value: id:2]
            Number value: 2
            Key: id
            [Path: /id]
