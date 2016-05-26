# pyapns-http2
Python library for new Apple Push Notification Service based on HTTP2/0


Usage
======

```
apns = APNS(dev=True, cert=cert_file, key=key_file)
stream_id = connection.send(token, message, id_=id_, topic=topic)
status, apns_id, body = connection.feedback(stream_id)
```

Throughput
===========

It sends 1500 pushes in 6.5 seconds with gevent, throughput 229.333955 pushes/sec.

You should limit concurency=50, looks like it's maximum number of APNS streams in one connection. You can use several connections though.

```
import gevent.monkey
gevent.monkey.patch_all()
import gevent
import gevent.pool

def apns2_send(token):
    message = Payload(alert=alert, sound='default', badge=0, content_available=None, extra=content)

    stream_id = connection.send(token, message, id_=None, topic='me.wayd.Prince-dev')
    status, apns_id, body = connection.feedback(stream_id)
    #print status, body, token
    if status == 200:
        return True
    else:
        if status == 410:
            ts = datetime.datetime.fromtimestamp(body['timestamp']/1000.)
        return False

n = 1500

def test_gevent():
    start = time.time()

    threads = []
    pool = gevent.pool.Pool(50)

    tokens = []
    for i in xrange(n):
        tokens.append(bool(random.getrandbits(1)) and expired_token or good_token)
    #pool.add(gevent.spawn(apns2_send, )

    pool.map(apns2_send, tokens)

    took = time.time() - start
    print 'GEVENT Send %d pushes in %s seconds, errors: %d, througput %f pushes/sec' % (n, took, n-ok_count, float(n)/float(took))
```




