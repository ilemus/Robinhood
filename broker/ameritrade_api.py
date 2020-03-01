from .ameritrade_url import Url
from .ApiBase import ApiBase
import time
import requests


class Ameritrade(ApiBase):
    def __init__(self, client_id="QOPIXDKLBHG6PXRAHNFCR1LC58ZMMFHX"):
        super().__init__()
        self.session.headers = {
            'Connection': 'keep-alive',
            'DNT': '1'
        }
        '''
            Ameritrade wants to open a browser window or otherwise redirect to their login page.
            How to form to internal request.
            https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https://localhost&client_id=QOPIXDKLBHG6PXRAHNFCR1LC58ZMMFHX@AMER.OAUTHAP
            _csfr=814861e3-3fea-4b18-9651-a8cfacf01240
            &s_scope=PlaceTrades+AccountAccess+MoveMoney
            &s_client-desc=cliclient
            &s_client-name=QOPIXDKLBHG6PXRAHNFCR1LC58ZMMFHX@AMER.OAUTHAP
            &fp_fp2DeviceId=8b9d59b77e16496f94bfda8be55b060a
            &fp_browser=mozilla/5.0+(windows+nt+10.0;+win64;+x64;+rv:73.0)+gecko/20100101+firefox/73.0|5.0+(Windows)|Win32
            &fp_screen=24|1536|864|824
            &fp_timezone=-6
            &fp_language=lang=en-US|syslang=|userlang=
            &fp_java=0
            &fp_cookie=1
            &fp_cfp={"navigator":{"properties":{"doNotTrack":"unspecified","maxTouchPoints":"0","oscpu":"Windows+NT+10.0;+Win64;+x64","vendor":"","vendorSub":"","productSub":"20100101","cookieEnabled":"true","buildID":"20181001000000","webdriver":"false","hardwareConcurrency":"12","appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0+(Windows)","platform":"Win32","userAgent":"Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64;+rv:73.0)+Gecko/20100101+Firefox/73.0","product":"Gecko","language":"en-US","onLine":"true"},"propertiesMD5":"551c644b8bee69e6c9c1371351fc29bb","navorderMD5":"d6e0b898d210c876d0c4e4eced591cd6","navmethods":"vibrate|javaEnabled|getGamepads|getVRDisplays|mozGetUserMedia|sendBeacon|requestMediaKeySystemAccess|registerProtocolHandler|taintEnabled","navmethMD5":"98288d814fb8f7a931b503c9a99e8d45"},"screen":{"properties":{"availWidth":"1536","availHeight":"824","width":"1536","height":"864","colorDepth":"24","pixelDepth":"24","top":"0","left":"0","availTop":"0","availLeft":"0","mozOrientation":"landscape-primary","onmozorientationchange":"NULL"},"propertiesMD5":"8ed1699940e8f38cda24729715b459cb","tamper":false},"timezone":"-6|-5","canvas":"f3b84e719180c3c5b37da8ac9a4b3e1e","java":false,"localstorage":true,"sessionstorage":true,"indexedDB":true,"plugins":{"names":"","namesMD5":"d41d8cd98f00b204e9800998ecf8427e"},"fonts":"2e8ad97446bda38227f4904a8753f7fc","mathroutines":"11013.232920103324|-1.4214488238747245","md5":"118757b6c1fd15a5648814139690299d","latency":164,"form":{"fields":"su_username|su_password|rememberuserid|authorize|reject"},"clkhz":null}
            &su_username={USERNAME}
            &su_password={PASSWORD}
            &authorize=Log+in
            &signed=24879f023abdeabba9d2c75eb8198e78a7c7b428
            
            // Second request for encryption detection
            _csfr=f0cd9a64-a61f-4934-b585-7033bb1a2416
            &fp_cfp={"navigator":{"properties":{"doNotTrack":"unspecified","maxTouchPoints":"0","oscpu":"Windows+NT+10.0;+Win64;+x64","vendor":"","vendorSub":"","productSub":"20100101","cookieEnabled":"true","buildID":"20181001000000","webdriver":"false","hardwareConcurrency":"12","appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0+(Windows)","platform":"Win32","userAgent":"Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64;+rv:73.0)+Gecko/20100101+Firefox/73.0","product":"Gecko","language":"en-US","onLine":"true"},"propertiesMD5":"551c644b8bee69e6c9c1371351fc29bb","navorderMD5":"d6e0b898d210c876d0c4e4eced591cd6","navmethods":"vibrate|javaEnabled|getGamepads|getVRDisplays|mozGetUserMedia|sendBeacon|requestMediaKeySystemAccess|registerProtocolHandler|taintEnabled","navmethMD5":"98288d814fb8f7a931b503c9a99e8d45"},"screen":{"properties":{"availWidth":"1536","availHeight":"824","width":"1536","height":"864","colorDepth":"24","pixelDepth":"24","top":"0","left":"0","availTop":"0","availLeft":"0","mozOrientation":"landscape-primary","onmozorientationchange":"NULL"},"propertiesMD5":"8ed1699940e8f38cda24729715b459cb","tamper":false},"timezone":"-6|-5","canvas":"f3b84e719180c3c5b37da8ac9a4b3e1e","java":false,"localstorage":true,"sessionstorage":true,"indexedDB":true,"plugins":{"names":"","namesMD5":"d41d8cd98f00b204e9800998ecf8427e"},"fonts":"2e8ad97446bda38227f4904a8753f7fc","mathroutines":"11013.232920103324|-1.4214488238747245","md5":"118757b6c1fd15a5648814139690299d","latency":104,"form":{"fields":"su_username|su_password|rememberuserid|authorize|reject"},"clkhz":null}
        '''
        self.client_id = client_id + "@AMER.OAUTHAP"

    def login(self, username, password):
        #https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https://localhost&client_id=QOPIXDKLBHG6PXRAHNFCR1LC58ZMMFHX@AMER.OAUTHAP
        params = {
            "response_type": "code",
            "redirect_uri": "http://localhost:80",
            "client_id": self.client_id
        }
        headers = {"Content-Type": "x-www-form-urlencoded"}
        payload = {
            "_csfr": self.device_id,
            "s_scope": "PlaceTrades+AccountAccess+MoveMoney",
            "s_client-name": self.client_id,
            "fp_fp2DeviceId": "8b9d59b77e16496f94bfda8be55b060a",
            "fp_browser": "mozilla/5.0+(windows+nt+10.0;+win64;+x64;+rv:73.0)+gecko/20100101+firefox/73.0|5.0+(Windows)|Win32",
            "fp_screen": "24|1536|864|824",
            "fp_timezone": int(-time.timezone / 60 / 60),
            "fp_language": "en-US|syslang=|userlang=",
            "fp_java": 0,
            "fp_cookie": 1,
            "fp_cfp": '{"navigator":{"properties":{"doNotTrack":"unspecified","maxTouchPoints":"0","oscpu":"Windows+NT+10.0;+Win64;+x64","vendor":"","vendorSub":"","productSub":"20100101","cookieEnabled":"true","buildID":"20181001000000","webdriver":"false","hardwareConcurrency":"12","appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0+(Windows)","platform":"Win32","userAgent":"Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64;+rv:73.0)+Gecko/20100101+Firefox/73.0","product":"Gecko","language":"en-US","onLine":"true"},"propertiesMD5":"551c644b8bee69e6c9c1371351fc29bb","navorderMD5":"d6e0b898d210c876d0c4e4eced591cd6","navmethods":"vibrate|javaEnabled|getGamepads|getVRDisplays|mozGetUserMedia|sendBeacon|requestMediaKeySystemAccess|registerProtocolHandler|taintEnabled","navmethMD5":"98288d814fb8f7a931b503c9a99e8d45"},"screen":{"properties":{"availWidth":"1536","availHeight":"824","width":"1536","height":"864","colorDepth":"24","pixelDepth":"24","top":"0","left":"0","availTop":"0","availLeft":"0","mozOrientation":"landscape-primary","onmozorientationchange":"NULL"},"propertiesMD5":"8ed1699940e8f38cda24729715b459cb","tamper":false},"timezone":"-6|-5","canvas":"f3b84e719180c3c5b37da8ac9a4b3e1e","java":false,"localstorage":true,"sessionstorage":true,"indexedDB":true,"plugins":{"names":"","namesMD5":"d41d8cd98f00b204e9800998ecf8427e"},"fonts":"2e8ad97446bda38227f4904a8753f7fc","mathroutines":"11013.232920103324|-1.4214488238747245","md5":"118757b6c1fd15a5648814139690299d","latency":164,"form":{"fields":"su_username|su_password|rememberuserid|authorize|reject"},"clkhz":null}',
            "su_username": username,
            "su_password": password,
            "authorize": "Log+in",
            "signed": "24879f023abdeabba9d2c75eb8198e78a7c7b428"
        }
        req = requests.Request('POST', Url.oauth(), params=params, headers=headers, data=payload)
        pretty_print_post(req)
        # response = requests.post(Url.oauth(), params=params, headers=headers, data=payload)
        # pretty_print_post(response)
        response = self.session.post(Url.oauth(), params=params, headers=headers, data=payload)
        pretty_print_post(response)


def pretty_print_post(req):
    req = req.prepare()
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        ))
