import os
from pathlib import Path

import arrow
from flask import Flask, abort, request, Response
from werkzeug.http import parse_range_header

KEY_PATH = r'C:\DATA\PKI\pyazurite.key'  # FIXME
CERT_PATH = r'C:\DATA\PKI\pyazurite.pem'  # FIXME

app = Flask(__name__)
data_folder = Path(r'C:\DATA')  # FIXME


@app.route('/blob/<path:path>', methods=['HEAD', 'GET'])
def web_blob(path):
    cur_path = data_folder / path

    if not cur_path.exists():
        abort(404)

    if request.method == 'HEAD':
        file_size = cur_path.stat().st_size

        rsp = Response()
        rsp.headers = {
            'x-ms-meta-Name': path,
            'x-ms-blob-type': 'BlockBlob',
            'x-ms-meta-DateUploaded': arrow.utcnow().isoformat(),
            'x-ms-lease-status': 'unlocked',
            'x-ms-lease-state': 'available',
            'x-ms-blob-committed-block-count': '1',
            'Accept-Ranges': 'bytes',
            'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0',
            'Content-Type': 'text/csv; charset=latin-1',
            'Content-Length': file_size
        }

        return rsp
    elif request.method == 'GET':
        rsp = Response()

        msrange = parse_range_header(request.headers.get('x-ms-range'))
        start = msrange.ranges[0][0]
        end = msrange.ranges[0][1]
        data_len = end - start + 1

        with cur_path.open('rb') as ifile:
            ifile.seek(start, os.SEEK_SET)
            cur_data = ifile.read(data_len)

            rsp.headers = {
                'x-ms-meta-Name': path,
                'x-ms-blob-type': 'BlockBlob',
                'x-ms-meta-DateUploaded': arrow.utcnow().isoformat(),
                'x-ms-lease-status': 'unlocked',
                'x-ms-lease-state': 'available',
                'x-ms-blob-committed-block-count': '1',
                'Accept-Ranges': 'bytes',
                'Server': 'Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0',
                'Content-Type': 'text/csv; charset=latin-1',
                'Content-Length': len(cur_data)
            }
            rsp.set_data(cur_data)
            rsp.add_etag()

        return rsp
    else:
        abort(400)


if __name__ == '__main__':
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(CERT_PATH, KEY_PATH)

    app.run(debug=True,
            port='443',
            ssl_context=context)
