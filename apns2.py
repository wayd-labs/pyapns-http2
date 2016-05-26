from hyper import HTTP20Connection
from hyper.common.headers import HTTPHeaderMap
from hyper.tls import init_context
import json

class APNSError(Exception):
    pass

class APNS(object):
    def __init__(self, cert, key, dev=False, alt_port=False):
        self.server = 'api.development.push.apple.com' if dev\
            else 'api.push.apple.com'
        self.port = 2197 if alt_port else 443

        self._ssl_context = init_context(cert=(cert, key))
        self._conn = HTTP20Connection(
            host=self.server,
            port=self.port,
            force_proto='h2',
            ssl_context=self._ssl_context)

    def send(self, push_token, payload,
             id_=None, expiration=None, priority=None, topic=None):
        headers = HTTPHeaderMap()
        if id_:
            headers['apns-id'] = id_
        if expiration:
            headers['apns-expiration'] = expiration
        if priority:
            headers['apns-priority'] = priority
        if topic:
            headers['apns-topic'] = topic

        stream = self._conn.request(
            'POST',
            '/3/device/' + push_token,
            headers=headers,
            body=json.dumps(payload, cls=PayloadEncoder)
        )
        return stream

    def feedback(self, stream_id):
        resp = self._conn.get_response(stream_id)
        if resp.status != 200:
            body = json.loads(resp.read())
        else:
            body = None
        return (
            resp.status,
            resp.headers.get('apns-id', [None])[0],
            body)


class PayloadEncoder(json.JSONEncoder):
    def default(self, o):
        d = {'aps': {}}
        if o.alert is not None:
            d['aps']['alert'] = o.alert
        if o.badge is not None:
            d['aps']['badge'] = o.badge
        if o.sound  is not None:
            d['aps']['sound'] = o.sound
        if o.content_available  is not None:
            d['aps']['content_available'] = o.content_available
        if o.category is not None:
            d['aps']['category'] = o.category

        if len(d['aps']) == 0:
            raise APNSError("One of 'alert', 'badge', 'sound', " +\
                            "'content_available', 'category' should be specified")

        if o.extra is not None:
            if 'aps' in o.extra:
                raise APNSError("'aps' is not allowed in extra")
            d.update(o.extra)

        return d


class Payload(object):
    def __init__(self, alert=None, badge=None, sound=None,
                 content_available=None, category=None, extra=None):
        self.alert = alert
        self.badge = badge
        self.sound = sound
        self.content_available = content_available
        self.category = category

        self.extra = extra
